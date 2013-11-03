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

class Server(pb.Referenceable):

    def __init__(self):
        self.users = {}
        self.localMachines = {}

    def remote_addLocalMachine(self, username, localMachine):
        if not self.users.has_key(username):
            self.users[username] = []
        self.users[username].append(localMachine)

    def remote_addUser(self, username):
        self.users.append(username)

    def sendFileToLocalMachines(self, from_localMachine, username, fileName, timeStamp):
        user = self.users[username]
        if user:

            for localMachine in user:
                localMachine.callRemote("sendFile", fileName, timeStamp)



fileio = FileIOFactory({})
localMachine = fileio.getRootObject()
localMachine.addCallBack()
reactor.listenTCP(port, fileio)

reactor.run()