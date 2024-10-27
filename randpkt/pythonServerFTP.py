# import socket
from scapy.all import *
import time
import sys
from threading import Thread

server = "192.168.2.147"
sport = 4322

tcpsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    tcpsocket.bind((server, sport))
except socket.error as e:
    str(e)
start = 0
while True:
    tcpsocket.listen(2)
    print("Waiting for a connection, Server Started")
    (conn, (ip,port)) = tcpsocket.accept()
    print( 'time taken ', time.time()-start, 'seconds')
    conn.send(bytes.fromhex('32 32 30 20 28 76 73 46 54 50 64 20 32 2e 33 2e 34 29 0d 0a'))
    print("Connected to:", ip)
    data = conn.recv(1024)
    print(data)
    #time.sleep(0.01)
    conn.send(bytes.fromhex('33 33 31 20 50 6c 65 61 73 65 20 73 70 65 63 69 66 79 20 74 68 65 20 70 61 73 73 77 6f 72 64 2e 0d 0a'))
    data = conn.recv(1024)
    print(data)
    #conn.send(bytes.fromhex('35 33 30 20 4c 6f 67 69 6e 20 69 6e 63 6f 72 72 65 63 74 2e 0d 0a'))
    start = time.time()
    send(IP(dst=ip)/fuzz(TCP(dport=port)))
