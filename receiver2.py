import socket
import sys
import random

raddr = ('localhost', 8080)
saddr = ('localhost', 0)
errp = 20 #err prob of ack packet
drop = 20 #drop probability due to network issues

# Creates a packet from a sequence number and byte data
def make(seq_num, data = b''):
    seq_bytes = seq_num.to_bytes(4, byteorder = 'little', signed = True)
    if random.randint(1, errp) > 1:
        err_bytes = (0).to_bytes(4, byteorder = 'little', signed = True)
    else:
        err_bytes = (1).to_bytes(4, byteorder = 'little', signed = True)
    return seq_bytes + err_bytes + data

# Creates an empty packet
def make_empty():
    return b''

# Extracts sequence number and data from a non-empty packet
def extract(packet):
    seq_num = int.from_bytes(packet[0:4], byteorder = 'little', signed = True)
    err = int.from_bytes(packet[4:8], byteorder = 'little', signed = True)
    return seq_num, err, packet[8:]

# Receive packets from the sender
def receive(sock, filename):
    # Open the file for writing
    try:
        file = open(filename, 'wb')
    except IOError:
        print('File Not Found')
        return
    
    expected_pkt = 0
    while True:
        # Get the next packet from the sender
        pkt, _ = sock.recvfrom(1024)
        if not pkt:
            break
        seq_num, error, data = extract(pkt)
        
        # Send back an ACK
        if (error==0):
            if seq_num == expected_pkt:
                pkt = make(expected_pkt)
                if random.randint(1, drop) > 1:
                    sock.sendto(pkt, saddr)
                expected_pkt += 1
                file.write(data)
            else:
                pkt = make(expected_pkt - 1)
                sock.sendto(pkt, saddr)
        else:
            pkt = make(expected_pkt - 1)
            sock.sendto(pkt, saddr)

    file.close()

# Main function
if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(raddr) 

    filename = sys.argv[1]
    receive(sock, filename)
    sock.close()
