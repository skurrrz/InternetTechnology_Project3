import socket
import re
import math

################################## Receiver.py ######################################

# This is the receiver portion of the "Selective Repeat" algorithm
# Please look at "Customizable Variables" to adjust the program
# 
# Receiver.py will accept packets in groups of [window_size] and send back an Ack for each
#	sequence number received that it was expecting
# If not all expected sequence numbers were received, it will wait for Sender.py to send 
# 	all missing packets before shifting window and expecting a new set
# If repeat packets are sent, they will be ignored and discarded

################################# Create Socket ######################################

receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
receiver_socket.settimeout(5)
HOST ="localhost"
PORT =8000
receiver_socket.connect((HOST,PORT))

#################################### Variables ########################################

# Customizable variables
num_packets = 10				# Total number of packets to be sent
window_size = 5					# Window size, all packets must be ACKed before window shifts
message = "Ack:"				# This is the message to be sent to the Receiver

# Variables for program
max_n = math.ceil(num_packets/window_size)
disconnect_Msg = "fin"
n = 1

################################ Functions ##################################

# Create list of all packets that should be sent in this window
# Returns: List of sequence numbers of the packets
def createSequenceNumList():
	sequence_num_list = []
	for y in range (window_size*(n-1), window_size*n):
			sequence_num_list.append(y)
	return sequence_num_list
	
# Takes the data from the Sender and gets the sequence numbers
# All sequence numbers are removed from the list of expected sequence numbers    
def evaluatePacketSequence(data, sequence_num_list):
	response = ""
	for x in range (0, window_size):
		try:
			data = data.encode()
		except:
			pass
				
		if dataIsNotEmpty(data):
			packet_Num, data = getPacketNum(data)
			
		response = buildResponse(packet_Num, response)
			
	if responseIsNotEmpty(response):
		receiver_socket.send(response.encode())	
	else:
		pass
		
	print("")

# Checks if response is not empty
def responseIsNotEmpty(response):	
	if (len(response) > 0):
		return True
		
# Checks if data is not empty
def dataIsNotEmpty(data):
	if (len(data.decode()) > 0):
		return True


# Gets first packet number in sequence		
def getPacketNum(data):
	packet_Num = 0
	packet_Num, data = data.split(b'|', 1)
	packet_Num = packet_Num.decode('utf-8').strip()
	data = data.decode('utf-8').strip()
	packet_Num = packet_Num.replace(' ','')		
	packet_Num = packet_Num[6:]
	return packet_Num, data

# Builds response string of Acks to send back	
def buildResponse(packet_Num, response):
	if int(packet_Num) in sequence_num_list:
		sequence_num_list.remove(int(packet_Num))
		print("Hello:", packet_Num)
		response += message + str(packet_Num) + " | "
	return response	

# Checks if disconnect was requested
def disconnectRequested(data):
    if data.decode('utf-8') == "fin":
        return True

# Prints connection end message		
def endConnection():
	print("All packets have been sent, closing connection")		

# Checks if not all packets have been received	
def notSentAllPackets():
	if n <= max_n:
		return True

# Checks if list of sequence numbers is not empty		
def listIsNotEmpty(sequence_num_list):
	if len(sequence_num_list) > 0:
		return True

# Shifts window by n		
def shiftWindow(n):
	n = n + 1
	return n
	
################################ Beginning of Algorithm ##################################

while notSentAllPackets():
	sequence_num_list = createSequenceNumList()
	while listIsNotEmpty(sequence_num_list):	
		data = receiver_socket.recv(1000);
		if disconnectRequested(data) == True:
			break	
		evaluatePacketSequence(data, sequence_num_list)
	n = shiftWindow(n)
endConnection()
receiver_socket.close()