__author__ = 'Student'

from twisted.spread import pb
from twisted.internet import reactor
#from file_transfer import *
import listenAndServe
#from fileTransferServerAndClient import *
from binascii import crc32
from client import *

import pickle
from socket import *


class Server():

    def __init__(self, filePath):
        # stores local machines; dictionary
        self.usersToLM = {}
        # stores users to passwords
        self.usersToPW = {}
        # server filepath
        self.file_path = filePath
        self.port = 1234



    def addLocalMachine(self, username, localMachine):
        if username not in self.usersToLM:
            self.usersToLM[username] = []
        self.usersToLM[username].append(localMachine)

    def addUser(self, username, password):
        if username not in self.usersToPW:
            self.usersToPW[username] = password
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
        #for machine in local_machines:
            #transmitOne(filePath, )

# if __name__=='__main__':
#     test_server = Server('/TestServer')
#     lm_one = LocalMachine('testUser', '/test_user/machineOne/OneDir', address='localhost', port=1234)
#     lm_two = LocalMachine('testUser', '/test_user/machineTwo/OneDir', address='localhost', port=1234)
#     test_server.addUser('testUser', 1234)
#     test_server.addLocalMachine('testUser', lm_one)
#     test_server.addLocalMachine('testUser', lm_two)

    # os.system("~/PycharmProjects/OneDir/fileTransferServerAndClient.py ")



if __name__=='__main__':
    test_server = Server('~/TestServer')
    lm_one = LocalMachine('testUser', '~/test_user/machineOne/OneDir', address='localhost', port=1234)
    lm_two = LocalMachine('testUser', '~/test_user/machineTwo/OneDir', address='localhost', port=1234)
    test_server.addUser('testUser', 1234)
    test_server.addLocalMachine('testUser', lm_one)
    test_server.addLocalMachine('testUser', lm_two)
    # remove/fix below, pointless, doesn't need to call a new process or whatever, easier ways to do it
    # just call method with port and file path
   # command = 'python ~/PycharmProjects/OneDir/fileTransferServerAndClient.py --server --port ' +  + ' ' + test_server.file_path_
    fileio = listenAndServe.FileIOFactory({})
    reactor.listenTCP(test_server.port, fileio)
    #test_server.file_path
    print 'Listening on port',test_server.port,'..'
    reactor.run()

    # detect which machine it came from and name of file
   # filename = 'testfile.docx'
    #from_machine = lm_one
   # for machine in test_server.usersToLM[lm_one.getUsername()]:
    #    if machine != lm_one:
      #      #command = 'python ~/PycharmProjects/OneDir/fileTransferServerAndClient.py --client ' + test_server.file_path_ + '/' + filename
            #os.system(command)
      #      print "we will now send the file to machine with username " + machine.getUsername() + " and address " + machine.getAddress()


    #The server needs to listen for whether it receives a new array from a client
            #(this will indicate what work it needs to do to handle a file change)
    #|
    #v not reallly sure why this is necessary

    # Set the socket parameters
    #    host = "localhost"
     #   port = 21567
    #    buf = 4096
    #    addr = (host,port)
    #
        # Create socket and bind to address
     #   UDPSock = socket(AF_INET,SOCK_DGRAM)
     #   UDPSock.bind(addr)

        # Receive messages
     #   while 1:

     #       data,addr = UDPSock.recvfrom(buf)
     #       receivedArray = pickle.loads(data)
     #       break
        # We do not close the socket so it will continue to listen after it receives an array