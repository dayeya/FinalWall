from src.net.connection import Connection
from src.net.aionetwork import Safe_Recv_Result
from src.http_tools import SearchContext, search_header, contains_body_seperator


async def recv_from_server(server: Connection) -> Safe_Recv_Result:
    data = b""
    chunk = b""
    while not contains_body_seperator(data):
        chunk = await server.recv()
        if not chunk:
            break
        data += chunk

    content = b""
    content_length = int(search_header(data, SearchContext.CONTENT_LENGTH))
    while not len(content) >= content_length:
        chunk = await server.recv()
        if not chunk:
            break
        content += chunk

    response = data + content
    return response, 0


async def recv_from_client(client: Connection) -> Safe_Recv_Result:
    data = b""
    while not contains_body_seperator(data):
        chunk = await client.recv()
        if not chunk:
            break
        data += chunk
    return data, 0


async def forward_data(conn: Connection, data: bytes) -> None:
    await conn.send(data)
