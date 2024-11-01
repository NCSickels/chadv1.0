#!/usr/bin/env python3

import scapy.all as scapy
from subprocess import Popen, PIPE
import ssl
import socket
import random
import time
import argparse
import os
import sys

VERBOSE = False
PCAP_LOCATION = './test.pcap'
radamsa_bin = '/usr/bin/radamsa'
clients_list = []
servers_list = []
packets_list = []

HOST = '127.0.0.1'
PORT = 443
FUZZ_FACTOR = 50.0


def mutate(payload):
    try:
        radamsa = [radamsa_bin, '-n', '1', '-']
        p = Popen(radamsa, stdin=PIPE, stdout=PIPE)
        mutated_data = p.communicate(input=payload.encode())[0].decode()
    except Exception as e:
        print(f"Could not execute 'radamsa': {e}")
        sys.exit(1)

    return mutated_data


def log_events(log_info, type_event):
    log_msg = f"[{time.ctime()}] {log_info}\n"

    if type_event == "fuzzing":
        try:
            with open('fuzz.log', 'a') as fd:
                fd.write(log_msg)
        except IOError as err:
            return f"[!] Error opening log file: {err}"

    elif type_event == "error":
        try:
            with open('error.log', 'a') as fd:
                fd.write(log_msg)
        except IOError as err:
            return f"[!] Error opening error file: {err}"

    else:
        return f"[!] '{type_event}' is an unrecognized log event type."

    return ""


def main():
    global PCAP_LOCATION, HOST, PORT, FUZZ_FACTOR

    parser = argparse.ArgumentParser(
        description="A very simple mash-up of Scapy + radamsa to extract data from pcap and perform fuzzing ad infinitum.")
    parser.add_argument(
        "-H", "--host", help="Destination IP - Default: 127.0.0.1")
    parser.add_argument("-p", "--port", help="Destination Port - Default: 443")
    parser.add_argument("-f", "--file", help="Input File Location")
    parser.add_argument("-z", "--fuzz", help="Fuzz Factor - Default: 50.0")
    parser.add_argument("-v", "--version", action="version",
                        version=f"{parser.prog} 1.0")

    args = parser.parse_args()

    if args.host:
        HOST = args.host
    if args.port:
        PORT = int(args.port)
    if args.fuzz:
        FUZZ_FACTOR = float(args.fuzz)
    if args.file:
        PCAP_LOCATION = args.file
    if not os.path.exists(PCAP_LOCATION):
        print(f"{PCAP_LOCATION} file not found. Please check")
        exit(1)

    pktcounter = 0
    packets = scapy.rdpcap(PCAP_LOCATION)
    random.seed(time.time())

    print(f"This pcap contains a total of {len(packets)} packets. Parsing...")

    '''
    Extract the payload of all client->server packets, put them in an
    ordered list for subsequent fuzzing.
    '''
    for pkt in packets:
        '''
        So we can tell since the very begining who is the client and the
        server. We assume the client initiates the connection with a packet
         with SYN as the only flag activated.
        '''
        if pktcounter == 0:
            if pkt.sprintf("%TCP.flags%") == 'S':
                clients_list.append(pkt.src)
                servers_list.append(pkt.dst)

        if VERBOSE:
            print(f"Parsing packet #{pktcounter}")
            print(pkt.summary())
        pktcounter += 1

        try:
            if pkt.raw:
                '''
                We make sure we only fuzz data traveling from the client to
                the server, in this case is the only thing we're interested
                as we're fuzzing the back-end application
                '''
                if pkt.src in clients_list:
                    print(
                        f"Packet #{pktcounter} has some client->server raw data. Go fuzz!")
                    packet_payload = pkt.raw
                    packets_list.append((pktcounter, str(packet_payload)))
        except IndexError:
            continue

    # Infinite loop of mutating packets and them down the wire
    fuzz_iterations = 0

    while True:
        iterations_str = f"[+] Fuzzing iteration number #{fuzz_iterations}"
        print(iterations_str)

        try:
            fuzz_iterations += 1
            sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sockfd.settimeout(5)
            ssl_sockfd = ssl.wrap_socket(sockfd)
            ssl_sockfd.connect((HOST, PORT))

            for packet in packets_list:
                payload = packet[1]
                if random.random() < FUZZ_FACTOR / 100:
                    payload = mutate(payload)
                    iterations_str += f"\n--- Payload ---\n{payload}\n"
                    print(payload)

                ssl_sockfd.send(payload)
                received_buffer = ssl_sockfd.recv(1024).decode()
                iterations_str += "\n--- Received ---\n" + \
                    f"{received_buffer}\n"
                print(received_buffer)

                log_events(iterations_str + '\n', "fuzzing")

                print("")

        except Exception as err:
            error_str = f"[!] Error during iteration #{
                fuzz_iterations}: {str(err)}"
            print(error_str)
            log_str = error_str + '\n' + iterations_str
            log_events(log_str, "error")


if __name__ == "__main__":
    main()
