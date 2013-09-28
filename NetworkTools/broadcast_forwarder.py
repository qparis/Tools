import socket
from struct import *
import datetime
import pcapy
import sys
import binascii

listen_to = "eth1"
send_to = "br0"
source_broadcast = '192.168.1.255';
destination_broadcast = '192.168.26.255'
router_mac = '00:00:00:00:00:00'
debug = True

def main(argv):
	dev = listen_to
	cap = pcapy.open_live(dev , 65536 , 1 , 0)

	while(1) :
		(header, packet) = cap.next()
		parse_packet(packet)


def showhex(char):
    result = str(hex(ord(char)))
    result = result.replace("0x","")
    nombreZero = 2-len(result);
    i = 0;
    while(i < nombreZero):
        result = "0"+result;
        i+=1;
    return result;
    
def showIPHeader(packet):
	i = 14;    
	while(i < 34):   
		if(i%2 == 0 and i!=14):
		        print ""
		sys.stdout.write(showhex(packet[i]));
		sys.stdout.write(" ")
		i+=1
    
def showFullPacket(packet):
	i = 0;    
	while(i < len(packet)):   
		if(i%2 == 0 and i!=14):
		        print ""
		sys.stdout.write(showhex(packet[i]));
		sys.stdout.write(" ")
		i+=1
            
def changeDestination(packet):
	offset = 14;
	broadcaster = destination_broadcast.split('.');
	packetT = list(packet);

	packetT[16+offset] = chr(int(broadcaster[0]));
	packetT[17+offset] = chr(int(broadcaster[1]));
	packetT[18+offset] = chr(int(broadcaster[2]));
	packetT[19+offset] = chr(int(broadcaster[3]));
        
	new_packet = "".join(packetT)
	return new_packet

def changeMacSource(packet):
    # 80:ee:73:37:09:40
	macer = router_mac.split(':')
        
	packetT = list(packet);
    
	packetT[6] = chr(int(macer[0],16));
	packetT[7] = chr(int(macer[1],16));
	packetT[8] = chr(int(macer[2],16));
	packetT[9] = chr(int(macer[3],16));
	packetT[10] = chr(int(macer[4],16));
	packetT[11] = chr(int(macer[5],16));

	new_packet = "".join(packetT)
	return new_packet

def sumAndRemove(line1, line2):
    result = line1+line2;
    if(result > 0xffff):
        result = str(hex(result)).replace("0x","");
        carry = int(result[0],16)
        result = int(result[1]+result[2]+result[3]+result[4],16);
        result += carry;
        
    return result;
    
def calculateChecksum(packet):
    
    i = 0;
    line = [""]*10;
    while(i < 10):
        line[i] = int(showhex(packet[12+2*(i+1)])+showhex(packet[13+2*(i+1)]),16);
        i+=1;
    
    
    result = sumAndRemove(line[0],line[1]);
    result = sumAndRemove(result,line[2]);
    result = sumAndRemove(result,line[3]);
    result = sumAndRemove(result,line[4]);
    result = sumAndRemove(result,line[6]);
    result = sumAndRemove(result,line[7]);
    result = sumAndRemove(result,line[8]);
    result = sumAndRemove(result,line[9]);
 
    #checksum = hex(result);
    checksum = hex(int("0xffff",16)-result);
    return checksum;

def eraseChecksum(packet, nCheck):
    monCheck = str(nCheck).replace("0x","");
    i = 0;
    nombreZero = 4-len(monCheck);
    
    while(i < nombreZero):
        monCheck = "0"+monCheck;
        i+=1;
        
    first_part = monCheck[0]+monCheck[1];
    second_part = monCheck[2]+monCheck[3];
    
    first_part = int(first_part, 16);
    second_part = int(second_part, 16);
    
    offset = 14;
    packetT = list(packet);
    packetT[10+offset] = chr(first_part);
    packetT[11+offset] = chr(second_part);

    new_packet = "".join(packetT)
    return new_packet
    
        
def parse_packet(packet) :
    eth_length = 14
    eth_header = packet[:eth_length]
    eth = unpack('!6s6sH' , eth_header)
    eth_protocol = socket.ntohs(eth[2])

    if eth_protocol == 8 :

		ip_header = packet[eth_length:20+eth_length]
		iph = unpack('!BBHHHBBH4s4s' , ip_header)

		version_ihl = iph[0]
		version = version_ihl >> 4
		ihl = version_ihl & 0xF

		iph_length = ihl * 4

		ttl = iph[5]
		s_addr = socket.inet_ntoa(iph[8]);
		d_addr = socket.inet_ntoa(iph[9]);

		dest = str(d_addr);
        
		soc = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, 0x8100) #create the raw-socket
		soc.bind((send_to,0x08100)) # ether type for ARP
    
		
		if(dest == source_broadcast or dest == '255.255.255.255' or dest == '224.0.0.252' or dest == '224.0.0.251' or dest == '239.0.0.250'):
			new_packet = changeDestination(packet);
			new_packet = changeMacSource(packet);
			
   			checksum = calculateChecksum(new_packet);             
			new_packet = eraseChecksum(new_packet, checksum);
			if(debug == True):
				print "Packet sent"
			soc.send(new_packet);

if __name__ == "__main__":
  main(sys.argv)
