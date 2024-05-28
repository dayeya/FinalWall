import pickle
import asyncio
from enum import Enum

import websockets.exceptions
from websockets.server import serve, WebSocketServerProtocol

from engine.errors import StateError
from engine.config import WafConfig

from engine.time_utils import get_unix_time, get_epoch_time

from engine.proxy_network.anonymity import AccessList
from engine.proxy_network.geolocation import get_geoip_data, get_external_ip
from engine.proxy_network.behavior import recv_from_client, forward_data, recv_from_server

from engine.tunnel import Tunnel, TunnelEvent
from engine.net.connection import Connection, AsyncStream
from engine.net.aionetwork import create_new_task, HostAddress, REMOTE_ADDR

from engine.internal.events import Classifier
from engine.internal.events import SecurityLog, AccessLog
from engine.internal.events import Event, CONNECTION, AUTHORIZED_REQUEST, UNAUTHORIZED_REQUEST

from engine.internal.tokenization import tokenize
from engine.internal.signature_db import SignatureDb

from engine.internal.core.profile import Profile
from engine.internal.core.transaction import Transaction
from engine.internal.core.managers.ban_manager import BanManager
from engine.internal.core.managers.event_manager import EventManager
from engine.internal.core.managers.profile_manager import ProfileManager
from engine.internal.core.blocking.block import create_security_page
from engine.internal.core.vuln_checks import check_transaction, validate_dirty_client, classify_by_flags


class _WafState(Enum):
    """An enum allowing state handling for Waf."""
    CREATED = "Created"
    DEPLOYED = "Deployed"
    WORKING = "WORKING"
    CLOSED = "Closed"


