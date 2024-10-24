#!/usr/bin/python3
#coding=utf-8


import struct
import time, datetime
import sys
# from scapy.all import *
import scapy.all as scapy


def parsePkt(pkt):
    global pwriter
    if pkt['TCP'].dport == 1433:
        for i in range(100):
            pkt['TCP'].sport = 20000+i
            pwriter.write(pkt)
    elif pkt['TCP'].sport == 1433:
        for i in range(100):
            pkt['TCP'].dport = 20000+i
            pwriter.write(pkt)
    pwriter.flush()

def main():
    global pwriter
    if len(sys.argv) != 3 :
       print("usage:%s in.pcap out.pcap"%sys.argv[0])
       print("in.pcap:  需要复制的抓包文件")
       print("out.pcap: 改写的抓包文件")
       return
    
    pwriter=scapy.PcapWriter(sys.argv[2])
    pr = scapy.PcapReader(sys.argv[1])
    count = 1
    while True:
        try:
            pkt = pr.read_packet();
            if pkt is None :
                break
            print('packet:%d'%count)
            parsePkt(pkt)
            count = count+1
            # if count > 2 :
            #    break
        except Exception as err:
            print(err)
            break
    pr.close()
    pwriter.close()

if __name__ == '__main__':
    main()
