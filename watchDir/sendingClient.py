__author__ = 'Student'

from multiprocessing import Process
from twisted.internet import reactor
import sendFile



class LocalMachine():

    def __init__(self, username, directory, address='localhost'):
        self.username = username
        self.oneDir = directory
        self.address = address
        self.port = 1234

    def transmitFile(self, source):
        sendFile.sendFile(source,self.address,self.port)
        print 'Dialing on port',self.port,'..'
        reactor.run(installSignalHandlers=0)
    #
    #def sendArray(self, array):
    #    host = "localhost"
    #    #port = self.port
    #    buf = 4096
    #    addr = (host,self.port)
    #
    #    # Create socket
    #    UDPSock = socket(AF_INET,SOCK_DGRAM)
    #
    #    # Send the array
    #    while (1):
    #        if(UDPSock.sendto( pickle.dumps(array), addr)):
    #            print "Sending message"
    #            break
    #
    #    # Close socket
    #    UDPSock.close()

    def getUsername(self):
        return self.username

    def getAddress(self):
        return self.address

    #These will be only called from the OneDirHandler
    #Will be handled by a listener method on the server
    def moved(self, fileSource, destination):
        #print "_____MOVE______"
        fileData = [self.username, self.address, "mov", fileSource, destination]
        #self.sendArray(fileData)
        #some shit to listen for a confirming response
    def deleted(self, fileSource):
        #print "_____DELETE______"
        fileData = [self.username, self.address, "del", fileSource]
        #self.sendArray(fileData)
        #some shit to listen for a confirming response
    def modified(self, fileSource):
        #print "_____MOD______"
        fileData = [self.username, self.address, "mod", fileSource]
        #self.sendArray(fileData)
        #some shit to listen for a confirming response
        p = Process(target=self.transmitFile, args=(fileSource,))
        p.start()

    def created(self, fileSource):
        #print "_____CREATE______"
        fileData = [self.username_, self.address_, "cre", fileSource]
        #self.sendArray(fileData)
        #some shit to listen for a confirming response.
        p = Process(target=self.transmitFile, args=(fileSource,))
        p.start()



