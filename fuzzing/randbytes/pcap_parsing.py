from scapy.all import IP, TCP, send
from timeit import default_timer as timer


def send_packet(destination_ip, destination_port):
    start_time = timer()
    try:
        send(IP(dst=destination_ip)/TCP(dport=destination_port, flags='S'))
    except Exception as e:
        print(f"An error occurred: {e}")
    end_time = timer()
    print(f"Time taken to send packet: {end_time - start_time} seconds")


if __name__ == "__main__":
    destination_ip = '192.168.2.180'
    destination_port = 53
    send_packet(destination_ip, destination_port)
