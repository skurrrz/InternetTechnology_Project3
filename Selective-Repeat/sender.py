import socket
import sys
import re
import random
import select
import math

################################## Sender.py ######################################

# This is the sender portion of the "Selective Repeat" algorithm
# Please look at "Customizable Variables" to adjust the program
# 
# Sender.py will send packets in groups of [window_size] and wait for Receiver.py to
# 	send an Ack for each sent packet. Packet loss is simulated during the message building
#	segment of Sender.py. 
# If Sender.py does not receive all expected Acks, it will resend whichever packets that 
#	did not get Acked. 
# Sender.py has a timeout feature: If it does not receive any Acks, it will attempt to resend
#	whichever packets from the current set that still need Acks

################################# Creates Socket ######################################

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.settimeout(5)
HOST = "localhost"
PORT = 8000
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client_socket.bind((HOST, PORT))
client_socket.listen(5)
conn, address = client_socket.accept()

#################################### Variables ########################################

# Customizable variables
packet_loss_chance = 30			# Set to 0 for 0% chance of packet loss
num_packets = 10				# Total number of packets to be sent
window_size = 5					# Window size, all packets must be ACKed before window shifts
message = "Hello:"				# This is the message to be sent to the Receiver

# Variables for program
max_n = math.ceil(num_packets/window_size)
n = 1

################################ Functions ##################################

# Create list of all sequence numbers sent in this window (expected Ack values)
# Returns: List of expected Ack numbers of the packets
def createAckList():
	ack_num_list = []
	for y in range (window_size*(n-1), window_size*n):
			ack_num_list.append(y)	
	return ack_num_list

#Simulates sending packets in window, with a [packet_loss_chance]% of losing a packet
def sendPacketsInList(ack_num_list):
	data = ""
	for x in ack_num_list:
		random_int =  random.randint(1,100)		
		
		# Packet is "lost"
		if (random_int < packet_loss_chance):
			pass
		
		# Packet is not "lost"
		elif (random_int >= packet_loss_chance):
			data += message + str(x) + " | "
			
	print("")
	#print("sending:", data)
	conn.send(data.encode())

# Takes the response from the Receiver and gets the Ack values sent back
# All returned Ack values are removed from ack_num_list
def evaluateResponse(response, ack_num_list):
	for x in range(0, window_size):		
		try:
			response = response.encode()
		except:
			pass
				
		# Get the first Ack number in the sent sequence
		if (len(response) > 0 and len(response) > 0 ):	
			ack_Num, response = getAckNum(response)
		
		# Sequence is empty, all non-lost packets have been received
		else:
			break
		
		# If received Ack was in the list, print and remove from list
		if isInList(ack_Num, ack_num_list):
			ack_num_list = removeFromList(ack_Num, ack_num_list)
	return ack_num_list
	
def getAckNum(response):
	ack_Num, response = response.split(b'|', 1)
	ack_Num = ack_Num.decode('utf-8').strip()
	response = response.decode('utf-8').strip()
	ack_Num = ack_Num.replace(' ','')		
	ack_Num = ack_Num[4:]
	return ack_Num, response
	
	
def isInList(ack_Num, ack_num_list):
	if int(ack_Num) in ack_num_list:	
		return True
	
def removeFromList(ack_Num, ack_num_list):
	ack_num_list.remove(int(ack_Num))
	print("Ack:", ack_Num)
	return ack_num_list
	
# Checks if there are still packets that need to be sent	
def notSentAllPackets():
	if n <= max_n:
		return True
		
# Checks if ack_num_list is empty
def listIsNotEmpty(ack_num_list):
	if len(ack_num_list) > 0:
		return True

# Shifts the window by n
def shiftWindow(n):
	n = n + 1
	return n
	
# Receiver has signaled to disconnect	
def disconnectRequested(response):
    if response.decode('utf-8') == "fin":
        return True	
	
# send disconnect message to Receiver, then close connection 	
def endConnection():
	print("All packets have been sent, closing connection")	
	disconnect_Msg = "fin"
	conn.send(disconnect_Msg.encode())
	
	
################################ Beginning of Algorithm ##################################
# Keeps a list of N packets; Sends all remaining packets; wait for Acks; 
# remove any received Acks from list; repeat until list is empty; shift window

while notSentAllPackets():
	ack_num_list = createAckList()		
	while listIsNotEmpty(ack_num_list):
		try:
			if len(ack_num_list) > 0:
				sendPacketsInList(ack_num_list)				
			elif len(ack_num_list) == 0:
				break
				
			conn.settimeout(1)
			response = conn.recv(1000);

			if disconnectRequested(response) == True:
				break	
				
			ack_num_list = evaluateResponse(response, ack_num_list)
			
		except socket.timeout:
			continue
			
	n = shiftWindow(n)
endConnection()				
client_socket.close()