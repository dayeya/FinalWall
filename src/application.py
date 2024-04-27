import asyncio
from enum import Enum
from src.exceptions import StateError, VersionError

from src.proxy_network.acl import AccessList
from src.proxy_network.behavior import recv_from_client, forward_data, recv_from_server

from config import WafConfig
from date import get_unix_time

from net.connection import Connection, AsyncStream
from net.aionetwork import create_new_task, HostAddress, REMOTE_ADDR

from internal.tokenization import tokenize
from internal.system.checker import check_transaction
from internal.system.actions.block import build_block, build_redirect, contains_block
from internal.system.transaction import Transaction, CLIENT_REQUEST
from internal.database import SignatureDb


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
    def __init__(self) -> None:
        self.__config = WafConfig()
        self.__acl = AccessList(
            main_list=[],
            api=self.__config.acl["api"],
            interval=self.__config.acl["interval"],
            backup=self.__config.acl["backup"]
        )
        self.__server = None
        self.__state = _WafState.CREATED
        self.__address = (self.__config.proxy["ip"], self.__config.proxy["port"])
        self.__target = (self.__config.webserver["ip"], self.__config.webserver["port"])
        print(f"INFO: Waf created")

    @property
    def state(self) -> _WafState:
        return self.__state

    @property
    def config(self) -> WafConfig:
        return self.__config

    @property
    def target(self):
        return self.__target

    async def __handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """
        Handles each request by a single client.
        :param reader:
        :param writer:
        :return: None
        """
        stream = await AsyncStream.open_stream(*self.__target)
        web_server = Connection(
            stream=stream,
            addr=HostAddress(*self.__target)
        )
        client = Connection(
            stream=AsyncStream(reader, writer),
            addr=HostAddress(*writer.get_extra_info(REMOTE_ADDR))
        )
        request = await recv_from_client(client)
        if not request:
            print(f"ERROR: could not recv from {client}")

        tx = Transaction(
            owner=client.addr,
            real_host_address=None,
            has_proxies=False,
            raw=request,
            side=CLIENT_REQUEST,
            creation_date=get_unix_time(self.__config.timezone["time_zone"])
        )

        tx.process()
        check_result = await check_transaction(tx)

        if check_result.unwrap():
            location = ("/block?token=" + tokenize()).encode("utf-8")
            redirection = build_redirect(location)
            await forward_data(client, redirection)
            print(check_result.unwrap_log())
            return

        token = contains_block(tx)
        if token:
            block_html: bytes = build_block(token)
            await forward_data(client, block_html)
            return

        print(check_result.unwrap_log())
        await forward_data(web_server, request)
        response = await recv_from_server(web_server)
        if not response:
            print(f"ERROR: could not recv from server")
        await forward_data(client, response)

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

    waf = Waf()
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
