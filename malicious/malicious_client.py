import os
import sys
from socket import *

def sys_append_modules():
    """
    Appends all importent modules into sys_path.
    :returns: None. 
    """
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../...'))
    sys.path.append(parent_dir)

sys_append_modules()
from util_modules.network import send_recv

def connect(sock: socket, dst) -> None:
    sock.connect(dst)
    
def main() -> None:
    dst = ('localhost', 60000)
    sock = socket(AF_INET, SOCK_STREAM)
    connect(sock, dst)
    while True:
        data = str(input('Enter something: '))
        print(f'[+] Got: {send_recv(sock, data)}')
 
if __name__ == '__main__':
    main()