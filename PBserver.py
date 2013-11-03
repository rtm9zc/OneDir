__author__ = 'Student'

from twisted.spread import pb
from twisted.internet import reactor
from file_transfer import *
from binascii import crc32


class Server(pb.Referenceable):

    def __init__(self):
        # stores local machines; dictionary
        self.users = {}
        # what does this do?
        #self.localMachines = {}
        self.userAccounts = {}

    def remote_addLocalMachine(self, username, localMachine):
        if username not in self.users:
            self.users[username] = []
        self.users[username].append(localMachine)

    # self.users is now a list of usernames?
    # def remote_addUser(self, username):
        #self.users.append(username)

    def remote_addUser(self, username, password):
        if username not in self.userAccounts:
            self.userAccounts[username] = password
        else:
            # raise an error that an account w/ that username already exists

    # method to check passwords against username; returns boolean
    def remote_checkPassword(self, username, password):
        if username in self.userAccounts:
            return self.userAccounts[username] == password
        else:
            return False

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