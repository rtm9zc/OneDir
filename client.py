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

    def sendString(self, string):
        #some stuff to send a formatted string to the server
        print(string)
    def getUsername(self):
        return self.username_

    def getAddress(self):
        return self.address_

    def moved(self, source, destination):
        self.sendString("mov " + source + " " + destination)
        #some shit to listen for a confirming response
    def deleted(self, file):
        self.sendString("del " + file)
        #some shit to listen for a confirming response
    def modified(self, file):
        self.sendString("mod " + file)
        #some shit to listen for a confirming response
        self.sendFile(file)
    def created(self, file):
        self.sendString("cre " + file)
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