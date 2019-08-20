import socket
import sys
import random
import math

################################## Sender.py ######################################

# This is the sender portion of the "Go-Back-N" algorithm
#
# Sender will send 5 packets at a time, but they might get lost before they get to Receiver
# Packet loss is simulated with "packet_loss_chance" (default is 30%), there is a 30% chance
# that the packet N will not make it to receiver
# Receiver will send back Acks in sequential order; if it receives a packet out of order it will
# continue to send an Ack for the last received packet until the Sender sends the correct packet

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
packet_loss_chance = 30         # Set to 0 for 0% chance of packet loss
num_packets = 10                # Total number of packets to be sent
window_size = 5                 # Window size, all packets must be ACKed before window shifts
message = "Hello:"              # This is the message to be sent to the Receiver

# Variables for program
max_n = math.ceil(num_packets/window_size)
n = 1
sequence_Num = 0
highest_Ack = 0
ack_Num = 0
disconnect_Msg = "fin"
acks_Recv = 0

################################ Functions ##################################

# Simulates sending packets in window, with a [packet_loss_chance]% of losing a packet
def sendNPackets(sequence_Num):
    data = buildNPackets(sequence_Num)
    data = data.strip()
    
    if dataIsNotEmpty(data):
        #print("Data sent", data)
        conn.send(data.encode())
        return True
        
    else:
        pass
        return False
        
# Checks if data is empty
def dataIsNotEmpty(data):       
    if (len(data) > 0):
        return True
        
# Builds a string of packets to send to receiver        
def buildNPackets(sequence_Num):
    data = ""
    for x in range(0, window_size):
        random_int =  random.randint(1,100)
        
        # Max sequence number has been reached
        if (sequence_Num >= num_packets):
            continue
            
        # Packet is "lost"
        if (random_int < packet_loss_chance):
            sequence_Num += 1
        
        # Packet is not "lost"
        elif (random_int >= packet_loss_chance):
            data += message + str(sequence_Num) + " | "
            sequence_Num += 1   
    return data

# Waits for Acks, will accept [window size] at a time
def waitForAcks(sequence_Num, highest_Ack, acks_Recv):         
    for x in range(0, 5):
        response = conn.recv(6);
    
        if not response or response == "":
            continue    
        
        else: 
            ack_Num = getAckNum(response)
            evaluateAck(ack_Num)    
                
            # Decide if highest Ack value needs to be updated   
            if isNewHighestAck(ack_Num, highest_Ack):
                acks_Recv = acks_Recv + 1
                highest_Ack = ack_Num
                
        if isLastAck(ack_Num, num_packets):
            break
            
    sequence_Num = setNewSequenceNum(highest_Ack, acks_Recv)
    return sequence_Num, highest_Ack, acks_Recv

# Set new Sequence Number based on highest Ack received
def setNewSequenceNum(highest_Ack, acks_Recv):
    if (int(acks_Recv) == 0):
        return 0
    else:
        return int(highest_Ack) + 1

# Check if latest Ack received is the last one expected
def isLastAck(ack_Num, num_packets):
    if (int(ack_Num) == (num_packets - 1)):
        return True
    
# Evaluate whether the latest received Ack is the highest one received          
def isNewHighestAck(ack_Num, highest_Ack):
    if int(ack_Num) > int(highest_Ack):
        return True

# Evaluate Ack to determine if it should be printed or not  
def evaluateAck(ack_Num):
    # (Special Case) Hello:0 was not received
    if (int(ack_Num) < 0):
        pass
    
    elif (int(ack_Num) == highest_Ack and int(ack_Num) != 0):
        pass

    else:
        print ("Ack:",ack_Num)
    
# Get Ack Num from response 
def getAckNum(response):
    response = (response.decode())
    ack_Num = response.strip()
    ack_Num = response[4:].strip()
    return ack_Num

# send disconnect message to Receiver, then close connection
def endConnection():
    print("All packets sent, closing connection.")
    conn.send(disconnect_Msg.encode())
    
################################ Beginning of Program ##################################
# Sends N packets, waits for Acks, then sends next N packets based on the highest Ack received

while sequence_Num < num_packets:
    try:
        if sendNPackets(sequence_Num) == True:
            sequence_Num, highest_Ack, acks_Recv = waitForAcks(sequence_Num, highest_Ack, acks_Recv)  
            print("")
    except socket.timeout:
       continue
endConnection() 
client_socket.close()