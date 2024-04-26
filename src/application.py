import asyncio
from enum import Enum
from src.exceptions import StateError, VersionError

from src.proxy_network.acl import AccessList
from src.proxy_network.behaviour import recv_from_client, forward_data, recv_from_server

from config import Config
from date import get_unix_time

from net.connection import Connection, AsyncStream
from net.aionetwork import create_new_task, HostAddress, REMOTE_ADDR

from internal.tokenization import tokenize
from internal.database import SignaturesDB
from internal.system.checker import Checker
from internal.system.actions.block import build_block, build_redirect
from internal.system.transaction import Transaction, CLIENT_REQUEST


class _WafState(Enum):
    CREATED = "Created"
    DEPLOYED = "Deployed"
    WORKING = "WORKING"
    CLOSED = "Closed"


class Waf:
    def __init__(self) -> None:
        self.config = Config()
        self.__checker = Checker()
        self.__state = _WafState.CREATED
        self.__address = (
            self.config.proxy["ip"],
            self.config.proxy["port"]
        )
        self.__server = None
        print(f"INFO: Waf created")

    @property
    def state(self):
        return self.__state

    async def __handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        ip = self.config.webserver["ip"]
        port = self.config.webserver["port"]
        web_server = Connection(
            stream=await AsyncStream.open_stream(ip, port),
            addr=HostAddress(ip, port)
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
            creation_date=get_unix_time(self.config.timezone["time_zone"])
        )
        tx.process()

        valid_transaction, log_object = await self.__checker.check_transaction(tx)
        if valid_transaction:
            location = ("/block?token=" + tokenize()).encode("utf-8")
            redirection = build_redirect(location)
            await forward_data(client, redirection)
            print(log_object)

        elif token := self.__checker.contains_block(tx):
            block_html: bytes = build_block(token)
            await forward_data(client, block_html)

        else:
            print(log_object)
            await forward_data(web_server, request)
            response = await recv_from_server(web_server)
            if not response:
                print(f"ERROR: could not recv from server")
            await forward_data(client, response)

    async def deploy(self):
        if self.__state is _WafState.DEPLOYED:
            raise StateError("Instance already deployed")
        if self.__state is _WafState.WORKING:
            raise StateError("Instance is working, try Waf.close() then Waf.deploy()")
        if self.__state is _WafState.CLOSED:
            raise StateError("Instance is closed, try Waf.restart()")

        # Deploy instance, state is _Waf.CREATED
        self.__server: asyncio.Server = await asyncio.start_server(
            client_connected_cb=self.__handle_connection,
            host=self.config.proxy["ip"],
            port=self.config.proxy["port"],
            start_serving=False
        )
        self.__state = _WafState.DEPLOYED
        print(f"INFO: Waf deployed at {self.__address}")

    async def work(self):
        if self.__state is _WafState.CREATED:
            raise StateError("Instance is created, try Waf.deploy() before running")
        if self.__state is _WafState.WORKING:
            raise StateError("Instance is working")
        if self.__state is _WafState.CLOSED:
            raise StateError("Instance is closed, try Waf.restart()")

        # Run instance, state is _WafState.DEPLOYED.
        async with self.__server:
            self.__state = _WafState.WORKING
            print(f"INFO: Waf listening at {self.__address}")
            await self.__server.serve_forever()

    async def restart(self):
        if self.__state is not _WafState.CLOSED:
            raise StateError("Instance is not closed")
        await self.deploy()
        await self.work()

    async def close(self):
        if self.__state is _WafState.CLOSED:
            return
        self.__server.close()
        await self.__server.wait_closed()
        self.__state = _WafState.CLOSED
        print("INFO: Waf closed")


async def main():
    try:
        SignaturesDB()
    except Exception as _database_loading_err:
        print("ERROR: Could not initialize database due:", _database_loading_err)

    waf = Waf()
    await waf.deploy()

    AccessList.api = waf.config.acl["api"]
    AccessList.interval = waf.config.acl["refetch_interval"]
    work = [
        create_new_task(task_name="WAF_WORK", task=waf.work, args=()),
        create_new_task(task_name="ACL_ACTIVITY_LOOP", task=AccessList.activity_loop, args=())
    ]
    await asyncio.gather(*work)

if __name__ == "__main__":
    import tracemalloc
    tracemalloc.start()

    import sys
    if sys.version_info[0:2] != (3, 12):
        raise VersionError("Wrong python version. Please use +=3.12 only")

    asyncio.run(main())
