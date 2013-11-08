
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

class FileIOProtocol(basic.LineReceiver):
    """ File Receiver """

    class Session(object):
        """ Session object, just a demo """
        def is_invalid(self):
            return False

        def is_stale(self):
            return False

    class Status(object):
        """ Status object.. just a demo """
        def update(self, **kargs):
            """ """
            print '-'*80
            pp.pprint(kargs)

    def __init__(self):
        """ """
        self.session = FileIOProtocol.Session()
        self.status = FileIOProtocol.Status()
        self.outfile = None
        self.remain = 0
        self.crc = 0

    def lineReceived(self, line):
        """ """
        print ' ~ lineReceived:\n\t', line
        #print "0"
        try:
            self.instruction = json.loads(line)
            print "1"
            self.instruction.update(dict(client=self.transport.getPeer().host))
            print "2"
            self.size = self.instruction['file_size']
            self.original_fname = self.instruction.get('original_file_path',
                                                       'not given by client')


            # Create the upload directory if not already present
            uploaddir = line.split()[1]
            print " * Using upload dir:",uploaddir
            if not os.path.isdir(uploaddir):
                os.makedirs(uploaddir)

            self.outfilename = os.path.join(uploaddir, 'data.out')

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

        except ValueError:
            print "not a file"
            self.transport.loseConnection()

    def rawDataReceived(self, data):
        """ """
        if self.remain%10000==0:
            print ' & ',self.remain,'/',self.size
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
        try:
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
                client = self.instruction.get('client', 'anonymous')

                self.status.update( crc = self.crc,
                                    file_size = self.size,
                                    client = client,
                                    new_file = self.outfilename,
                                    original_file = self.original_fname,
                                    file_metadata = fileinfo(self.outfilename),
                                    upload_time = datetime.datetime.now() )
        except AttributeError:
            print "not a file"

def fileinfo(fname):
    """ when "file" tool is available, return it's output on "fname" """
    return ( os.system('file 2> /dev/null')!=0 and \
             os.path.exists(fname) and \
             os.popen('file "'+fname+'"').read().strip().split(':')[1] )


class FileIOFactory(ServerFactory):
    """ file receiver factory """
    protocol = FileIOProtocol

    def __init__(self, db, options={}):
        """ """
        self.db = db
        self.options = options