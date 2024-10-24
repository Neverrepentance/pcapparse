#!/usr/bin/python3
#coding=utf-8

###

import struct
import time, datetime
import sys
from scapy.all import *



def parsePkt(pkt):
    global bdata,pwriter
    if pkt['TCP'].dport == 22:
        pkt['TCP'].sport = 3306
        pwriter.write(pkt)
    elif pkt['TCP'].sport == 22:
        pkt['TCP'].dport = 3306
        pwriter.write(pkt)
    pwriter.flush()

def main():
    global pwriter
    if len(sys.argv) != 3 :
       print("usage:%s in.pcap out.pcap"%sys.argv[0])
       print("in.pcap:  需要复制的抓包文件")
       print("out.pcap: 改写的抓包文件")
       return

    pkts = rdpcap(sys.argv[1])
    if len(pkts) == 0:
        return
    
    pwriter=PcapWriter(sys.argv[2])
    count = 1 
    for pkt in pkts:
        parsePkt(pkt)


if __name__ == '__main__':
    main()
