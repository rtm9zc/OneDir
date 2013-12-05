
from serverClasses import *
import sys

import threading

import moveMessage

from binascii import crc32
import os, json, pprint

from twisted.protocols import basic
from twisted.internet.protocol import ServerFactory
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import FileSender
from twisted.internet.defer import Deferred
from twisted.internet import reactor
from logHandler import adminLog

import time

pp = pprint.PrettyPrinter(indent=1)

from time import gmtime, strftime



class TransferCancelled(Exception):
    """ Exception for a user cancelling a transfer """
    pass


class ServerReceiverProtocol(basic.LineReceiver):
    """ File Receiver """

    def __init__(self):
        """ """
        self.outfile = None
        self.remain = 0
        self.crc = 0
        self.isFile = True

    def lineReceived(self, line):
        """ """
        print ' ~ lineReceived:\n\t', line

        self.timeOut = False

        currentTime = int(time.time())

        self.factory.setMachineTimes(currentTime, self.transport.getPeer().host)


        self.isFile = True
        self.isSyncChange = False
        self.Failure = False
        self.syncChangeToOn = False

        # get username via ip address
        clientUsername = self.factory.retrieveUser(self.transport.getPeer().host)


        if line == 'syncOn':
            #self.factory.log.add(clientUsername + ": Sync is now on")
            self.factory.setSyncMachine(self.transport.getPeer().host, True)
            self.isFile = False
            self.isSyncChange = True
            self.syncChangeToOn = True

            #self.factory.clearSyncQueue(self.transport.getPeer().host)

            #print self.factory.usersToLM
            self.transport.loseConnection()
            return

        if line == 'syncOff':
            #self.factory.log.add(clientUsername + ": Sync is now off")
            self.factory.setSyncMachine(self.transport.getPeer().host, False)
            self.isFile = False
            self.isSyncChange = True
            #print self.factory.usersToLM
            self.transport.loseConnection()
            return

        # Create the upload directory if not already present
        uploaddir = os.path.join(self.factory.dir_path, clientUsername)

        if line[0:6] == 'delete':
            originalPath = line[6:]
            machinePath = self.factory.retrieveFilePath(self.transport.getPeer().host)
            endPath = os.path.relpath(originalPath, machinePath)
            pathToDelete = os.path.join(uploaddir, endPath)
            if os.path.exists(pathToDelete):

                src = pathToDelete
                destDir = os.path.join(self.factory.dir_path, "previousFileVersions")
                destFile = os.path.join(destDir, clientUsername + strftime("%Y-%m-%d %H.%M.%S", gmtime()) + os.path.basename(self.original_fname))
                shutil.copyfile(src, destFile)

                os.remove(pathToDelete)
            else:
                self.Failure = True
                self.transport.loseConnection()
                return
            self.isFile = False
            #self.factory.log.add("File modifications for user " + clientUsername)
            self.outfilename = 'delete' + pathToDelete



            self.transport.loseConnection()
            return

        if line[0:5] == 'moved':
            sourceDestString = line[5:]
            sourceAndDest = sourceDestString.split("##")
            source = sourceAndDest[0]
            destination = sourceAndDest[1]
            machinePath = self.factory.retrieveFilePath(self.transport.getPeer().host)
            endSource = os.path.relpath(source, machinePath)
            endDest = os.path.relpath(destination, machinePath)
            sourcePath = os.path.join(uploaddir, endSource)
            destinationPath = os.path.join(uploaddir, endDest)
            if os.path.exists(sourcePath):
                shutil.move(sourcePath, destinationPath)
            else:
                self.Failure = True
                self.transport.loseConnection()
                return
            self.isFile = False
            self.outfilename = 'moved' + sourcePath + '##' + destinationPath
            self.transport.loseConnection()
            return


        if line[0:5] == 'isDir':

            if line[5:12] == 'Created':
                originalPath = line[12:]
                machinePath = self.factory.retrieveFilePath(self.transport.getPeer().host)
                endDir = os.path.relpath(originalPath, machinePath)
                newDir = os.path.join(uploaddir, endDir)
                if not os.path.exists(newDir):
                    os.makedirs(newDir)
                else:
                    self.Failure = True
                    self.transport.loseConnection()
                    return
                self.isFile = False
                self.outfilename = 'isDirCreated' + newDir
                self.transport.loseConnection()
                return

            if line[5:12] == 'Deleted':
                originalPath = line[12:]
                machinePath = self.factory.retrieveFilePath(self.transport.getPeer().host)
                endDir = os.path.relpath(originalPath, machinePath)
                dirToRemove = os.path.join(uploaddir, endDir)
                if os.path.exists(dirToRemove):
                    shutil.rmtree(dirToRemove)
                else:
                    self.Failure = True
                    self.transport.loseConnection()
                self.isFile = False
                self.outfilename = 'isDirDeleted' + dirToRemove
                self.transport.loseConnection()
                return

        # otherwise upload file as usual

        self.instruction = json.loads(line)
        self.instruction.update(dict(client=self.transport.getPeer().host))
        self.size = self.instruction['file_size']
        self.original_fname = self.instruction.get('original_file_path',
                                                   'not given by client')


        print " * Using upload dir:",uploaddir
        if not os.path.isdir(uploaddir):
            os.makedirs(uploaddir)


        machinePath = self.factory.retrieveFilePath(self.transport.getPeer().host)
        endFileName = os.path.relpath(self.original_fname, machinePath)

        # Need to change to be able to handle files within subdirectories!!!
        self.outfilename = os.path.join(uploaddir, endFileName)

        src = self.outfilename
        destDir = os.path.join(self.factory.dir_path, "previousFileVersions")
        destFile = os.path.join(destDir, clientUsername + strftime("%Y-%m-%d %H.%M.%S", gmtime()) + os.path.basename(self.original_fname))
        if os.path.exists(src):
            shutil.copyfile(src, destFile)

        fullUploadDir, tail = os.path.split(self.outfilename)
        if not os.path.isdir(fullUploadDir):
            os.makedirs(fullUploadDir)

        print ' * Receiving into file@',self.outfilename
        try:
            self.outfile = open(self.outfilename,'wb')
        except Exception, value:
            print ' ! Unable to open file', self.outfilename, value
            self.transport.loseConnection()
            return

        self.remain = int(self.size)
        print ' & Entering raw mode.',self.outfile, self.remain
        self.setRawMode()

    def rawDataReceived(self, data):
        """ """
        if self.remain%10000==0:
            print '   & ',self.remain,'/',self.size
        self.remain -= len(data)

        self.crc = crc32(data, self.crc)
        self.outfile.write(data)

    def connectionMade(self):
        """ """
        #self.log("Connection made...")
        basic.LineReceiver.connectionMade(self)
        print '\n + a connection was made'
        print ' * ',self.transport.getPeer()

    def connectionLost(self, reason):

        clientUsername = self.factory.retrieveUser(self.transport.getPeer().host)

        #self.factory.log.add("Connection lost for user " + clientUsername)

        if self.isFile == False:
            print 'connection lost'
            if self.isSyncChange or self.Failure:
                print 'connection Lost'
                if self.syncChangeToOn:
                    self.factory.clearSyncQueue(self.transport.getPeer().host)
            else:
                user_address = self.transport.getPeer().host
                self.factory.sendMessageToMachines(user_address, self.outfilename)
        if self.isFile == True:
            #self.factory.log.add("File modifications for user " + clientUsername)
            basic.LineReceiver.connectionLost(self, reason)
            print ' - connectionLost'
            if self.outfile:
                self.outfile.close()
                # Problem uploading - tmpfile will be discarded
            if self.remain != 0:
                print str(self.remain) + ')!=0'
                remove_base = '--> removing tmpfile@'
                if self.remain<0:
                    reason = ' .. file moved too much'
                if self.remain>0:
                    reason = ' .. file moved too little'
                print remove_base + self.outfilename + reason
                os.remove(self.outfilename)

            # Success uploading - tmpfile will be saved to disk.
            else:

                user_address = self.transport.getPeer().host

                print 'user_address is ' + user_address

                self.factory.sendToMachines(user_address, self.outfilename)

                print '\n--> finished saving upload@' + self.outfilename

                #self.factory.testSendMachines(user_address)

