import http.server
import socketserver
from log.clogger import get_central_logger

DATA = "fVENOXc0CU2gcGtUHMmjUYABYkievrMxPQM7BJNUfaJwGSpwReRfIZ95t2KoqXLAT6fbCg1K6f9f1xxOyuaVuycbgi4aqS2aeI53WqqdGfIdxewn"
PORT = 1337


def start_server(port: int = 1337, data: str = "") -> None:
    """Starts server that sends predefined AD response data to the client."""
    logger = get_central_logger()

    class CustomHandler(http.server.BaseHTTPRequestHandler):
        def __init__(
            self,
            *args,
            ip_address: str = "192.168.56.106",
            port: int = 1337,
            **kwargs,
        ):
            self.ip_address = ip_address
            self.port = port
            self.logger = get_central_logger()

            super().__init__(*args, **kwargs)

        def handle(self):
            client_ip, client_port = self.client_address
            self.logger.received_traffic(
                f"Received packet from {client_ip}:{client_port} to {self.ip_address}:{self.port}"
            )
            # Write the DATA directly to the socket
            self.request.sendall(DATA.encode("utf-8"))
            self.logger.ad_response(
                f"Active Defense Response: Sent packet from {self.ip_address}:{PORT} to {client_ip}:{client_port}"
            )
            self.logger.sent_traffic(
                f"Sent packet to {client_ip}:{client_port} from {self.ip_address}:{self.port}"
            )

            self.logger.info(f"Starting server on port: {PORT}...")

    try:
        with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
            logger.info(f"Serving on port: {PORT}. Press Ctrl+C to stop.")
            httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server.")
    except Exception as e:
        logger.error(f"Error starting server: {e}")
    return
