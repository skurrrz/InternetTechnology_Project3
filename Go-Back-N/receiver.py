import socket
import re
import time

################################## Receiver.py ######################################

# This is the receiver portion of the "Go-Back-N" algorithm
# Sender will send 5 packets at a time, but they might get lost before they get to Receiver
# Packet loss is simulated with "packet_loss_chance" (default is 30%), there is a 30% chance
#   that the packet N will not make it to receiver
# Receiver will send back Acks in sequential order; if it receives a packet out of order it will
#   continue to send an Ack for the last received packet until the Sender sends the correct packet

################################# Create Socket ######################################

receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
receiver_socket.settimeout(5)
HOST ="localhost"
PORT =8000
receiver_socket.connect((HOST,PORT))

#################################### Variables ########################################

# Customizable variables
num_packets = 10                # Total number of packets to be sent [0, num_packets]
window_size = 5                 # Window size, all packets must be ACKed before window shifts
message = "Ack:"                # This is the message to be sent to the Receiver

# Variables for program
disconnect_Msg = "fin"
num_packets_received = 0
ack_Num = 0
packet_Num = 0

#################################### Functions ######################################
    
# Evaluates string of packets sent from Sender  
def evaluatePacketSequence(data, ack_Num, num_packets_received):       
    packets_Remain = True
    
    for x in range(0, window_size):
        response = ""
        
        if (receivedAllPackets(ack_Num) == True):
            break
            
        else:
            data = encodeData(data)
      
            if (dataIsNotEmpty(data) and isRemainingPackets(packets_Remain)): 
                packet_Num, data = getNextPacketNum(data)
                
            # If sequence number == expected next packet number, send Ack and print message
            if evaluatePacket(packet_Num, ack_Num, packets_Remain, num_packets_received) == True:
                ack_Num += 1    
                num_packets_received += 1
            else:
                packets_Remain = False 
                
    return ack_Num, num_packets_received

# Checks if there are remaining packets in the string   
def isRemainingPackets(packets_Remain):
    if packets_Remain == True:
        return True
        
# Checks if data is not empty   
def dataIsNotEmpty(data):
    if len(data.decode()) > 0:
        return True
    
# Encodes data if necessary
def encodeData(data):
    try:
        data = data.encode()
    except:
        pass    
    return data
    
# Check if all total packets have been received
def receivedAllPackets(ack_Num):
    if (num_packets_received >= num_packets):   
        receiver_socket.send(disconnect_Msg.encode())   
        return True
    

# Evaluates first packet in data string 
def evaluatePacket(packet_Num, ack_Num, packets_Remain, num_packets_received):
    if (isNextExpectedNum(packet_Num, ack_Num) and isRemainingPackets(packets_Remain)): 
        print("Hello:" + str(ack_Num))
        response = message + str(ack_Num) + " "
        receiver_socket.send(response.encode())
        return True
        
    # Packet received was not the expected next packet
    elif (int(packet_Num) != ack_Num):
    
        # (Special case) Hello:0 has not been received yet
        if (num_packets_received == 0):
            response = "Ack:-1"
            
        #Sends back last Ack
        else:
            response = "Ack:" + str(ack_Num - 1) + " "
        
        #Sends back last received Ack
        receiver_socket.send(response.encode()) 
        return False

# Checks if the current received packet is the next expected one
def isNextExpectedNum(packet_Num, ack_Num):
    if int(packet_Num) == ack_Num:
        return True
        
# Get the next packet number from the sequence       
def getNextPacketNum(data):
    packet_Num, data = data.split(b'|', 1)
    packet_Num = packet_Num.decode('utf-8')
    data = data.decode('utf-8')
    packet_Num = packet_Num.replace(' ','')     
    packet_Num = packet_Num[6:]   
    return packet_Num, data

# Check if disconnect message was sent to receiver               
def disconnectRequested(data):
    if data.decode('utf-8') == "fin":
        return True             

# Print connection end message              
def endConnection():
    print("All packets sent, closing connection.")
        
################################ Beginning of Program ##################################

while True:
    data = receiver_socket.recv(1000);
        
    if not data or data == "":
        continue
        
    if disconnectRequested(data) == True:
        endConnection()
        break
        
    else:
        ack_Num, num_packets_received = evaluatePacketSequence(data, ack_Num, num_packets_received)
        print("")
    
receiver_socket.close() 