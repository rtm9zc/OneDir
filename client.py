__author__ = 'Student'

from twisted.spread import pb
from twisted.internet import reactor
from file_transfer import *
from binascii import crc32


class LocalMachine(pb.root):

    def __init__(self, username, filePath, address='127.0.0.1', port='1234'):
        self.username_ = username
        self.file_path_ = filePath
        self.address_ = address
        self.port_ = port


    def sendFile(self, fileName):
        transmitOne(self.file_path_,self.port_,self.address_)
        reactor.run()

    def getUsername(self):
        return self.username_


# set up as server

fileio = FileIOFactory({})
reactor.listenTCP(port, fileio)
print 'Listening on port',port,'..'
reactor.run()

# if we get watchdog event, call sendFile()

while True:
    # if watchdog event occurs
        # call sendFile() method



