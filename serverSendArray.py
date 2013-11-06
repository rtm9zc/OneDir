from socket import *
import pickle


# Set the socket parameters
host = "localhost"
port = 21567
buf = 4096
addr = (host,port)

# Create socket and bind to address
UDPSock = socket(AF_INET,SOCK_DGRAM)
UDPSock.bind(addr)

# Receive messages
while 1:

    data,addr = UDPSock.recvfrom(buf)
    receivedArray = pickle.loads(data)
    print repr(receivedArray) # prints array('i', [1, 3, 2])
    break


# Close socket
UDPSock.close()