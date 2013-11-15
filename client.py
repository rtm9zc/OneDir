__author__ = 'Student'

from twisted.spread import pb
from twisted.internet import reactor
from file_transfer import *
import pickle
from socket import *

# Client listening port (and server sending port) = 2000
# Server listening port (and client sending port) = 3000
# Client send array port (and server listening array port) = 4000


class LocalMachine():

    def __init__(self, username, filePath, address='localhost'):
        self.username_ = username
        self.file_path_ = filePath
        self.address_ = address
        
        self.listeningport = 2000
        self.sendingport = 3000
        self.arrayport = 4000

        

    def sendFile(self):
        transmitOne(self.file_path_,self.address_,self.port)
        print 'Dialing on port',self.port,'..'
        reactor.run(installSignalHandlers=0)
        #will not work more than once!
        #fix this ^
        #         | ?  Works, but buggy, I think.

    def sendArray(self, array):
        host = "localhost"
        #port = self.port
        buf = 4096
        addr = (host,self.port)

        # Create socket
        UDPSock = socket(AF_INET,SOCK_DGRAM)

        # Send the array
        while (1):
            if(UDPSock.sendto( pickle.dumps(array), addr)):
                print "Sending message"
                break

        # Close socket
        UDPSock.close()



    def getUsername(self):
        return self.username_

    def getAddress(self):
        return self.address_

    #These will be only called from the OneDirHandler
    #Will be handled by a listener method on the server
    def moved(self, source, destination):
        print "_____MOVE______"
        fileData = [self.username_, self.address_, "mov", source, destination]
        #self.sendArray(fileData)
        #some shit to listen for a confirming response
    def deleted(self, file):
        print "_____DELETE______"
        fileData = [self.username_, self.address_, "del", file]
        #self.sendArray(fileData)
        #some shit to listen for a confirming response
    def modified(self, file):
        print "_____MOD______"
        fileData = [self.username_, self.address_, "mod", file]
        #self.sendArray(fileData)
        #some shit to listen for a confirming response
        #p = Process(target=self.sendFile)
        #p.start()

    def created(self, file):
        print "_____CREATE______"
        fileData = [self.username_, self.address_, "cre", file]
        #self.sendArray(fileData)
        #some shit to listen for a confirming response.
        #p = Process(target=self.sendFile)
        #p.start()



