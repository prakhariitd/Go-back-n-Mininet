import sys
import random
import socket
import _thread
import time
from timer import Timer

raddr = ('localhost', 8080)
saddr = ('localhost', 0)
sleep = 0.05
tout = 0.5
send_timer = Timer(tout)
win_size = 7
next_frame_to_send = 0
base = 0
mutex = _thread.allocate_lock()
errp = 10 #error prob of data packet
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

# Send thread
def send(sock, filename):
	global mutex
	global base
	global send_timer

    # Open the file
	try:
		file = open(filename, 'rb')
	except IOError:
		print('File Not Found')
		return
    
    # Add all the packets to the buffer
	pbuffer = []
	seq_num = 0

	while True:
		pkt_size = random.randint(512,1024)
		data = file.read(pkt_size)
		if not data: break
		pbuffer.append(make(seq_num, data))
		seq_num += 1

	num_pkts = len(pbuffer)
	win_size = 7
	win_size = min(win_size, num_pkts-base)
	next_frame_to_send = 0
	base = 0

    # Start the receiver thread
	_thread.start_new_thread(receive, (sock,))

	while (base < num_pkts):
		mutex.acquire()
        # Send all the pbuffer in the window
		while (next_frame_to_send < base + win_size):
			if (random.randint(1, drop) > 1):
				sock.sendto(pbuffer[next_frame_to_send],raddr)
			next_frame_to_send += 1

        # Start the timer
		if (not send_timer.running()):
			send_timer.start()

        # Wait until a timer goes off or we get an ACK
		while (send_timer.running() and not send_timer.timeout()):
			mutex.release()
			time.sleep(sleep)
			mutex.acquire()

		if (send_timer.timeout()): #Timeout
			send_timer.stop();
			next_frame_to_send = base
		else:
			win_size = min(win_size, num_pkts-base)
		mutex.release()

    # Send empty packet as end of file
	sock.sendto(make_empty(),raddr)
	file.close()
    
# Receive thread
def receive(sock):
    global mutex
    global base
    global send_timer

    while True:
        pkt, _ = sock.recvfrom(1024);
        ack, error, _ = extract(pkt);

        # If we get an ACK for the first packet
        if (error == 0):
	        if (ack >= base):
	            mutex.acquire()
	            base = ack + 1
	            send_timer.stop()
	            mutex.release()
	        else:
	        	mutex.acquire()
	        	send_timer.stop();
	        	next_frame_to_send = base
	        	mutex.release()

if __name__ == '__main__':
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind(saddr)
	filename = sys.argv[1]
	send(sock,filename)
	sock.close()