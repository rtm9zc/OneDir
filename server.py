__author__ = 'Student'

from twisted.spread import pb
from twisted.internet import reactor
from file_transfer import *
from binascii import crc32


class Server():

    def __init__(self):
        # stores local machines; dictionary
        self.usersToLM = {}
        # stores users to passwords
        self.usersToPW = {}
        # server filepath

    def addLocalMachine(self, username, localMachine):
        if username not in self.users:
            self.usersToLM[username] = []
        self.usersToLM[username].append(localMachine)

    def addUser(self, username, password):
        if username not in self.userAccounts:
            self.usersToPW[username] = password
        else:
            # raise an error that an account w/ that username already exists

    # method to check passwords against username; returns boolean
    def checkPassword(self, username, password):
        if username in self.usersToPW:
            return self.usersToPW[username] == password
        else:
            return False

    def sendFileToLocalMachines(self, username, filePath):

        # modify filePath to reflect server's filePath

        local_machines = self.usersToLM[username]
        #for  in local_machines:
            #localMachine.callRemote("sendFile", fileName, timeStamp)
        for machine in local_machines:
            transmitOne(filePath, )

fileio = FileIOFactory({})
reactor.listenTCP(port, fileio)
print 'Listening on port',port,'..'
reactor.run()