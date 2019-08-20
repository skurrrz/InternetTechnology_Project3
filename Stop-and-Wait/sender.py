import socket
import sys
import random 

################################## Sender.py ######################################

# This is the Sender portion of the "Stop-and-Wait" algorithm
# Sender will send one packet at a time, which is a message + sequence number
# Receiver will receive the packet, print it, and send back a packet = Ack + sequence number
# Sender will then print this Ack and send next packet
# After Sender has finished sending all packets, it will send "disconnect" and close

################################# Creates Socket ######################################

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.settimeout(10)
HOST = "localhost"
PORT = 8000
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client_socket.bind((HOST, PORT))
client_socket.listen(5)
conn, address = client_socket.accept()

#################################### Variables ########################################

# Customizable variables
packet_loss_chance = 0          # Set to 0 for 0% chance of packet loss
num_packets = 10                # Total number of packets to be sent
message = "Hello:"              # This is the message to be sent to the Receiver

# Variables for program
sequence_Num = 0
disconnect_Msg = "fin"
ack_Num = 0

################################ Functions ##################################

# Sends next packet in sequence to receiver
def sendPacket():
    random_int =  random.randint(1,100)
        
    # [packet_loss_chance]% chance of sending packet
    if (random_int >= packet_loss_chance):
        data = message + str(sequence_Num)
        conn.send(data.encode())
        #print("Data sent: ", data)
        
# Check if response was received from Receiver
def checkForResponse(response):
    if not response:
        return False

# Checks if received Ack was correct for the last sent packet       
def isAckCorrect(response, sequence_Num):
    ack_Num = response.decode('utf-8')
    ack_Num = ack_Num.strip()   
    ack_Num = response[4:].strip()
    if (int(ack_Num) == sequence_Num):
        print (response.decode())
        return True
    
# Sends disconnect message and ends connection  
def closeConnection():
    print("All packets sent, closing connection.")
    conn.send(disconnect_Msg.encode())
    client_socket.close()

# Checks if not all packets have been sent
def notAllPacketsSent(sequence_Num,num_packets):
    if sequence_Num < num_packets:
        return True
        
################################ Beginning of Program ##################################

while notAllPacketsSent(sequence_Num,num_packets):
    try:
        sendPacket()
        response = conn.recv(500);
        if checkForResponse(response) == False:
            break   
        elif isAckCorrect(response,sequence_Num) == True:
            sequence_Num += 1
    except socket.timeout:
        continue
closeConnection()