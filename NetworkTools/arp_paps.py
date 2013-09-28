import socket
from struct import *
import datetime
import pcapy
import sys
import binascii
import struct

# ARP PAPS

# Cet outil permet de rediriger les paquets de certaines plages d'IP vers une machine d'un réseau local en l'absence de configuration de routes statiques sur pas mal de routeurs (style box)

# Mode d'emploi : 
# - Régler le DHCP du routeur avec un masque de sous réseau assez grand (qui contient les plages à rediriger) (Dans l'exemple, 255.255.0.0 conviendra bien)
# - Configurer les plages d'IP à rediriger (qui doivent être des sous plages )
# - Faire tourner ce script sur la machine vers qui envoyer les paquets.

# Ce script n'est pas une méthode propre pour faire ce genre de manipulation, à ne pas utiliser en production. C'est juste fait pour des utilisations perso

listen_to = "eth0"

networks = [
    ["192.168.26.0", "255.255.255.0"],
    ["192.168.200.0", "255.255.255.0"],
    ["192.168.100.0", "255.255.255.0"],
    ["192.168.102.0", "255.255.255.0"],
    ["192.168.5.0", "255.255.255.0"]
]

def main(argv):
	dev = listen_to
	cap = pcapy.open_live(dev , 65536 , 1 , 0)

	while(1) :
		(header, packet) = cap.next()
		parse_packet(packet)

def ipStringToBin(ip):
    return pack('!4B', *[int(x) for x in ip.split('.')])

def ipStr(ip):
    return str(ord(ip[0]))+"."+str(ord(ip[1]))+"."+str(ord(ip[2]))+"."+str(ord(ip[3]))

def in_networks(ip):
    for network in networks:
        networkBin = ipStringToBin(network[0])
        maskBin = ipStringToBin(network[1])
        
        # Ouai bon ok, on a vu mieux ...
        if (
         int(bin(ord(networkBin[0])),2) & int(bin(ord(maskBin[0])),2) == int(bin(ord(ip[0])),2) & int(bin(ord(maskBin[0])),2) and 
         int(bin(ord(networkBin[1])),2) & int(bin(ord(maskBin[1])),2) == int(bin(ord(ip[1])),2) & int(bin(ord(maskBin[1])),2) and 
         int(bin(ord(networkBin[2])),2) & int(bin(ord(maskBin[2])),2) == int(bin(ord(ip[2])),2) & int(bin(ord(maskBin[2])),2) and 
         int(bin(ord(networkBin[3])),2) & int(bin(ord(maskBin[3])),2) == int(bin(ord(ip[3])),2) & int(bin(ord(maskBin[3])),2)
        ):
            return True

    return False
    
def send_arp(ip, device):
    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.SOCK_RAW)
    sock.bind((device, socket.SOCK_RAW))


    mac = sock.getsockname()[4]
    arpop = pack('!H', 0x0002)

    arpframe = [
        ### ETHERNET
        pack('!6B', *(0xFF,)*6),
        mac,
        pack('!H', 0x0806),

        ### ARP
        pack('!HHBB', 0x0001, 0x0800, 0x0006, 0x0004),
        arpop,
        mac,
        ip,
        mac,
        ip
        ]

    sock.send(''.join(arpframe))

    return True


def parse_packet(packet) :
    eth_length = 14
    eth_header = packet[:eth_length]
    eth = unpack('!6s6sH' , eth_header)
    eth_protocol = socket.ntohs(eth[2])


    if(eth_protocol == 1544):
        if(packet[20] == "\x00" and packet[21] == "\x01"): # Who-Has packet
            ip = packet[38:42]
            if(in_networks(ip)):
                print ipStr(ip)+" is in networks. Sending ARP packet."
                send_arp(ip, listen_to)
            else:
                print ipStr(ip)+" is not in networks. Ignoring ARP packet."
            

if __name__ == "__main__":
  main(sys.argv)