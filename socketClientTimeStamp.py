__author__ = 'student'

#!/usr/bin/env python

from socket import *

HOST = 'localhost'
PORT = 21567
BUFSIZ = 1024
ADDR = (HOST, PORT)

tcpCliSock = socket(AF_INET, SOCK_STREAM)
tcpCliSock.connect(ADDR)

while 1:
    data = raw_input('> ')
    if not data: break
    tcpCliSock.send(data)
    data = tcpCliSock.recv(1024)
    if not data: break
    print data

tcpCliSock.close()