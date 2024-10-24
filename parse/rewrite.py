#!/usr/bin/python3
#coding=utf-8

###
#对在审计服务器上抓取13579端口的报文进行处理，剥离报文由于使用tcp传输而增加的tcp头以及消息头
#提取插件传输的数据内容----插件实际抓取的报文，生成新的pcap文件，可以用ptest进行验证

import struct
import time, datetime
import sys
from scapy.all import *



def parsePkt(pkt, idx):
    global bdata,pwriter
    if pkt['TCP'].dport == 10001:
        pkt['TCP'].sport = 10000+idx
        pwriter.write(pkt)
    elif pkt['TCP'].sport == 10001:
        pkt['TCP'].dport = 10000+idx
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
    for i in range(100):
        print('loop:%d'%i)
        #pr = PcapReader(sys.argv[1])
        for pkt in pkts:
            parsePkt(pkt, i)


if __name__ == '__main__':
    main()
