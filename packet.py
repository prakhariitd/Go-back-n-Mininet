# packet.py - Packet-related functions

# Creates a packet from a sequence number and byte data
# def make(seq_num, data = b''):
#     seq_bytes = seq_num.to_bytes(4, byteorder = 'little', signed = True)
#     return seq_bytes + data

# # Creates an empty packet
# def make_empty():
#     return b''

# # Extracts sequence number and data from a non-empty packet
# def extract(packet):
#     seq_num = int.from_bytes(packet[0:4], byteorder = 'little', signed = True)
#     return seq_num, packet[4:]
import random

def make(seq_num, errp, data = b''):
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