import asyncio
from net.connection import Connection
from net.aionetwork import safe_send, Address, Safe_Send_Result, Safe_Recv_Result
from http_tools import SearchContext, search_header, contains_body_seperator

class Proxy:
    async def send_to_conn(self, conn: Connection, data: bytes) -> None:
        await conn.send(data)
            
    async def recv_from_server(self, server: Connection) -> Safe_Recv_Result:
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
    
    async def recv_from_client(self, client: Connection) -> Safe_Recv_Result:
        data = b""
        while not contains_body_seperator(data):
            chunk = await client.recv()
            if not chunk: 
                break
            data += chunk
        return data, 0