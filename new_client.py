#from new_file_transfer import *
#from new_server import *
from binascii import crc32
import os
import json
import pprint

from twisted.protocols import basic
from twisted.internet.protocol import ServerFactory
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import FileSender
from twisted.internet.defer import Deferred
from twisted.internet import reactor

from watchDir.sendingClient import LocalMachine


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

    def lineReceived(self, line):
        """ """
        print ' ~ lineReceived:\n\t', line
        self.instruction = json.loads(line)
        self.instruction.update(dict(client=self.transport.getPeer().host))
        self.size = self.instruction['file_size']
        self.original_fname = self.instruction.get('original_file_path',
                                                   'not given by client')

        # Create the upload directory if not already present
        uploaddir = self.factory.dir_path
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

                print '\n--> finished saving upload@' + self.outfilename
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


def transmitOne(path, address='localhost', port=1234,):
    """ helper for file transmission """
    controller = type('test',(object,),{'cancel':False, 'total_sent':0,'completed':Deferred()})
    f = FileIOClientFactory(path, controller)
    reactor.connectTCP(address, port, f)
    return controller.completed


class LocalMachine(ServerFactory):

    protocol = ClientReceiverProtocol

    def __init__(self, username, filePath, address='localhost', send_port=1234, listen_port=1235):
        # username associated with the local machine
        self.username_ = username
        # file path for local machine
        self.dir_path = filePath
        self.address_ = address

        self.send_port = send_port
        self.listen_port = listen_port

        self.isServer = False

        #reactor.listenTCP(listen_port, self)
        #reactor.run()

    def send_file(self, filePath):
        # send to server (aka on my laptop)
        #transmitOne(filePath,'137.54.51.83',self.send_port)
        #transmitOne(filePath,port=self.send_port,address='localhost')
        #transmitOne(filePath, 'localhost',self.send_port)
        #address = 'localhost'
        address = '127.0.0.1'
        port = self.send_port
        controller = type('test',(object,),{'cancel':False, 'total_sent':0,'completed':Deferred()})
        f = FileIOClientFactory(filePath, controller)
        reactor.connectTCP(address, port, f)
        return controller.completed

    #def test_handler(self):


    def get_user(self):
        return self.username_

    def get_address(self):
        return self.address_

    def get_filepath(self):
        return self.dir_path

    def get_listenport(self):
        return self.listen_port

    def get_sendport(self):
        return self.send_port


def doEverything():
    lm = LocalMachine('testUser', '/home/student/pycharm-community-3.0.1/OneDir/test_user/test.txt', address='localhost')
    reactor.listenTCP(lm_one.listen_port, lm_one)
    print 'Listening on port',lm_one.listen_port,'..'
    #lm_one.send_file('/Users/alowman/test_user/machineOne/OneDir/testfile.docx')
    reactor.run()

if __name__ == "__main__":

    # my laptop
    #lm_one = LocalMachine('KingGeorge', '~/test_user/machineOne/OneDir', address='137.54.49.223', send_port=1234, listen_port=1235)
    lm_one = LocalMachine('KingGeorge', '/Users/alowman/test_user/machineOne/OneDir', address='127.0.0.1', send_port=1234, listen_port=1235)

    # lab desktop
    #lm_two = LocalMachine('KingGeorge', '~/home/ajl3mp/OneDir', address='128.143.63.86', send_port=1234, listen_port=1235)


    #reactor.listenTCP(lm_one.listen_port, lm_one)
    #reactor.listenTCP(lm_two.listen_port, lm_two)
    #print 'Listening on port',lm_one.listen_port,'..'
    # print 'Listening on port',lm_two.listen_port,'..'

    #p = Process(target=reactor.run)
    #p.start()

    #p2 = Process(target=lm_one.send_file('~/test_user/machineOne/OneDir/testfile.docx'))
    #p2.start()

    # if event occurs:

    lm = LocalMachine('testUser', '/home/student/pycharm-community-3.0.1/OneDir/test_user/test.txt', address='localhost')
    reactor.listenTCP(lm_one.listen_port, lm_one)
    print 'Listening on port',lm_one.listen_port,'..'
    #lm_one.send_file('/Users/alowman/test_user/machineOne/OneDir/testfile.docx')
    reactor.run()
