import unittest
from blanket_src.packet_tools import path_segment

class TestPathSegment(unittest.TestCase):  
    
    # [Test functions]
    
    def test_invalid_method(self) -> None:
        payload = """
                    INVALIDMETHOD /path HTTP/1.1\r\n
                    Host: 127.0.0.1:8080\r\n\r\n
                  """
        self.assertIsNone(path_segment(payload))

    def test_no_path(self) -> None:
        payload = """
                    GET HTTP/1.1\r\n
                    Host: 127.0.0.1:8080\r\n\r\n
                  """
        self.assertIsNone(path_segment(payload))

    def test_missing_newline(self) -> None:
        payload = """
                    GET /path HTTP/1.1\r\n
                    Host: 127.0.0.1:8080\r\n
                  """
        self.assertIsNone(path_segment(payload))

    def test_malformed_request_line(self) -> None:
        payload = """
                    InvalidRequestLine\r\n
                    Host: 127.0.0.1:8080\r\n\r\n
                """
        self.assertIsNone(path_segment(payload))
        
    def test_url_encoded_path(self) -> None:
        payload = """
                    POST /encoded%2Fpath HTTP/1.1\r\n
                    Host: 127.0.0.1:8080\r\n\r\n
                  """
        self.assertEqual(path_segment(payload), ('POST', '/encoded%2Fpath'))
        
    def test_empty_request(self) -> None:
        payload = """
                    GET / HTTP/1.1\r\n
                    Host: 127.0.0.1:8080\r\n
                    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0\r\n
                    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8\r\n
                    Accept-Language: en-US,en;q=0.5\r\n
                    Accept-Encoding: gzip, deflate, br\r\n
                    Content-Type: application/x-www-form-urlencoded\r\n
                    Content-Length: 60\r\n
                    Origin: http://127.0.0.1:8080\r\n
                    Connection: keep-alive\r\n
                    Referer: http://127.0.0.1:8080/login\r\n\r\n\r\n
                  """
        self.assertEqual(path_segment(payload), ('GET', '/'))
        
    def test_dir_request(self) -> None:
        payload = """
                    GET /foo HTTP/1.1\r\n
                    Host: 127.0.0.1:8080\r\n
                    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0\r\n
                    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8\r\n
                    Accept-Language: en-US,en;q=0.5\r\n
                    Accept-Encoding: gzip, deflate, br\r\n
                    Content-Type: application/x-www-form-urlencoded\r\n
                    Content-Length: 60\r\n
                    Origin: http://127.0.0.1:8080\r\n
                    Connection: keep-alive\r\n
                    Referer: http://127.0.0.1:8080/login\r\n\r\n\r\n
                  """
        self.assertEqual(path_segment(payload), ('GET', '/foo'))  
          
    def test_mul_dir_request(self) -> None:
        payload = """
                    POST /Blanket/foo/bar HTTP/1.1\r\n
                    Host: 127.0.0.1:8080\r\n
                    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0\r\n
                    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8\r\n
                    Accept-Language: en-US,en;q=0.5\r\n
                    Accept-Encoding: gzip, deflate, br\r\n
                    Content-Type: application/x-www-form-urlencoded\r\n
                    Content-Length: 60\r\n
                    Origin: http://127.0.0.1:8080\r\n
                    Connection: keep-alive\r\n
                    Referer: http://127.0.0.1:8080/login\r\n\r\n\r\n
                  """
        self.assertEqual(path_segment(payload), ('POST', '/Blanket/foo/bar'))    
    
if __name__ == '__main__':
    unittest.main()