def fileinfo(fname):
    """ when "file" tool is available, return it's output on "fname" """
    return ( os.system('file 2> /dev/null')!=0 and \
             os.path.exists(fname) and \
             os.popen('file "'+fname+'"').read().strip().split(':')[1] )

class FileIOClient(basic.LineReceiver):
    """ file sender """

    def __init__(self, path, controller):
        """ """
        print "in FileIOClient"

        self.path = path
        self.controller = controller

        self.infile = open(self.path, 'rb')
        self.insize = os.stat(self.path).st_size

        self.result = None
        self.completed = False

        self.controller.file_sent = 0
        self.controller.file_size = self.insize

    def _monitor(self, data):
        """ """
        self.controller.file_sent += len(data)
        self.controller.total_sent += len(data)

        # Check with controller to see if we've been cancelled and abort
        # if so.
        if self.controller.cancel:
            print 'FileIOClient._monitor Cancelling'

            # Need to unregister the producer with the transport or it will
            # wait for it to finish before breaking the connection
            self.transport.unregisterProducer()
            self.transport.loseConnection()

            # Indicate a user cancelled result
            self.result = TransferCancelled('User cancelled transfer')

        return data

    def cbTransferCompleted(self, lastsent):
        """ """
        self.completed = True
        self.transport.loseConnection()

    def connectionMade(self):
        """ """
        instruction = dict(file_size=self.insize,
                           original_file_path=self.path)
        instruction = json.dumps(instruction)
        print "test"
        self.transport.write(instruction+'\r\n')
        sender = FileSender()
        sender.CHUNK_SIZE = 2 ** 16
        d = sender.beginFileTransfer(self.infile, self.transport,
                                     self._monitor)
        d.addCallback(self.cbTransferCompleted)

    def connectionLost(self, reason):
        """
            NOTE: reason is a twisted.python.failure.Failure instance
        """
        from twisted.internet.error import ConnectionDone
        basic.LineReceiver.connectionLost(self, reason)
        print ' - connectionLost\n  * ', reason.getErrorMessage()
        print ' * finished with',self.path
        self.infile.close()
        if self.completed:
            self.controller.completed.callback(self.result)
        else:
            self.controller.completed.errback(reason)

