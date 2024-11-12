import socket
import time
from threading import Thread
from random import randbytes
import logging

logging.basicConfig(level=logging.INFO)

server = "192.168.2.147"
s_port = 4322


def handle_client(conn, addr):
    try:
        logging.info(f"Connected to: {addr}")
        conn.send(bytes.fromhex(
            '32 32 30 20 28 76 73 46 54 50 64 20 32 2e 33 2e 34 29 0d 0a'))
        data = conn.recv(1024)
        logging.info(f"Received: {data}")

        conn.send(bytes.fromhex(
            '33 33 31 20 50 6c 65 61 73 65 20 73 70 65 63 69 66 79 20 74 68 65 20 70 61 73 73 77 6f 72 64 2e 0d 0a'))
        data = conn.recv(1024)
        logging.info(f"Received: {data}")

        fuzzing_response = randbytes(24)
        logging.info(f"Fuzzing Response: {fuzzing_response}")

        conn.send(bytes.fromhex('353330204c6f67696e20696e636f72726563742e0d0a'))
    except Exception as e:
        logging.error(f"Error handling client {addr}: {e}")
    finally:
        conn.close()


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcpsocket:
        try:
            tcpsocket.bind((server, s_port))
            tcpsocket.listen(2)
            logging.info("Server started, waiting for connections...")

            while True:
                conn, addr = tcpsocket.accept()
                start = time.time()
                logging.info(f"Time taken: {time.time() - start} seconds")
                Thread(target=handle_client, args=(conn, addr)).start()
        except socket.error as e:
            logging.error(f"Socket error: {e}")
        except Exception as e:
            logging.error(f"Server error: {e}")


if __name__ == "__main__":
    start_server()
