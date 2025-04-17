"""Chad Command Line Argument Handler"""

import asyncio
from modules.connections.interface import NetworkInterface
from log.clogger import get_central_logger


class ChadCLI:
    """Custom command line argument handler for the Chad application"""

    def __init__(
        self,
        adapter: str = "enp0s8",
        ip_address: str = "192.168.56.102",
        port: int = 1337,
        server: bool = True,
    ) -> None:
        self.logger = get_central_logger()
        self.loop = asyncio.get_event_loop()
        self.adapter = adapter
        self.ip_address = ip_address
        self.port = port
        self.server = server

    def run(self) -> None:
        self.logger.info("Starting Chad packet capture...")
        if not self.server:
            self.network_interface = NetworkInterface(
                interface=self.adapter, loop=self.loop
            )
            self.network_interface.start_capture()
        else:
            import http.server
            import socketserver

            PORT = 1337
            DATA = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCS"

            class CustomHandler(http.server.BaseHTTPRequestHandler):
                def handle(self):
                    self.logger = get_central_logger()
                    # Write the TESTDATA directly to the socket
                    self.request.sendall(DATA.encode("utf-8"))
                    self.logger.ad_response(
                        f"Active defense response sent through port {PORT}"
                    )

            self.logger.info(f"Starting server on port {PORT}...")
            try:
                with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
                    self.logger.info(f"Serving on port {PORT}. Press Ctrl+C to stop.")
                    httpd.serve_forever()
            except KeyboardInterrupt:
                self.logger.info("Shutting down server.")
            except Exception as e:
                self.logger.error(f"Error starting server: {e}")
            return
