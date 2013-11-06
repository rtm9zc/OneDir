from socket import *

from array import *
import pickle

# Set the socket parameters
host = "localhost"
port = 21567
buf = 4096
addr = (host,port)

# Create socket
UDPSock = socket(AF_INET,SOCK_DGRAM)


a = [1,2,3,4]
# Send messages
while (1):
    if(UDPSock.sendto( pickle.dumps(a), addr)):
        print "Sending message"
        break

# Close socket
UDPSock.close()