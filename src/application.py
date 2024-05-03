import asyncio
from enum import Enum
from errors import StateError, VersionError

from proxy_network.anonymity import AccessList
from proxy_network.geolocation import get_geoip_data
from proxy_network.behavior import recv_from_client, forward_data, recv_from_server

from config import WafConfig
from time_utils import get_unix_time, get_epoch_time

from net.profile import Profile
from net.connection import Connection, AsyncStream
from net.aionetwork import create_new_task, HostAddress, REMOTE_ADDR

from events.ban import BanMap
from events.handler import ProfileHandler
from events.event import Event, CONNECTION, AUTHORIZED_REQUEST, UNAUTHORIZED_REQUEST

from internal.database import SignatureDb
from internal.tokenization import tokenize
from internal.system.transaction import Transaction
from internal.system.checks import check_transaction, validate_dirty_client, classify_by_flags
# from internal.system.types import ANONYMOUS, GEOLOCATION
from internal.system.logging import SecurityLog, AccessLog, AttackClassifier
from internal.system.actions.block import create_security_page


class _WafState(Enum):
    """
    An enum allowing state handling for Waf.
    """
    CREATED = "Created"
    DEPLOYED = "Deployed"
    WORKING = "WORKING"
    CLOSED = "Closed"


class Waf:
    """
    A class representing a Web application firewall.
    Protects a *single* entity in the network.
    """
    def __init__(self, conf: WafConfig) -> None:
        self.__config = conf
        self.__server = None
        self.__ban_map = BanMap()
        self.__profile_handler = ProfileHandler()
        self.__acl = AccessList(main_list=[],
                                api=conf.acl["api"],
                                interval=conf.acl["interval"],
                                backup=conf.acl["backup"])
        self.__address = (conf.proxy["ip"], conf.proxy["port"])
        self.__target = (conf.webserver["ip"], conf.webserver["port"])
        self.__state = _WafState.CREATED
        print(f"INFO: Waf created")

    @property
    def state(self) -> _WafState:
        return self.__state

    @property
    def config(self) -> WafConfig:
        return self.__config

    @property
    def target(self) -> tuple[str, int]:
        return self.__target

    def __set_connection_profile(self, client: Connection):
        """
        Creates a 'CONNECTION' event and profile.
        :param client:
        :return:
        """
        event = Event(kind=CONNECTION, id=tokenize(), log=None, tx=None)
        profile = Profile(
            host=client.ip,
            connection_date=get_unix_time(self.__config.timezone["time_zone"]),
            last_used_port=client.port,
            last_connection_time=get_epoch_time(),
            last_event=event,
            attempted_attacks=0,
            last_attempted_attack=""
        )
        with self.__profile_handler as ph:
            ph.insert_profile(client.hash, profile)

    async def __handle_unauthorized_client(self, client: Connection, event: Event):
        """
        Handles an event made by an unauthorized user.
        :param event:
        :return:
        """
        # Update the profile.
        with self.__profile_handler as ph:
            profile: Profile = ph.get_profile_by_hash(client.hash)
            profile_updates = {
                "last_used_port": client.port,
                "last_connection_time": get_epoch_time(),
                "last_event": event,
                "attempted_attacks": profile.attempted_attacks + 1,
                "last_attempted_attack": ",".join(event.log.classifiers)
            }
            ph.update_profile(client.hash, profile_updates)

        # TODO: Check if the client is already banned and work on ban system.

        # Build a security page.
        further_information = ""
        security_page_header = ""
        match event.log.classifiers:
            case [AttackClassifier.Sql_Injection | AttackClassifier.Unauthorized_access]:
                security_page_header = self.__config.securitypage["attack_header"]
                further_information = self.__config.securitypage["attack_additional_info"]
            case [AttackClassifier.Anonymity]:
                security_page_header = self.__config.securitypage["anonymity_header"]
                further_information = self.__config.securitypage["anonymity_additional_info"]
            case [AttackClassifier.Banned_Geolocation]:
                security_page_header = self.__config.securitypage["geo_header"]
                further_information = self.__config.securitypage["geo_additional_info"]
            case [AttackClassifier.Anonymity, AttackClassifier.Banned_Geolocation]:
                security_page_header = self.__config.securitypage["dirty_header"]
                further_information = self.__config.securitypage["dirty_additional_info"]

        # Forward it.
        security_page: bytes = create_security_page(info={
            "header": security_page_header,
            "further_information": further_information,
            "token": event.id
        })
        await forward_data(client, security_page)

        # Log the log object.
        print(event.log)

    async def __handle_authorized_client(self, client: Connection, event: Event):
        """
        Handles an authorized client.
        :param client:
        :param event:
        :return:
        """
        # Update the profile.
        with self.__profile_handler as ph:
            profile_updates = {
                "last_used_port": client.port,
                "last_connection_time": get_epoch_time(),
                "last_event": event,
            }
            ph.update_profile(client.hash, profile_updates)

        # Connect to the web server.
        stream = await AsyncStream.open_stream(*self.__target)
        web_server = Connection(stream=stream, addr=HostAddress(*self.__target))

        # Forward the clients request.
        await forward_data(web_server, event.tx.raw)
        response = await recv_from_server(web_server)
        await forward_data(client, response)

        # Log the log object.
        print(event.log)

    async def __handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """
        Handles each request by a single client.
        :param reader:
        :param writer:
        :return: None
        """
        client = Connection(stream=AsyncStream(reader, writer),
                            addr=HostAddress(*writer.get_extra_info(REMOTE_ADDR)))

        # Insert a connection profile.
        self.__set_connection_profile(client)

        access_list = self.__acl
        banned_countries = self.__config.geoip["banned_countries"]
        flags = validate_dirty_client(client.ip, access_list, banned_countries)

        if flags != 0:
            log_classifiers = classify_by_flags(flags)
            security_log = SecurityLog(
                ip=client.ip,
                port=client.port,
                creation_date=get_unix_time(self.__config.timezone["timezone"]),
                classifiers=log_classifiers,
                geolocation=get_geoip_data(client.ip)
            )
            event = Event(
                kind=UNAUTHORIZED_REQUEST,
                id=tokenize(),
                log=security_log,
                tx=None
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
                creation_date=get_unix_time(self.__config.timezone["time_zone"]),
                classifiers=check_result.classifiers,
                geolocation=get_geoip_data(client.ip)
            )
            event = Event(
                kind=UNAUTHORIZED_REQUEST,
                id=tokenize(),
                log=security_log,
                tx=tx
            )
            await self.__handle_unauthorized_client(client, event)
            return

        access_log = AccessLog(
            ip=client.ip,
            port=client.port,
            creation_date=get_unix_time(self.__config.timezone["time_zone"])
        )
        event = Event(
            kind=AUTHORIZED_REQUEST,
            id=str(tx.hash),
            log=access_log,
            tx=tx
        )
        await self.__handle_authorized_client(client, event)

    async def start_acl_loop(self):
        """
        Starts the Waf ACL loop.ssss
        :return:
        """
        await self.__acl.activity_loop()

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
            host=self.__config.proxy["ip"],
            port=self.__config.proxy["port"],
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
            self.__state = _WafState.WORKING
            print(f"INFO: Waf listening AT {self.__address}")
            await self.__server.serve_forever()

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


async def main():
    """
    Main entry point of program. the start of the Asyncio.Eventloop.
    Generated coroutines:
        WAF_WORK: Main work of the Waf instance.
        WAF_ACL_LOOP: Background task that updates the ACL (access list) once every interval.
    :return: None
    """
    try:
        SignatureDb()
    except Exception as _database_loading_err:
        print("ERROR: could not initialize database due:", _database_loading_err)

    conf = WafConfig()
    waf = Waf(conf=conf)
    await waf.deploy()

    work = [
        create_new_task(task_name="WAF_WORK", task=waf.work, args=()),
        create_new_task(task_name="WAF_ACL_LOOP", task=waf.start_acl_loop, args=())
    ]
    await asyncio.gather(*work)


if __name__ == "__main__":
    import tracemalloc

    tracemalloc.start()

    import sys

    if sys.version_info[0:2] != (3, 12):
        raise VersionError("Wrong python version. Please use +=3.12 only")

    asyncio.run(main())
