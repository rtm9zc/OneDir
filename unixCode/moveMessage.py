
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
        self.sendLine(self.path)

    def connectionLost(self, reason):
        """
            NOTE: reason is a twisted.python.failure.Failure instance
        """
        from twisted.internet.error import ConnectionDone
        basic.LineReceiver.connectionLost(self, reason)
        # print ' - connectionLost\n  * ', reason.getErrorMessage()
        # print ' * finished with',self.path
        reactor.stop()

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

def sendMessage(filePath, address, port):
    controller = type('test',(object,),{'cancel':False, 'total_sent':0,'completed':Deferred()})
    f = FileIOClientFactory(filePath, controller)
    reactor.connectTCP(address, port, f)
    return controller.completed