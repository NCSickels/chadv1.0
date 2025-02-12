"""Active Defense Response Handling Module"""

from scapy.all import IP, TCP, UDP, send


class ADResponse:
    """
    Active Defense Response class for sending responses to incoming packets.

    :param dst_ip: The destination IP address.
    :param dst_port: The destination port number.
    :param protocol: The protocol to use for the response (TCP or UDP).
    :param data: The data to send in the response.
    """

    def __init__(self, dst_ip, dst_port, protocol, data):
        self.dst_ip = dst_ip
        self.dst_port = dst_port
        self.protocol = protocol
        self.data = data

    def craft_packet(self):
        if self.protocol.lower() == "tcp":
            packet = IP(dst=self.dst_ip) / TCP(dport=self.dst_port) / self.data
        elif self.protocol.lower() == "udp":
            packet = IP(dst=self.dst_ip) / UDP(dport=self.dst_port) / self.data
        else:
            raise ValueError("Unsupported protocol: {}".format(self.protocol))
        return packet

    def send_packet(self):
        packet = self.craft_packet()
        send(packet)


# Example usage:
response = ADResponse("192.168.1.1", 80, "tcp", "Hello, World!")
response.send_packet()
