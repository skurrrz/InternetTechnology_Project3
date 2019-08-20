import socket
import re


################################## Receiver.py ######################################

# This is the Receiver portion of the "Stop-and-Wait" algorithm
# Sender will send one packet at a time, which is a message + sequence number
# Receiver will receive the packet, print it, and send back a packet = Ack + received sequence number
# After Sender has finished sending all packets, it will send "disconnect"
# When Receiver receives a "disconnect" it will close communication

################################# Create Socket ######################################

receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
receiver_socket.settimeout(5)
HOST ="localhost"
PORT =8000
receiver_socket.connect((HOST,PORT))

#################################### Variables ########################################

# Customizable variables
message = "Ack:"					# This is the message to be sent to the Receiver

# Variables for program
sequence_Num = 0
ack_Num = 0

################################ Functions ##################################

def disconnectedRequested(data):
	if data.decode() == "fin":
		return True

def sendAck(data):
	print (data.decode())
	data = data.decode('utf-8')
	data = data.strip()	
	packet_Num = data[6:]
	response = message + str(packet_Num) + " "
	receiver_socket.send(response.encode())	
	
def closeConnection():
	print("All packets sent, closing connection.")
	receiver_socket.close()
	
################################ Beginning of Program ##################################

while True:
	# Waits to receive data from Sender.py
	data = receiver_socket.recv(1000);
	
	# If 'fin' was sent, end program
	if disconnectedRequested(data) == True:
		break
	
	# Receive and print data, send back appropriate Ack
	else:
		sendAck(data)
	
#Close connection if "fin" has been received	
closeConnection()
