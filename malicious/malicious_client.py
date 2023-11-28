import os
import sys
from socket import *

def sys_append_modules() -> None:
    """
    Appends all importent modules into sys_path.
    :returns: None. 
    """
    parent = '../...'
    module = os.path.abspath(os.path.join(os.path.dirname(__file__), parent))
    sys.path.append(module)

sys_append_modules()
from common.network import safe_send_recv

def connect(sock: socket, dst) -> None:
    sock.connect(dst)
    
def main() -> None:
    dst = ('localhost', 60000)
    sock = socket(AF_INET, SOCK_STREAM)
    connect(sock, dst)
    while True:
        data = str(input('Enter something: '))
        print(f'[+] Got: {safe_send_recv(sock, data)}')
 
if __name__ == '__main__':
    main()