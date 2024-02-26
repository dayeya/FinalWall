import os
import sys
import unittest

module = os.path.abspath(os.path.join(os.path.dirname(__file__),  "../..."))
sys.path.append(module)

from blanket_src.internal.analyze.access import deny_access 


class TestDenyAcess(unittest.TestCase):
    def test_admin_acess(self) -> None:
        payload = """GET /admin HTTP/1.1\r\nHost: 127.0.0.1:8080\r\n\r\n"""
        self.assertTrue(deny_access(payload))

if __name__ == "__main__":
    unittest.main()
    