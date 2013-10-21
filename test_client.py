from twisted.internet import reactor, protocol

class TestClient(protocol.Protocol):

    def connectionMade(self):
        self.transport.write("this is a test")

    def dataReceived(self, data):
        "As soon as any data is received, write it back."
        print "Server received the following data:", data
        self.transport.loseConnection()

    def connectionLost(self, reason):
        print "connection lost"

class TestFactory(protocol.ClientFactory):
    protocol = TestClient

    def clientConnectionFailed(self, connector, reason):
        print "Connection has failed!"
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print "Connection has been lost!"
        reactor.stop()

def main():
    f = TestFactory()
    reactor.connectTCP("localhost", 8000, f)
    reactor.run()

if __name__ == '__main__':
    main()