class FileIOClientFactory(ClientFactory):
    """ file sender factory """

    protocol = FileIOClient

    def __init__(self, path, controller):
        """ """
        print 'in FileIOClientFactory class'
        self.path = path
        self.controller = controller

    def clientConnectionFailed(self, connector, reason):
        """ """
        print 'client connection failed'
        ClientFactory.clientConnectionFailed(self, connector, reason)
        self.controller.completed.errback(reason)

    def buildProtocol(self, addr):
        """ """
        print ' + building protocol'
        p = self.protocol(self.path, self.controller)
        p.factory = self
        return p


def transmitOne(path, address, port=1235,):
    """ helper for file transmission """
    controller = type('test',(object,),{'cancel':False, 'total_sent':0,'completed':Deferred()})
    f = FileIOClientFactory(path, controller)
    reactor.connectTCP(address, port, f)
    return controller.completed



class FileIOServerFactory(ServerFactory):
    """ file receiver factory """
    protocol = ServerReceiverProtocol

    def __init__(self, filePath, address=str(sys.argv[1]), send_port=1235, listen_port=1234):
        """ """
        # server filepath
        self.dir_path = filePath
        # server address
        self.address_ = address

        self.send_port = send_port
        self.listen_port = listen_port

        self.adminUser = ["admin"]
        self.usersToPW = {"admin": "pw"}
        adminMachine = BabyLocalMachine("admin", "1", "randomIP", "path")
        self.usersToLM = {"admin": [adminMachine]}

        #self.log = adminLog()


    def sendToMachines(self, address, filepath):
        username = self.retrieveUser(address)
        for machine in self.usersToLM[username]:
            if machine.ipAddress != address:
                #print 'address is ', address
                if machine.update:
                    if machine.syncState:
                        transmitOne(filepath,machine.ipAddress,self.send_port)
                    else:
                        machine.syncQueue.put(filepath)

    def sendMessageToMachines(self, address, filepath):
        username = self.retrieveUser(address)
        for machine in self.usersToLM[username]:
            if machine.ipAddress != address:
                #print 'address is ', address
                if machine.update:
                    if machine.syncState:
                        moveMessage.sendMessage(filepath,machine.ipAddress,self.send_port)
                    else:
                        machine.syncQueue.put(filepath)

    def retrieveUser(self, address):
        for username in self.usersToLM:
            for machine in self.usersToLM[username]:
                if machine.ipAddress == address:
                    return username

    def setSyncMachine(self, address, syncOn):
        for username in self.usersToLM:
            for machine in self.usersToLM[username]:
                if machine.ipAddress == address:
                    machine.syncState = syncOn

    def clearSyncQueue(self, address):
        for username in self.usersToLM:
            for machine in self.usersToLM[username]:
                if machine.ipAddress == address:
                    while not machine.syncQueue.empty():
                        message = machine.syncQueue.get()
                        if os.path.exists(message):
                            transmitOne(message, address, self.send_port)
                        else:
                            moveMessage.sendMessage(message, address, self.send_port)

    def retrieveFilePath(self, address):
        for username in self.usersToLM:
            for machine in self.usersToLM[username]:
                if machine.ipAddress == address:
                    return machine.pathToDirectory

    def setMachineTimes(self, time, address):
        currentUser = 'test'
        for username in self.usersToLM:
            for machine in self.usersToLM[username]:
                if machine.ipAddress == address:
                    currentUser = username
                    machine.lastUpdateTime = time
                    machine.update = False
        for machine in self.usersToLM[currentUser]:
            if (time - machine.lastUpdateTime) < 3:
                machine.update = False
            else:
                machine.update = True

    def send_file(self, filePath, address):
        port = self.send_port
        controller = type('test',(object,),{'cancel':False, 'total_sent':0,'completed':Deferred()})
        f = FileIOClientFactory(filePath, controller)
        reactor.connectTCP(address, port, f)
        return controller.completed


if __name__ == "__main__":

    #HOST, PORT = str(sys.argv[1]), 9999
    HOST, PORT = '', 9999

    print HOST
    print PORT

    twisted_server = FileIOServerFactory(str(sys.argv[2]))

    # Create the server, binding to localhost on port 9999
    socket_server = ThreadedTCPServer((HOST, PORT), MyTCPHandler, twisted_server)
    server_thread = threading.Thread(target=socket_server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    reactor.listenTCP(twisted_server.listen_port,twisted_server)
    print 'Listening on port',twisted_server.listen_port,'..'
    reactor.run()