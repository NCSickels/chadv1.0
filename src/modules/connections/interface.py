"""
Hook module for connecting to a live network interface using PyShark.
"""

import asyncio

import pyshark

from log.clogger import get_central_logger
from modules.helpers.helpers import check_sudo
from modules.connections.adresponse import ADResponse


class NetworkInterface:
    def __init__(
        self,
        interface: str = "any",
        display_filter: str = None,
        bpf_filter: str = "",
        loop=None,
    ):
        """
        Initialize the NetworkInterface with the specified network interface and display filter.

        :param interface: The name of the network interface to capture packets from.
        :param display_filter: Optional display filter to apply to the captured packets.
        :param capture: The capture object for the network interface.
        """
        self._interface = interface
        self._display_filter = display_filter
        self._bpf_filter = bpf_filter
        self._status = "Disconnected"
        self._connected_ip = "None"
        self._connected_port = 22
        self.capture = None
        self.logger = get_central_logger()
        self.loop = loop or asyncio.get_event_loop()
        self.capture_started_event = asyncio.Event()

    # --------------------------------------------------------------- #

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

    # --------------------------------------------------------------- #

    # TODO: Fix this to work with asyncio properly; capture packets repeats when trying to stop capture
    async def capture_packets(self):
        self.capture = pyshark.LiveCapture(
            interface="any",
            eventloop=self.loop,
        )
        self.logger.info(f"Starting packet capture on interface: {self._interface}")
        self.capture_started_event.set()
        try:
            for packet in self.capture.sniff_continuously(packet_count=10):
                self.handle_packet(packet)
            # await self.capture.apply_on_packets(self.handle_packet)
        except asyncio.CancelledError:
            self.logger.info("Packet capture task cancelled.")
        except EOFError:
            self.logger.info("Packet capture task ended.")
        except Exception as e:
            self.logger.error(f"Unexpected error during packet capture: {e}")
        finally:
            # await self.stop_capture()
            self.capture.close()

    def start_capture(self):
        """Start capturing packets on the network interface."""
        if not check_sudo():
            self.logger.error("This module requires root privileges to run.")
            return
        try:
            if not self.loop.is_running():
                self.loop.run_until_complete(self.capture_packets())
            else:
                self.loop.create_task(self.capture_packets())
                self.loop.run_until_complete(self.capture_started_event.wait())
        except Exception as e:
            self.logger.error(f"Error starting capture: {e}")

    async def stop_capture(self):
        """Stop capturing packets on the network interface."""
        if self.capture:
            asyncio.sleep(3)
            # await self.capture.close_async()
            self.capture.close()
            self.logger.info("Packet capture stopped.")

    def handle_packet(self, packet):
        # If IP packet, print source and destination IP addresses
        if "IP" in packet:
            self.logger.info(
                f"Source IP: {packet.ip.src}, Destination IP: {packet.ip.dst}"
            )
        print(packet)

    # --------------------------------------------------------------- #

    def send_packet(self, data):
        """
        Send a packet to the network interface.

        :param data: The data to send.
        """
        response = ADResponse(self._connected_ip, self._connected_port, "tcp", data)
        response.send_packet()

    # --------------------------------------------------------------- #

    def list_interfaces(self):
        """
        List all available network interfaces.

        :return: A list of available network interfaces.
        """
        return pyshark.tshark.tshark.get_tshark_interfaces()

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
