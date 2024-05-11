from typing import Callable

from engine.net.connection import Connection
from engine.http_process import SearchContext, search_header, contains_body_seperator

__doc__ = """behavior.py defines functions with similar functionality that of a proxy."""


async def recv_from_server(server: Connection) -> bytes:
    """
    Receiving data from the server.
    :param server:
    :return: bytes
    """
    http_data: bytes = await server.recv_until(
        condition=contains_body_seperator,
        args=()
    )
    content_length = int(search_header(http_data, SearchContext.CONTENT_LENGTH))
    content: bytes = await server.recv_until(
        condition=lambda _content, _content_length: len(content) >= _content_length,
        args=(content_length,)
    )
    return http_data + content


async def recv_from_client(client: Connection, execption_callback: Callable) -> bytes:
    """
    Receiving data from the client, if an error occurs callback will be called.
    :param execption_callback:
    :param client:
    :return: bytes
    """
    try:
        data: bytes = await client.recv_until(
            condition=contains_body_seperator,
            args=()
        )
        return data
    except:
        print(f"An exception occurred. Performing callback: {execption_callback.__name__}")
        execption_callback()


async def forward_data(conn: Connection, data: bytes) -> None:
    """
    Forward data to the connection.
    :param conn:
    :param data:
    :return:
    """
    await conn.write(data)
