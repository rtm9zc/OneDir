__author__ = 'Student'

from twisted.spread import pb
from twisted.internet import reactor
from file_transfer import *
from binascii import crc32


class LocalMachine():

    def __init__(self, username, filePath, address='localhost', port=1234):
        self.username_ = username
        self.file_path_ = filePath
        self.address_ = address
        self.port_ = port

    def sendFile(self, fileName):
        # transmitOne(self.file_path_,self.address_,self.port_)
        # print 'Dialing on port',self.port_,'..'
        # reactor.run()
        command = 'python ~/PycharmProjects/OneDir/fileTransferServerAndClient.py --client ' + self.file_path_ + '/' + filename
        os.system(command)

    def getUsername(self):
        return self.username_

    def getAddress(self):
        return self.address_

# if __name__=='__main__':
#     filename = 'testfile.docx'
#     lm_one = LocalMachine('testUser', '/test_user/machineOne/OneDir', address='localhost', port=1234)
#     lm_one.sendFile(filename)

if __name__=='__main__':
    filename = 'testfile.docx'
    lm_one = LocalMachine('testUser', '~/test_user/machineOne/OneDir', address='localhost', port=1234)
    lm_one.sendFile(filename)