class Waf:
    """
    A class representing a Web application firewall.
    Protects a *single* entity in the network.
    """
    def __init__(
            self,
            conf: WafConfig,
            ucid: int,
            local: bool=False,
            with_tunneling: bool=True,
            init_api: bool=True
    ) -> None:
        try:
            SignatureDb()
        except Exception as _database_loading_err:
            print("ERROR: could not initialize database due:", _database_loading_err)

        self.__ucid = ucid
        self.__config = conf
        self.__server = None
        self.__local = local
        self.__init_api = init_api
        self.__vulnerability_scores: dict[str, int] = {
            Classifier.SqlInjection: 0,
            Classifier.XSS: 0,
            Classifier.RFI: 0,
            Classifier.LFI: 0,
            Classifier.UnauthorizedAccess: 0,
            Classifier.BannedAccess: 0,
            Classifier.BannedGeolocation: 0,
            Classifier.Anonymity: 0
        }
        self.__with_tunneling = with_tunneling
        self.__tunnel = Tunnel(conf.admin["backend_api"])
        self.__ban_manager = BanManager()
        self.__event_manager = EventManager()
        self.__profile_manager = ProfileManager()
        self.__acl = AccessList(main_list=[],
                                api=conf.acl["api"],
                                interval=conf.acl["interval"],
                                backup=conf.acl["backup"])
        self.__api_address = (conf.waf["api_ip"], conf.waf["api_port"]) if init_api else None
        self.__address = (conf.waf["ip"], conf.waf["port"])
        self.__target = (conf.webserver["ip"], conf.webserver["port"])
        self.__state = _WafState.CREATED
        print(f"INFO: Waf created")

    @property
    def ucid(self) -> int:
        return self.__ucid

    @property
    def api(self) -> bool:
        return self.__init_api

    @property
    def local(self) -> bool:
        return self.__local

    @property
    def state(self) -> _WafState:
        return self.__state

    @property
    def config(self) -> WafConfig:
        return self.__config

    @property
    def target(self) -> tuple[str, int]:
        return self.__target

    @property
    def address(self) -> tuple[str, int]:
        return self.__address

    async def __start_api(self):
        """Starts the websocket API for the backend API."""
        async def __api_handler(websocket: WebSocketServerProtocol):
            """Handler for the catching events from the backend API used by the user."""
            data = -1
            try:
                async for event in websocket:
                    print(websocket.messages)
                    async with asyncio.Lock():
                        if event == TunnelEvent.TunnelConnection:
                            continue
                        if event == TunnelEvent.AccessLogUpdate:
                            data = self.get_authorized_events()
                        if event == TunnelEvent.SecurityLogUpdate:
                            data = self.get_security_events()
                        if event == TunnelEvent.vulnerabilityScoresUpdate:
                            data = self.get_vulnerability_scores()
                        # Forward the data to the API.
                        await websocket.send(pickle.dumps(data))
            except websockets.exceptions.ConnectionClosed:
                """Can either be raised from poor connectivity or large amounts of traffic."""
                return

        async with serve(__api_handler, *self.__api_address):
            print(f"WAF API started... Listening on: {self.__api_address}")
            await asyncio.get_event_loop().create_future()

    def __update_vulnerability_scores(self, classifier: Classifier):
        """Updates the number of times that an event was classified as an attack."""
        self.__vulnerability_scores[classifier] += 1

    def __set_connection_profile(self, client: Connection):
        """
        Creates a new profile with a last_event of connection (only if the client is not in the db).
        :param client:
        :return:
        """
        event = Event(kind=CONNECTION, id=tokenize(), log=None, request=None, response=None)
        profile = Profile(
            host=client.ip,
            connection_date=get_unix_time(self.__config.timezone["time_zone"]),
            last_used_port=client.port,
            last_connection_time=get_epoch_time(),
            last_event=event,
            attempted_attacks=0,
            last_attempted_attack=""
        )
        with self.__profile_manager as pm:
            pm.insert_profile(client.hash, profile)

    async def __handle_authorized_client(self, client: Connection, event: Event):
        """
        Handles an authorized client.
        :param client:
        :param event:
        :return:
        """
        # Update the profile.
        with self.__profile_manager as pm:
            profile_updates = {
                "last_used_port": client.port,
                "last_connection_time": event.log.sys_epoch_time,
                "last_event": event
            }
            pm.update_profile(client.hash, profile_updates)

        # Connect to the web server.
        stream = await AsyncStream.open_stream(*self.__target)
        web_server = Connection(stream=stream, addr=HostAddress(*self.__target))

        # Forward the clients request.
        await forward_data(web_server, event.request.raw)
        response = await recv_from_server(web_server)
        await forward_data(client, response)

        self.__event_manager.cache_event(event)

        # Log the log object.
        if self.__with_tunneling and self.__tunnel.connected:
            self.__tunnel.register_event(TunnelEvent.AccessLogUpdate)

    async def __handle_unauthorized_client(self, client: Connection, event: Event):
        """
        Handles an event made by an unauthorized user.
        :param event:
        :return:
        """
        # Update the profile.
        with self.__profile_manager as pm:
            profile: Profile = pm.get_profile_by_hash(client.hash)
            profile_updates = {
                "last_used_port": client.port,
                "last_connection_time": get_epoch_time(),
                "last_event": event,
                "attempted_attacks": profile.attempted_attacks + 1,
                "last_attempted_attack": ",".join(event.log.classifiers)
            }
            pm.update_profile(client.hash, profile_updates)

        # If this __handle is called, then client is not banned.
        # Ban the client and set correct duration.
        profile = self.__profile_manager.get_profile_by_hash(client.hash)

        if profile.attempted_attacks > self.__config.banning["threshold"]:  # exceeded the threshold.
            banned_at = get_epoch_time()
            ban_duration = profile.attempted_attacks * self.__config.banning["factor"]
            self.__ban_manager.insert_mapping(client.hash, banned_at, float(ban_duration))

        # Build a security page.
        further_information = ""
        security_page_header = ""
        match event.log.classifiers:
            case [Classifier.SqlInjection | Classifier.XSS | Classifier.UnauthorizedAccess | Classifier.BannedAccess]:
                security_page_header = self.__config.securitypage["attack_header"]
                further_information = self.__config.securitypage["attack_additional_info"]
            case [Classifier.Anonymity]:
                security_page_header = self.__config.securitypage["anonymity_header"]
                further_information = self.__config.securitypage["anonymity_additional_info"]
            case [Classifier.BannedGeolocation]:
                security_page_header = self.__config.securitypage["geo_header"]
                further_information = self.__config.securitypage["geo_additional_info"]
            case [Classifier.Anonymity, Classifier.BannedGeolocation]:
                security_page_header = self.__config.securitypage["dirty_header"]
                further_information = self.__config.securitypage["dirty_additional_info"]

        # Cache up some forensics.
        self.__event_manager.cache_event(event)
        self.__update_vulnerability_scores(event.log.classifiers[0])

        security_page: bytes = create_security_page(info={
            "header": security_page_header,
            "further_information": further_information,
            "token": event.id
        })
        await forward_data(client, security_page)

        # Inform the backend API with an event.
        if self.__with_tunneling and self.__tunnel.connected:
            self.__tunnel.register_event(TunnelEvent.SecurityLogUpdate)

    async def __handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """
        Handles each request by a single client.
        :param reader:
        :param writer:
        :return: None
        """
        # Change the IP of the connection to the external ip of the Waf instance.
        # This change happens only when the Waf instance is configured to be a local cluster.
        ip, port = writer.get_extra_info(REMOTE_ADDR)
        if self.__local:
            ip = get_external_ip()

        client = Connection(stream=AsyncStream(reader, writer), addr=HostAddress(ip, port))
        self.__set_connection_profile(client)

        if self.__ban_manager.banned(client.hash):
            security_log = SecurityLog(
                ip=client.ip,
                port=client.port,
                download=True,
                sys_epoch_time=get_epoch_time(),
                creation_date=get_unix_time(self.__config.timezone["time_zone"]),
                classifiers=[Classifier.BannedAccess],
                geolocation=get_geoip_data(client.ip)
            )
            event = Event(
                kind=UNAUTHORIZED_REQUEST,
                id=tokenize(),
                log=security_log,
                request=None,
                response=None,
            )
            await self.__handle_unauthorized_client(client, event)
            return

        access_list = self.__acl
        banned_countries = self.__config.geoip["banned_countries"]

        flags = validate_dirty_client(client.ip, access_list, banned_countries)

        if flags != 0:
            log_classifiers = classify_by_flags(flags)
            security_log = SecurityLog(
                ip=client.ip,
                port=client.port,
                download=True,
                sys_epoch_time=get_epoch_time(),
                creation_date=get_unix_time(self.__config.timezone["time_zone"]),
                classifiers=log_classifiers,
                geolocation=get_geoip_data(client.ip)
            )
            event = Event(
                kind=UNAUTHORIZED_REQUEST,
                id=tokenize(),
                log=security_log,
                request=None,
                response=None,
            )
            await self.__handle_unauthorized_client(client, event)
            return

        request = await recv_from_client(client, execption_callback=client.close)
        tx: Transaction = Transaction(
            owner=client.addr,
            real_host_address=None,
            raw=request,
            creation_date=get_unix_time(self.__config.timezone["time_zone"])
        )
        tx.process()

        access_list = self.__acl
        banned_countries = self.__config.geoip["banned_countries"]

        check_result = await check_transaction(tx, access_list, banned_countries)

        if check_result.result:
            security_log = SecurityLog(
                ip=client.ip,
                port=client.port,
                download=True,
                sys_epoch_time=get_epoch_time(),
                creation_date=get_unix_time(self.__config.timezone["time_zone"]),
                classifiers=check_result.classifiers,
                geolocation=get_geoip_data(client.ip)
            )
            event = Event(
                kind=UNAUTHORIZED_REQUEST,
                id=tokenize(),
                log=security_log,
                request=tx,
                response=None,
            )
            await self.__handle_unauthorized_client(client, event)
            return

        access_log = AccessLog(
            ip=client.ip,
            port=client.port,
            download=True,
            geolocation=get_geoip_data(client.ip),
            sys_epoch_time=get_epoch_time(),
            creation_date=get_unix_time(self.__config.timezone["time_zone"])
        )
        event = Event(
            kind=AUTHORIZED_REQUEST,
            id=str(tx.hash),
            log=access_log,
            request=tx,
            response=None
        )
        await self.__handle_authorized_client(client, event)

    def get_authorized_events(self) -> list:
        """Retrieves all the authorized events until this point in time."""
        return self.__event_manager.get_access_events()

    def get_security_events(self) -> list:
        """Retrieves all the unauthorized events until this point in time."""
        return self.__event_manager.get_security_events()

    def get_vulnerability_scores(self):
        """Returns a dictionary that maps a vulnerability with its detection score."""
        return self.__vulnerability_scores

    async def start_acl_loop(self):
        """
        Starts the Waf ACL loop.ssss
        :return:
        """
        await self.__acl.activity_loop()

    async def start_api(self):
        """Starts the inner API for user initiated events."""
        if not self.__init_api:
            return
        await self.__start_api()

    async def deploy(self) -> None:
        """
        Creates an Asyncio.Server with corresponding configurations.
        Note:
            Waf.deploy() *DOES NOT* run the server.
        :return: None
        """
        if self.__state is _WafState.DEPLOYED:
            raise StateError("Instance already deployed")
        if self.__state is _WafState.WORKING:
            raise StateError("Instance is working, try Waf.close() then Waf.deploy()")
        if self.__state is _WafState.CLOSED:
            raise StateError("Instance is closed, try Waf.restart()")

        # Deploy instance, state is _Waf.CREATED
        self.__server: asyncio.Server = await asyncio.start_server(
            client_connected_cb=self.__handle_connection,
            host=self.__config.waf["ip"],
            port=self.__config.waf["port"],
            start_serving=False
        )
        self.__state = _WafState.DEPLOYED
        print(f"INFO: Waf deployed AT: {self.__address!s}, FOR: {self.__target!s}")

    async def work(self):
        """
        Starts the main working task of the Waf - making it available to handle connections.
        Note:
            Waf serves forever and will stop when the coroutine is cancelled.
        :return: None
        """
        if self.__state is _WafState.CREATED:
            raise StateError("Instance is created, try Waf.deploy() before running")
        if self.__state is _WafState.WORKING:
            raise StateError("Instance is working")
        if self.__state is _WafState.CLOSED:
            raise StateError("Instance is closed, try Waf.restart()")

        # Run instance, state is _WafState.DEPLOYED.
        async with self.__server:
            work = [create_new_task(task_name="WAF_WORKER", task=self.__server.serve_forever, args=())]
            if self.__with_tunneling:
                work += [create_new_task(task_name="WAF_TUNNEL_CONNECT", task=self.__tunnel.connect, args=())]

            # Start serving.
            print(f"INFO: Waf listening AT {self.__address}")
            self.__state = _WafState.WORKING
            await asyncio.gather(*work)

    async def restart(self):
        """
        Restarts the Waf.
        :return: None
        """
        if self.__state is not _WafState.CLOSED:
            raise StateError("Instance is not closed")
        await self.deploy()
        await self.work()

    async def close(self):
        """
        Closes the Waf.
        :return: None
        """
        if self.__state is _WafState.CLOSED:
            return
        self.__server.close()
        await self.__server.wait_closed()
        self.__state = _WafState.CLOSED
        print("INFO: Waf closed")
