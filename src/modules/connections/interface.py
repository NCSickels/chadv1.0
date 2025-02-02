"""
Hook module for connecting to a live network interface using PyShark.
"""

import pyshark
from log.clogger import Logger


class NetworkInterface:
    def __init__(self, interface: str, display_filter: str = None):
        """
        Initialize the NetworkInterface with the specified network interface and display filter.

        :param interface: The name of the network interface to capture packets from.
        :param display_filter: Optional display filter to apply to the captured packets.
        :param capture: The capture object for the network interface.
        """
        self._interface = interface
        self._display_filter = display_filter
        self._status = "Disconnected"
        self._connected_ip = None
        self._connected_port = 22  # Default port for SSH
        self.capture = pyshark.LiveCapture(
            interface=self._interface, display_filter=self._display_filter
        )
        self.logger = Logger()

    @property
    def interface(self) -> str:
        """
        Get the name of the network interface.

        :return: The name of the network interface.
        """
        return self._interface

    @interface.setter
    def interface(self, value: str):
        """
        Set the name of the network interface.

        :param value: The name of the network interface.
        """
        self._interface = value

    @property
    def ip(self) -> str:
        """
        Get the IP address of the network interface.

        :return: The IP address of the network interface.
        """
        return self._connected_ip

    @ip.setter
    def ip(self, value: str):
        """
        Set the IP address of the network interface.

        :param value: The IP address of the network interface.
        """
        self._connected_ip = value

    @property
    def port(self) -> int:
        """
        Get the port number of the network interface.

        :return: The port number of the network interface.
        """
        return self._connected_port

    @port.setter
    def port(self, value: int):
        """
        Set the port number of the network interface.

        :param value: The port number of the network interface.
        """
        self._connected_port = value

    @property
    def status(self) -> str:
        """
        Get the status of the network interface.

        :return: The status of the network interface.
        """
        return self._status

    @status.setter
    def status(self, value: str):
        """
        Set the status of the network interface.

        :param value: The status of the network interface.
        """
        self._status = value

    def start_capture(self, ip: str, port: int):
        """
        Start capturing packets on the specified network interface.

        :param ip: The IP address to filter packets by.
        :param port: The port number to filter packets by.
        """
        try:
            self._connected_ip = ip
            self._connected_port = port
            self._status = "Connected"
            self.capture.sniff_continuously(packet_count=0)
            self.logger.info(f"Started capturing on interface: {self.interface}")
        except Exception as e:
            self.logger.error(f"Error starting capture: {e}")
            self._status = "Disconnected"

    def list_interfaces(self):
        """
        List all available network interfaces.

        :return: A list of available network interfaces.
        """
        try:
            capture = pyshark.LiveCapture()
            interfaces = capture.interfaces
            for interface in interfaces:
                print(interface)
            # return self.capture.interfaces
        except Exception as e:
            self.logger.error(f"Error listing interfaces: {e}")
            return []

    def stop_capture(self):
        """
        Stop capturing packets.
        """
        try:
            if self.capture:
                self.capture.close()
                self._status = "Disconnected"
                self.logger.info(f"Stopped capturing on interface: {self.interface}")
        except Exception as e:
            self.logger.error(f"Error stopping capture: {e}")
            self._status = "Connected"

    def process_packets(self, packet_handler):
        """
        Process packets using the provided packet handler function.

        :param packet_handler: A function that takes a packet as an argument and processes it.
        """
        if not self.capture:
            raise RuntimeError(
                "Capture has not been started. Call start_capture() first."
            )

        try:
            for packet in self.capture.sniff_continuously():
                packet_handler(packet)
        except KeyboardInterrupt:
            print("Packet capture interrupted by user.")
        finally:
            self.stop_capture()

    def get_status_info(self):
        """
        Get the status of the network interface.

        :return: A dictionary containing the status, connected IP, port, and interface.
        """
        return {
            "status": self._status,
            "connected_ip": self._connected_ip,
            "connected_port": self._connected_port,
            "interface": self._interface,
        }
