import os
import sys
from benchmark_dec import benchmark_time

parent = "./.."
module = os.path.abspath(os.path.join(os.path.dirname(__file__), parent))
sys.path.append(module)

# Import all functions to benchmark.
from blanket_src.http_tools import *

@benchmark_time("Path Segment", 1_000)
def bench_path_segment() -> None:
    _ = path_segment("GET /images/layout/logo.png HTTP/1.0\r\nUser-Agent: Wget/1.12 (linux-gnu)\r\nAccept: */*\r\nHost: packetlife.net\r\nConnection: Keep-Alive\r\n\r\n")

@benchmark_time("Content-Length", 1_000)
def bench_get_content_length() -> None:
    _ = get_content_length(b"HTTP/1.1 200 OK\r\nServer: nginx/0.8.53\r\nDate: Tue, 01 Mar 2011 20:45:16 GMT\r\nContent-Type: image/png\r\nContent-Length: 21684\r\nLast-Modified: Fri, 21 Jan 2011 03:41:14 GMT\r\nConnection: keep-alive\r\nKeep-Alive: timeout=20\r\nExpires: Wed, 29 Feb 2012 20:45:16 GMT\r\nCache-Control: max-age=31536000\r\nCache-Control: public\r\nVary: Accept-Encoding\r\nAccept-Ranges: bytes\r\n\r\n")
 
if __name__ == '__main__':
    bench_path_segment()
    bench_get_content_length()