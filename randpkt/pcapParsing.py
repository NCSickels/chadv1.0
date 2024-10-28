from scapy.all import *
from timeit import default_timer as timer
start = timer()
send(IP(dst='192.168.2.180')/TCP(dport=53, flags='S'))
end = timer()
print(end - start)
