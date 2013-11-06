__author__ = 'Student'

from twisted.spread import pb
from twisted.internet import reactor
from file_transfer import *
from binascii import crc32
import sys
import time
import logging
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import thread

import pickle
from socket import *


class LocalMachine():

    def __init__(self, username, filePath, address='localhost', port=1234):
        self.username_ = username
        self.file_path_ = filePath
        self.address_ = address
        self.port_ = port

    def sendFile(self, fileName):
        transmitOne(self.file_path_,self.address_,self.port_)
        print 'Dialing on port',self.port_,'..'
        reactor.run()

    def sendArray(self, array):
        host = "localhost"
        port = self.port
        buf = 4096
        addr = (host,port)

        # Create socket
        UDPSock = socket(AF_INET,SOCK_DGRAM)

        a = self.array

        # Send the array
        while (1):
            if(UDPSock.sendto( pickle.dumps(a), addr)):
                print "Sending message"
                break

    # Close socket
    UDPSock.close()



    def getUsername(self):
        return self.username_

    def getAddress(self):
        return self.address_

    #These will be only called from the OneDirHandler
    #Will be handled by a listener method on the server
    def moved(self, source, destination):
        self.sendString(self.username_ + " " + self.address_ + " mov " + source + " " + destination)
        #some shit to listen for a confirming response
    def deleted(self, file):
        self.sendString(self.username_ + " " + self.address_ + " del " + file)
        #some shit to listen for a confirming response
    def modified(self, file):
        self.sendString(self.username_ + " " + self.address_ + " mod " + file)
        #some shit to listen for a confirming response
        self.sendFile(file)
    def created(self, file):
        self.sendString(self.username_ + " " + self.address_ + " cre " + file)
        #some shit to listen for a confirming response
        self.sendFile(file)

class OneDirHandler(FileSystemEventHandler, ):
    localstring = (str)
    localstring = os.getcwd()
    locallen = localstring.__len__()+1
    machine = (LocalMachine)
    def __init__(self, local):
        machine = local
    def on_moved(self, event):
        #Only really called on name change
        #Should tell server to change name on file (src_path) to (dest_path)
        source = event.src_path[self.locallen:]
        dest = event.dest_path[self.locallen:]
        if (source.find(".git") == -1 and source.find(".idea") == -1):
            print("File moved! (" + source + " at time: " +
              time.strftime("%Y-%m-%d %H:%M:%S")+ ")")
            print("Destination: " + dest)
            thread.start_new_thread(self.machine.moved(source, dest))
    def on_created(self, event):
        #Called on making new file
        #Should send file over to server
        source = event.src_path[self.locallen:]
        if (source.find(".git") == -1 and source.find(".idea") == -1):
            print("File created! (" + source + " at time: " +
              time.strftime("%Y-%m-%d %H:%M:%S")+ ")")
            thread.start_new_thread(self.machine.created(source))
    def on_deleted(self, event):
        #Called on deletion of file/directory
        #Server should delete same file
        source = event.src_path[self.locallen:]
        if (source.find(".git") == -1 and source.find(".idea") == -1):
            print("File deleted! (" + source + " at time: " +
              time.strftime("%Y-%m-%d %H:%M:%S")+ ")")
            thread.start_new_thread(self.machine.deleted(source))
    def on_modified(self, event):
        source = event.src_path[self.locallen:]
        if (source.find(".git") == -1 and source.find(".idea") == -1):
            print("File modified! (" + source + " at time: " +
              time.strftime("%Y-%m-%d %H:%M:%S")+ ")")
            thread.start_new_thread(self.machine.modified(source))

if __name__ == "__main__":
    lm_one = LocalMachine('testUser', '~/test_user/machineOne/OneDir', address='localhost', port=1234)
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = OneDirHandler(lm_one)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()