#!/usr/bin/python3
#coding=utf-8

###
#对在审计服务器上抓取13579端口的报文进行处理，剥离报文由于使用tcp传输而增加的tcp头以及消息头
#提取插件传输的数据内容----插件实际抓取的报文，生成新的pcap文件，可以用ptest进行验证

import struct
import time, datetime
import sys
from scapy.all import *

bdata=bytearray()
status = 0
pktType = 0
pktLen = 0
ehterdata= [0x8c,0x1c,0xda,0x41,0xc8,0x0f,0x00,0x15,0x5d,0x03,0x1c,0x08,0x08,0x00]
firstpkt = 1


def parseMsg():
    global bdata, status,pwriter,pktLen,pktType,ehterdata,firstpkt
    
    #if firstpkt == 1 :
    #    bdata=bdata[23:]
    #    firstpkt = 0

    while len(bdata) >0 :
        if status == 0  and len(bdata)>=1:
            (pktType,) = struct.unpack('b',bdata[0:1])
            bdata=bdata[1:]
            status = 1
        elif status == 1 and len(bdata)>=4:
            (pktLen,)=struct.unpack('I',bdata[0:4])
            #if pktLen > 3000:
            #  print("status:%d,len:%d, pktLen:%d"%(status,len(bdata),pktLen))
            #  time.sleep(10000)
            bdata=bdata[4:]
            status = 2
        elif status == 2 and len(bdata)>=pktLen:
            if pktType == 1:
                print("write len:%d"%pktLen)
                # newPkt = IP(bdata[4:pktLen])
                # tba = bytearray(newPkt)
                # tdata=bytes(tba)
                # pwriter.write(tdata)
                # tmpdata = bytearray(ehterdata) +bdata[4:pktLen]
                # pwriter.write(bytes(tmpdata))
                pwriter.write(bytes(bdata[0:pktLen]))

            bdata=bdata[pktLen:]
            pktLen = 0
            status = 0
            pktType = 0
        else:
            print("status:%d,len:%d, pktLen:%d"%(status,len(bdata),pktLen))
            return



def parsePkt(pkt):
    global bdata
    if pkt['TCP'].dport != 13579:
        return
    if pkt.haslayer('Raw') :
        tmp = pkt['Raw'].load
        print("TCP len:%d"%len(tmp))
        if len(tmp) == 0 :
            return
    else:
        return

    bdata+= tmp
    parseMsg()



def main():
    global pwriter
    if len(sys.argv) != 3 :
       print("usage:%s in.pcap out.pcap"%sys.argv[0])
       print("in.pcap:  从审计服务13579上抓取的报文，抓取报文的时候要加上插件所在IP的过滤条件")
       print("out.pcap: 提取出来的报文")
       return

    #pkts = rdpcap(sys.argv[1])
    #if len(pkts) == 0:
    #    return
    pr = PcapReader(sys.argv[1])
    
    pwriter=PcapWriter(sys.argv[2])
    count = 1 
    while True:
        pkt = pr.read_packet();
        if pkt is None :
           break
        print('packet:%d'%count)
        #if count == 15 :
        #    return
        count = count+1
        parsePkt(pkt)


if __name__ == '__main__':
    main()
