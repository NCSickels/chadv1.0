"""Chad Command Line Argument Handler"""

import asyncio
from modules.connections.interface import NetworkInterface
from log.clogger import get_central_logger


class ChadCLI:
    """Custom command line argument handler for the Chad application"""

    def __init__(self, adapter, ip_address, port):
        self.logger = get_central_logger()
        self.loop = asyncio.get_event_loop()
        self.adapter = adapter
        self.ip_address = ip_address
        self.port = port
        self.network_interface = NetworkInterface(interface="any", loop=self.loop)

    def run(self) -> None:
        self.logger.info("Starting Chad packet capture...")
        self.network_interface.start_capture()
        return
