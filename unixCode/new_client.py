#from new_file_transfer import *
#from new_server import *
from binascii import crc32
import os
import json
import pprint
import shutil
import fileCrypto

from twisted.protocols import basic
from twisted.internet.protocol import ServerFactory
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import FileSender
from twisted.internet.defer import Deferred
from twisted.internet import reactor

#from sendingClient import LocalMachine

pp = pprint.PrettyPrinter(indent=1)

class TransferCancelled(Exception):
    """ Exception for a user cancelling a transfer """
    pass


class ClientReceiverProtocol(basic.LineReceiver):
    """ File Receiver """

    def __init__(self):
        """ """
        self.outfile = None
        self.remain = 0
        self.crc = 0
        self.isFile = True

    def jsonStuff(self,line):
        self.instruction = json.loads(line)
        self.instruction.update(dict(client=self.transport.getPeer().host))
        self.size = self.instruction['file_size']
        self.original_fname = self.instruction.get('original_file_path',
                                                   'not given by client')


    def lineReceived(self, line):
        """ """
        # print ' ~ lineReceived:\n\t', line

        self.isFile = True

        uploaddir = self.factory.dir_path

        if line[0:6] == 'delete':
            originalPath = line[6:]
            machinePath = os.path.join(self.factory.server_path, self.factory.username)
            endPath = os.path.relpath(originalPath, machinePath)
            pathToDelete = os.path.join(uploaddir, endPath)
            if os.path.exists(pathToDelete):
                os.remove(pathToDelete)
            self.isFile = False
            self.transport.loseConnection()
            return

        if line[0:5] == 'moved':
            sourceDestString = line[5:]
            sourceAndDest = sourceDestString.split("##")
            source = sourceAndDest[0]
            destination = sourceAndDest[1]
            machinePath = os.path.join(self.factory.server_path, self.factory.username)
            endSource = os.path.relpath(source, machinePath)
            endDest = os.path.relpath(destination, machinePath)
            sourcePath = os.path.join(uploaddir, endSource)
            destinationPath = os.path.join(uploaddir, endDest)
            if os.path.exists(sourcePath):
                shutil.move(sourcePath, destinationPath)
            self.isFile = False
            self.transport.loseConnection()
            return

        if line[0:5] == 'isDir':

            if line[5:12] == 'Created':
                originalPath = line[12:]
                machinePath = os.path.join(self.factory.server_path, self.factory.username)
                endDir = os.path.relpath(originalPath, machinePath)
                newDir = os.path.join(uploaddir, endDir)
                if not os.path.exists(newDir):
                    os.makedirs(newDir)
                self.isFile = False
                self.transport.loseConnection()
                return

            if line[5:12] == 'Deleted':
                originalPath = line[12:]
                machinePath = os.path.join(self.factory.server_path, self.factory.username)
                endDir = os.path.relpath(originalPath, machinePath)
                dirToRemove = os.path.join(uploaddir, endDir)
                if os.path.exists(dirToRemove):
                    shutil.rmtree(dirToRemove)
                self.isFile = False
                self.transport.loseConnection()
                return


        self.instruction = json.loads(line)
        self.instruction.update(dict(client=self.transport.getPeer().host))
        self.size = self.instruction['file_size']
        self.original_fname = self.instruction.get('original_file_path',
                                                   'not given by client')

        # Create the upload directory if not already present

        # print " * Using upload dir:",uploaddir
        if not os.path.isdir(uploaddir):
            os.makedirs(uploaddir)

        self.outfilename = os.path.join(uploaddir, os.path.basename(self.original_fname))

        # print ' * Receiving into file@',self.outfilename
        try:
            self.outfile = open(self.outfilename,'wb')
        except Exception, value:
            # print ' ! Unable to open file', self.outfilename, value
            self.transport.loseConnection()
            return

        self.remain = int(self.size)
        # print ' & Entering raw mode.',self.outfile, self.remain
        self.setRawMode()


    def rawDataReceived(self, data):
        """ """
        # if self.remain%10000==0:
        #     print '   & ',self.remain,'/',self.size
        self.remain -= len(data)

        self.crc = crc32(data, self.crc)
        self.outfile.write(data)

    def connectionMade(self):
        """ """
        basic.LineReceiver.connectionMade(self)
        #print '\n + a connection was made'
        #print ' * ',self.transport.getPeer()

    def connectionLost(self, reason):

        if self.isFile:
            basic.LineReceiver.connectionLost(self, reason)
            if self.outfile:
                self.outfile.close()
                # Problem uploading - tmpfile will be discarded
            if self.remain != 0:
                remove_base = '--> removing tmpfile@'
                if self.remain<0:
                    reason = ' .. file moved too much'
                if self.remain>0:
                    reason = ' .. file moved too little'
                #print remove_base + self.outfilename + reason
                os.remove(self.outfilename)
            else:
                if ".enc" in self.outfilename:
                    fileCrypto.decrypt_file('somekey', self.outfilename)
                    os.remove(self.outfilename)
        # Else: Success uploading - tmpfile will be saved to disk.
        # else:
        #     #print '\n--> finished saving upload@' + self.outfilename
        #     print 'finished saving upload'


def fileinfo(fname):
    """ when "file" tool is available, return it's output on "fname" """
    return ( os.system('file 2> /dev/null')!=0 and \
             os.path.exists(fname) and \
             os.popen('file "'+fname+'"').read().strip().split(':')[1] )


class FileIOClient(basic.LineReceiver):
    """ file sender """

    def __init__(self, path, controller):
        """ """
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
        basic.LineReceiver.connectionLost(self, reason)
        self.infile.close()
        if self.completed:
            self.controller.completed.callback(self.result)
        else:
            self.controller.completed.errback(reason)

class FileIOClientFactory(ClientFactory):
    """ file sender factory """

    protocol = FileIOClient

    def __init__(self, path, controller):
        self.path = path
        if ".enc" not in path:
            fileCrypto.encrypt_file('somekey', self.path)
            self.path = self.path + ".enc"
        self.controller = controller

    def clientConnectionFailed(self, connector, reason):
        ClientFactory.clientConnectionFailed(self, connector, reason)
        self.controller.completed.errback(reason)

    def buildProtocol(self, addr):
        p = self.protocol(self.path, self.controller)
        p.factory = self
        return p


def transmitOne(path, address='localhost', port=1234,):
    """ helper for file transmission """
    if ".enc" not in path:
        fileCrypto.encrypt_file('somekey', path)
        path = path + ".enc"
    controller = type('test',(object,),{'cancel':False, 'total_sent':0,'completed':Deferred()})
    f = FileIOClientFactory(path, controller)
    reactor.connectTCP(address, port, f)
    return controller.completed


class ListenerMachine(ServerFactory):

    protocol = ClientReceiverProtocol

    def __init__(self, filePath, userName, serverPath, listen_port=1235):
        # file path for local machine
        self.dir_path = filePath
        # username for machine
        self.username = userName
        #file path for server machine
        self.server_path = serverPath
        # port to listen on
        self.listen_port = listen_port

