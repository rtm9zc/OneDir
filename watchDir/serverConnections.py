
from serverClasses import *

from multiprocessing import Process

from binascii import crc32
from optparse import OptionParser
import os, json, pprint, datetime

from twisted.protocols import basic
from twisted.internet import protocol
from twisted.application import service, internet
from twisted.internet.protocol import ServerFactory
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import FileSender
from twisted.internet.defer import Deferred
from twisted.internet import reactor

pp = pprint.PrettyPrinter(indent=1)



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

    def lineReceived(self, line):
        """ """
        print ' ~ lineReceived:\n\t', line
        self.instruction = json.loads(line)
        self.instruction.update(dict(client=self.transport.getPeer().host))
        self.size = self.instruction['file_size']
        self.original_fname = self.instruction.get('original_file_path',
                                                   'not given by client')

        # get username via ip address
        clientUsername = self.factory.retrieveUser(self.transport.getPeer().host)

        # Create the upload directory if not already present
        uploaddir = os.path.join(self.factory.dir_path, clientUsername)

        print " * Using upload dir:",uploaddir
        if not os.path.isdir(uploaddir):
            os.makedirs(uploaddir)

        # Need to change to be able to handle files within subdirectories!!!
        self.outfilename = os.path.join(uploaddir, os.path.basename(self.original_fname))

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
        basic.LineReceiver.connectionMade(self)
        print '\n + a connection was made'
        print ' * ',self.transport.getPeer()

    def connectionLost(self, reason):
        """ """
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
            #reactor.stop()

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


def transmitOne(path, address='localhost', port=1235,):
    """ helper for file transmission """
    controller = type('test',(object,),{'cancel':False, 'total_sent':0,'completed':Deferred()})
    f = FileIOClientFactory(path, controller)
    reactor.connectTCP(address, port, f)
    return controller.completed



class FileIOServerFactory(ServerFactory):
    """ file receiver factory """
    protocol = ServerReceiverProtocol

    def __init__(self, filePath, address='localhost', send_port=1235, listen_port=1234):
        """ """
        # server filepath
        self.dir_path = filePath
        # server address
        self.address_ = address

        self.send_port = send_port
        self.listen_port = listen_port

        self.adminUser = ["admin"]
        self.usersToPW = {"admin": "pw", "alexa": "14"}
        adminMachine = BabyLocalMachine("admin", "1", "localhost", "path")
        self.usersToLM = {"admin": [adminMachine]}


    def sendToMachines(self, address, filepath):
        username = self.retrieveUser(address)
        for machine in self.usersToLM[username]:
            if machine.ipAddress != address:
                print 'address is ', address
                transmitOne(filepath,machine.ipAddress,self.send_port)

    def retrieveUser(self, address):
        for username in self.usersToLM:
            for machine in self.usersToLM[username]:
                if machine.ipAddress == address:
                    return username

    def testSendMachines(self, address):
        print 'in testSendMachines'
        username = self.retrieveUser(address)
        print 'username retrieved is ', username
        for machine in self.usersToLM[username]:
            self.send_file('/Users/alowman/testServer/testfile.rtf','127.0.0.1')

    def send_file(self, filePath, address):
        port = self.send_port
        controller = type('test',(object,),{'cancel':False, 'total_sent':0,'completed':Deferred()})
        f = FileIOClientFactory(filePath, controller)
        reactor.connectTCP(address, port, f)
        return controller.completed

if __name__ == "__main__":

    HOST, PORT = "localhost", 9999

    twisted_server = FileIOServerFactory('/Users/alowman/TestServer')

    # Create the server, binding to localhost on port 9999
    socket_server = ThreadedTCPServer((HOST, PORT), MyTCPHandler)
    server_thread = threading.Thread(target=socket_server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    reactor.listenTCP(twisted_server.listen_port,twisted_server)
    print 'Listening on port',twisted_server.listen_port,'..'
    reactor.run()