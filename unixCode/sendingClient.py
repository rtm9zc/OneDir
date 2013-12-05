
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
        # print 'Dialing on port',self.port,'..'
        reactor.run(installSignalHandlers=0)

    def transmitDelete(self, source):
        filePath = 'delete' + source
        moveMessage.sendMessage(filePath,self.address,self.port)
        # print 'Dialing on port',self.port,'..'
        reactor.run(installSignalHandlers=0)

    def getUsername(self):
        return self.username

    def getAddress(self):
        return self.address

    def transmitMessage(self, message):
        moveMessage.sendMessage(message,self.address,self.port)
        reactor.run(installSignalHandlers=0)

    def sendMessage(self, message):
        p = Process(target=self.transmitMessage, args=(message,))
        p.start()

    #These will be only called from the OneDirHandler
    #Will be handled by a listener method on the server
    def moved(self, fileSource, destination):
        # p = Process(target=self.transmitFile, args=(destination,))
        # p.start()
        # if getExtension(fileSource) != '.tmp':
        #     p2 = Process(target=self.transmitDelete, args=(fileSource,))
        #     p2.start()

        if getExtension(fileSource) != '.tmp':
            message = 'moved' + fileSource + "##" + destination
            p = Process(target=self.transmitMessage, args=(message,))
            p.start()

        else:
            p2 = Process(target=self.transmitFile, args=(destination,))
            p2.start()


    def deleted(self, fileSource):
        p = Process(target=self.transmitDelete, args=(fileSource,))
        p.start()

    def modified(self, fileSource):
        p = Process(target=self.transmitFile, args=(fileSource,))
        p.start()

    def created(self, fileSource):
        p = Process(target=self.transmitFile, args=(fileSource,))
        p.start()



