__author__ = 'student'

#!/usr/bin/env python


from socket import *
from time import time, ctime

HOST = ''
PORT = 21567
BUFSIZ = 1024
ADDR = (HOST, PORT)

tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind(ADDR)
tcpSerSock.listen(5)

while 1:
    print 'waiting for connection...'
    tcpCliSock, addr = tcpSerSock.accept()
    print '...connected from: ', addr

    while 1:
        data = tcpCliSock.recv(BUFSIZ)
        if not data: break
        tcpCliSock.send('[%s] %s' % (ctime(time()), data))

    tcpCliSock.close()

tcpSerSock.close()
