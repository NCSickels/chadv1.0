"""Active Defense Response Handling Module"""

from config.settings import NETWORK_SETTINGS as settings
from scapy.layers.inet import IP, TCP, UDP
from scapy.packet import Packet
from scapy.sendrecv import send


class ADResponse:
    """
    Active Defense Response class for sending responses to incoming packets.

    Examples:
        response = ADResponse("192.168.1.1", 80, "tcp", "Hello, World!");
        response.send_packet()

    Args:
        dst_ip (str): The destination IP address.
        dst_port (int): The destination port number.
        protocol (str): The protocol to use for the response (TCP or UDP).
        data (str): The data to send in the response.
    """

    def __init__(
        self,
        dst_ip: str = "192.168.56.102",
        dst_port: int = settings.ad_response_port,
        protocol: str = "tcp",
        data: str = "DATA",
    ):
        self.dst_ip = dst_ip
        self.dst_port = dst_port
        self.protocol = protocol
        self.data = data

    def craft_packet(self) -> Packet:
        if self.protocol.lower() == "tcp":
            packet = IP(dst=self.dst_ip) / TCP(dport=self.dst_port) / self.data
        elif self.protocol.lower() == "udp":
            packet = IP(dst=self.dst_ip) / UDP(dport=self.dst_port) / self.data
        else:
            raise ValueError("Unsupported protocol: {}".format(self.protocol))
        return packet

    def send_packet(self) -> None:
        packet = self.craft_packet()
        send(packet)
