__author__ = 'Student'

from twisted.spread import pb
from twisted.internet import reactor
from fileTransferServerAndClient.py import *


from binascii import crc32
from optparse import OptionParser
import os, json, pprint, datetime

from twisted.protocols import basic
from twisted.internet import protocol, defer, reactor
from twisted.application import service, internet
from twisted.python import log
from twisted.internet.protocol import ServerFactory
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import FileSender
from twisted.internet.defer import Deferred
from twisted.internet import reactor

class LocalMachine(pb.root):
    def remote_sendFile(self, fileName, timeStamp):
        transmitOne(file_path,port=port,address=address)




factory = pb.PBClientFactory()
reactor.connectTCP("localhost", 8800, factory)

reactor.run()