import pickle
from socket import *
from threading import Thread


class WAF_Proxy:

    addr: (str, int)


    def init(self, ip, port) -> None:
        """
        Creating a WAF_Proxy object.
        Args:
            ip (str): IP of the proxy
            port (int): PORT of the proxy
        """
        self.addr = (ip, port)
        self.main_sock = socket(AF_INET, SOCK_STREAM)

    def direct_site(self, site_url) -> None:

        """
        Will direct in the registry all the packets going to SITE into the Proxy.
        :param site:
        :return:
        """

        pass

    def boot_proxy(self) -> None:
        """
        Boots the proxy, allowing it to start operating.
        """
        self.main_sock.bind(self.addr)
        self.main_sock.listen(5)

        UP = True

        while UP:

            user_sock, addr = self.main_sock.accept()
            user_handler = Thread(target=self.handle_user, args=(user_sock, addr))

            # start current users analysis.
            user_handler.start()