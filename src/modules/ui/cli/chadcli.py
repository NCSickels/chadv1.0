"""Chad Command Line Argument Handler"""

import asyncio
from modules.connections.interface import NetworkInterface
from log.clogger import get_central_logger


class ChadCLI:
    """Custom command line argument handler for the Chad application"""

    def __init__(
        self,
        adapter: str = "eth0",
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
            TESTDATA = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCS"

            class CustomHandler(http.server.SimpleHTTPRequestHandler):
                def do_GET(self):
                    self.send_response(200)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()
                    self.wfile.write(TESTDATA.encode("utf-8"))

            self.logger.info(f"Starting server on port {PORT}...")
            try:
                with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
                    self.logger.info(f"Serving on port {PORT}. Press Ctrl+C to stop.")
                    httpd.serve_forever()
            except KeyboardInterrupt:
                self.logger.info("Shutting down the HTTP server.")
            except Exception as e:
                self.logger.error(f"Error starting HTTP server: {e}")
            return
