__author__ = 'Student'

from twisted.spread import pb
from twisted.internet import reactor
#from file_transfer import *
import listenAndServe
import Queue
#from fileTransferServerAndClient import *
from binascii import crc32
from client import *
from threading import Thread
import pickle
from socket import *

# Client listening port (and server sending port) = 2000
# Server listening port (and client sending port) = 3000
# Client send array port (and server listening array port) = 4000


class Server():

    def __init__(self, filePath):
        # stores local machines; dictionary
        self.usersToLM = {}
        # stores users to passwords
        self.usersToPW = {}
        # server filepath
        self.file_path = filePath
        self.listeningport = 3000
        self.sendingport = 2000
        self.arrayport = 4000



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

    def receive(self, host, port, buf, aqueue):
        addr = (host,port)
        UDPSock = socket(AF_INET,SOCK_DGRAM)
        UDPSock.bind(addr)
        # Receive messages
        while True:
            try:
                data,addr = UDPSock.recvfrom(buf)
                receivedArray = pickle.loads(data)
                aqueue.put(receivedArray)
            except:
                break

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
    lm_one = LocalMachine('testUser', '/home/student/', address='localhost')
    lm_two = LocalMachine('testUser', '/home/student/', address='localhost')
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
    arrayQueue = Queue.Queue()
    thread = Thread(target = test_server.receive,
                    args = ("localhost", 21567, 4096, arrayQueue))
    while True:
        try:
            if (arrayQueue.empty()):
                time.sleep(1)
            else:
                current = arrayQueue.get()
                function = current[2]
                if (function == "mov"):
                    #change name of file on server
                    #change name on all locals
                    1
                elif (function == "del"):
                    #remove file on server
                    #tell all locals to delete
                    1
                elif (function == "mod"):
                    #update file on server
                    #send new version to all locals
                    1
                elif (function == "cre"):
                    #make new file on server
                    #send file to all locals
                    1
        except:
            break
    thread.join()

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
