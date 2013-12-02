import os
import SocketServer
import socket
import threading

class BabyLocalMachine():

    def __init__(self, username, macAddress, ipAddress, pathToDirectory, port=1235):
        self.username = username
        self.macAddress = macAddress
        self.ipAddress = ipAddress
        self.pathToDirectory = pathToDirectory
        self.port = port

class ThreadedTCPServer(SocketServer.ThreadingTCPServer):

    def __init__(self, server_address, HandlerClass, twisted_server):
        self.allow_reuse_address = True
        SocketServer.ThreadingTCPServer.__init__(self, server_address, HandlerClass)
        self.twisted_server = twisted_server


class MyTCPHandler(SocketServer.BaseRequestHandler):

    def adminFiles(path): #returns a string with all
                      #subdirectories, files, and sizes under path
        outstring = ''
        totalsize = 0
        for dirname, dirnames, filenames in os.walk(path):
            # print path to all subdirectories first.
            outstring = outstring + "Subdirectories: \n"
            for subdirname in dirnames:
                outstring = outstring + os.path.join(dirname, subdirname) + '\n'
            outstring = outstring + "\nFiles: \n"
            # print path to all filenames.
            for filename in filenames:
                outstring = outstring + os.path.join(dirname, filename) + '\n'
                outstring = outstring + "Size (bytes): " + str(os.path.getsize(filename)) +'\n'
                totalsize += os.path.getsize(filename)
        outstring = outstring + "\nTotal size (bytes): " + str(totalsize)
        return outstring

    #override the handle method to allow for back and forth communication
    def handle(self):
        # self.request is the TCP socket connected to the client


        self.usertype = self.request.recv(1024).strip()
        self.usertype = str(self.usertype)
        booleanVal = "True"
        self.request.sendall(booleanVal + "\n")

        self.username = self.request.recv(1024).strip()
        self.username = str(self.username)
        isAdminUser = "False"
        if self.username in self.server.twisted_server.adminUser:
            isAdminUser = "True"
        self.request.sendall(isAdminUser + "\n")

        self.password = self.request.recv(1024).strip()
        self.password = str(self.password)


        if self.usertype == "newuser":
            self.server.twisted_server.usersToPW[self.username] = self.password
            print self.server.twisted_server.usersToPW
            self.server.twisted_server.usersToLM[self.username] = []
            print self.server.twisted_server.usersToPW

            # create new user directory
            #os.makedirs(os.path.join(self.server.twisted_server.dir_path, self.username))


        if self.password == self.server.twisted_server.usersToPW[self.username]:
            correctUserandPW = "True"
        else:
            correctUserandPW = "False"

        self.request.sendall(correctUserandPW + "\n")

        if correctUserandPW == "True":
            self.newPW =  self.request.recv(1024).strip()
            self.newPW = str(self.newPW)
            if self.newPW != "N":
                self.server.twisted_server.usersToPW[self.username] = self.newPW
                print self.server.twisted_server.usersToPW

            booleanVal = "True"
            self.request.sendall(booleanVal + "\n")


        if correctUserandPW == "True" and isAdminUser == "False":


            self.macAddress = self.request.recv(1024).strip()
            self.macAddress = str(self.macAddress)

            isLocalMachine = "False"
            for localM in self.server.twisted_server.usersToLM[self.username]:
                if self.macAddress == localM.macAddress:
                    isLocalMachine = localM.pathToDirectory
                    localM.ipAddress = self.client_address[0]

            self.request.sendall(isLocalMachine + "\n")

            if isLocalMachine == "False":
                filePath = self.request.recv(1024).strip()
                filePath = str(filePath)
                self.request.sendall(booleanVal + "\n")

                lm = BabyLocalMachine(self.username, self.macAddress, self.client_address[0], filePath)
                self.server.twisted_server.usersToLM[self.username].append(lm)
                os.makedirs(os.path.join(self.server.twisted_server.dir_path, self.username))


        if isAdminUser == "True" and correctUserandPW == "True":


            self.adminUserRequest = "1"

            while (self.adminUserRequest != "0"):

                self.adminUserRequest = self.request.recv(1024).strip()
                self.adminUserRequest = str(self.adminUserRequest)

                trueResponse = "True"
                print self.adminUserRequest

                if (self.adminUserRequest == "1"):
                    adminResults = str(self.server.twisted_server.usersToPW)
                    self.request.sendall(adminResults + "\n")
                if (self.adminUserRequest == "2"):
                    files = adminFiles("SERVER PATH")
                    self.request.sendall(files + "\n")
                if (self.adminUserRequest == "3"):
                    #number of per user total files and filesizes stored as a string and put into self.adminResults
                    files = adminFiles("SERVER PATH")
                    self.request.sendall(files + "\n")
                if (self.adminUserRequest == "4"):
                    self.request.sendall(trueResponse + "\n")
                    usernameToDelete = self.request.recv(1024).strip()
                    usernameToDelete = str(usernameToDelete)
                    del self.server.twisted_server.usersToPW[usernameToDelete]
                    del self.server.twisted_server.usersToLM[usernameToDelete]
                    #DELETE THE FILES ASSOCIATED WITH THIS USERNAME ON THE SERVER SIDE
                    self.request.sendall(trueResponse + "\n")
                if (self.adminUserRequest == "5"):
                    self.request.sendall(trueResponse + "\n")
                    usernameToDelete = self.request.recv(1024).strip()
                    usernameToDelete = str(usernameToDelete)
                    del self.server.twisted_server.usersToPW[usernameToDelete]
                    del self.server.twisted_server.usersToLM[usernameToDelete]
                    print str(self.server.twisted_server.usersToPW)
                    print str(self.server.twisted_server.usersToLM)
                    self.request.sendall(trueResponse + "\n")
                if (self.adminUserRequest == "6"):
                    self.request.sendall(trueResponse + "\n")
                    usernameToChangePW = self.request.recv(1024).strip()
                    usernameToChangePW = str(usernameToChangePW)

                    self.request.sendall(trueResponse + "\n")
                    passwordToChange = self.request.recv(1024).strip()
                    passwordToChange = str(passwordToChange)
                    self.server.twisted_server.usersToPW[usernameToChangePW] = passwordToChange
                    print str(self.server.twisted_server.usersToPW)
                    self.request.sendall(trueResponse + "\n")
                if (self.adminUserRequest == "7"):
                    #get history of connections involving synchronization stored as a string and put into self.adminResults
                    with open ("log.txt", "r") as myfile:
                        adminResults=myfile.read().replace('\n', '')
                    self.request.sendall(adminResults + "\n")