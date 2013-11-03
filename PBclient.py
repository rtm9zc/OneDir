__author__ = 'Student'

from twisted.spread import pb
from twisted.internet import reactor
from file_transfer import *
from binascii import crc32


class LocalMachine(pb.root):

    def __init__(self, filePath, address='127.0.0.1', port='1234'):
        self.file_path_ = filePath
        self.address_ = address
        self.port_ = port


    def remote_sendFile(self, fileName, timeStamp):
        transmitOne(self.file_path_,self.port_,self.address_)





factory = pb.PBClientFactory()
reactor.connectTCP("localhost", 8800, factory)

reactor.run()