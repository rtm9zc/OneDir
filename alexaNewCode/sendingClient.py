__author__ = 'Student'

from multiprocessing import Process
from twisted.internet import reactor
import sendFile
import moveMessage
import os

def getExtension(filename):
    return os.path.splitext(filename)[-1].lower()

class LocalMachine():

    def __init__(self, username, directory, address):
        self.username = username
        self.oneDir = directory
        # address of server to send to
        self.address = address
        # port to send files on (from client side)
        self.port = 1234

    def transmitFile(self, source):
        sendFile.sendFile(source,self.address,self.port)
        print 'Dialing on port',self.port,'..'
        reactor.run(installSignalHandlers=0)

    def transmitDelete(self, source):
        filePath = 'delete' + source
        moveMessage.sendMessage(filePath,self.address,self.port)
        print 'Dialing on port',self.port,'..'
        reactor.run(installSignalHandlers=0)

    def getUsername(self):
        return self.username

    def getAddress(self):
        return self.address

    #These will be only called from the OneDirHandler
    #Will be handled by a listener method on the server
    def moved(self, fileSource, destination):
        #print "_____MOVE______"

        p = Process(target=self.transmitFile, args=(destination,))
        p.start()
        if getExtension(fileSource) != '.tmp':
            p2 = Process(target=self.transmitDelete, args=(fileSource,))
            p2.start()

    def deleted(self, fileSource):
        #print "_____DELETE______"
        fileData = [self.username, self.address, "del", fileSource]
        #self.sendArray(fileData)
        #some shit to listen for a confirming response
        p = Process(target=self.transmitDelete, args=(fileSource,))
        p.start()
    def modified(self, fileSource):
        #print "_____MOD______"
        fileData = [self.username, self.address, "mod", fileSource]
        #self.sendArray(fileData)
        #some shit to listen for a confirming response
        p = Process(target=self.transmitFile, args=(fileSource,))
        p.start()

    def created(self, fileSource):
        #print "_____CREATE______"
        fileData = [self.username, self.address, "cre", fileSource]
        #self.sendArray(fileData)
        #some shit to listen for a confirming response.
        p = Process(target=self.transmitFile, args=(fileSource,))
        p.start()



