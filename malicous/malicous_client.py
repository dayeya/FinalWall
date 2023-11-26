from socket import *
from util_modules import send_recv

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