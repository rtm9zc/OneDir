from twisted.internet import reactor, protocol

class Test(protocol.Protocol):

    def dataReceived(self, data):
        "Ass soon as any data is received, write it back."
        self.transport.write(data)

def main():
    """This runs the protocol on port 8000"""
    factory = protocol.ServerFactory()
    factory.protocol = Test
    reactor.listenTCP(8000,factory)
    reactor.run()

if __name__ == '__main__':
    main()