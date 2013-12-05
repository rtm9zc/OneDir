import os, json

from twisted.protocols import basic
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import FileSender
from twisted.internet.defer import Deferred
from twisted.internet import reactor

class TransferCancelled(Exception):
    """ Exception for a user cancelling a transfer """
    pass

class FileIOClient(basic.LineReceiver):
    """ file sender """

    def __init__(self, path, controller):
        """ """
        # print "in FileIOClient"

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
            # print 'FileIOClient._monitor Cancelling'

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
        from twisted.internet.error import ConnectionDone
        basic.LineReceiver.connectionLost(self, reason)
        # print ' - connectionLost\n  * ', reason.getErrorMessage()
        # print ' * finished with',self.path
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
        # print 'in FileIOClientFactory class'
        self.path = path
        self.controller = controller

    def clientConnectionFailed(self, connector, reason):
        """ """
        # print 'client connection failed'
        ClientFactory.clientConnectionFailed(self, connector, reason)
        self.controller.completed.errback(reason)
        #print "end ?"

    def buildProtocol(self, addr):
        """ """
        # print ' + building protocol'
        p = self.protocol(self.path, self.controller)
        p.factory = self
        return p

def sendFile(filePath, address, port):

    controller = type('test',(object,),{'cancel':False, 'total_sent':0,'completed':Deferred()})
    f = FileIOClientFactory(filePath, controller)
    reactor.connectTCP(address, port, f)
    return controller.completed