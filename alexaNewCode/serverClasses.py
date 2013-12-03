import os
import SocketServer
import shutil

def getExtension(filename):
    return os.path.splitext(filename)[-1].lower()

class BabyLocalMachine():

    def __init__(self, username, macAddress, ipAddress, pathToDirectory, port=1235):
        self.username = username
        self.macAddress = macAddress
        self.ipAddress = ipAddress
        self.pathToDirectory = pathToDirectory
        self.port = port
        self.syncState = True

class ThreadedTCPServer(SocketServer.ThreadingTCPServer):

    def __init__(self, server_address, HandlerClass, twisted_server):
        self.allow_reuse_address = True
        SocketServer.ThreadingTCPServer.__init__(self, server_address, HandlerClass)
        self.twisted_server = twisted_server


class MyTCPHandler(SocketServer.BaseRequestHandler):

    def allAdminFiles(self, path): #returns a string with all
                      #subdirectories, files, and sizes under path
        outstring = ''
        users = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
        outstring = outstring + "Users: \n"
        for name in users:
            numFiles = 0
            totalBytes = 0
            outstring = outstring + "\n" + os.path.basename(name) + "\n"
            for root, subdirs, files in os.walk(os.path.join(path,name)):
                for fname in files:
                    fullPath = os.path.join(root, fname)
                    fileSize = str(os.path.getsize(fullPath))
                    outstring = outstring + fname + "\t" + fileSize + " bytes \n"
                    numFiles = numFiles + 1
                    totalBytes = totalBytes + os.path.getsize(fullPath)
            outstring = outstring + "Total number of files for user: " + str(numFiles) + "\n"
            outstring = outstring + "Total size of files (bytes) for user: " + str(totalBytes) + "\n"
        return outstring

    def userAdminFiles(self, path, username): #returns a string with all
                      #subdirectories, files, and sizes under path
        outstring = "User: " + username + "\n"
        numFiles = 0
        totalBytes = 0
        for root, subdirs, files in os.walk(os.path.join(path,username)):
            for fname in files:
                fullPath = os.path.join(root, fname)
                fileSize = str(os.path.getsize(fullPath))
                outstring = outstring + fname + "\t" + fileSize + " bytes \n"
                numFiles = numFiles + 1
                totalBytes = totalBytes + os.path.getsize(fullPath)
        outstring = outstring + "Total number of files for user: " + str(numFiles) + "\n"
        outstring = outstring + "Total size of files (bytes) for user: " + str(totalBytes) + "\n"
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

        correctUserandPW = "NA"


        if self.usertype == "newuser":

            if self.username in self.server.twisted_server.usersToPW:
                correctUserandPW = "Invalid"
            else:
                self.server.twisted_server.usersToPW[self.username] = self.password
                print self.server.twisted_server.usersToPW
                self.server.twisted_server.usersToLM[self.username] = []

        if correctUserandPW != "Invalid":

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
                    files = self.allAdminFiles(self.server.twisted_server.dir_path)
                    self.request.sendall(files + "\n")
                if (self.adminUserRequest == "3"):
                    self.request.sendall(trueResponse + "\n")
                    userToPrint = self.request.recv(1024).strip()
                    userToPrint = str(userToPrint)
                    files = self.userAdminFiles(self.server.twisted_server.dir_path, userToPrint)
                    self.request.sendall(files + "\n")
                if (self.adminUserRequest == "4"):
                    self.request.sendall(trueResponse + "\n")
                    usernameToDelete = self.request.recv(1024).strip()
                    usernameToDelete = str(usernameToDelete)
                    del self.server.twisted_server.usersToPW[usernameToDelete]
                    del self.server.twisted_server.usersToLM[usernameToDelete]
                    #DELETE THE FILES ASSOCIATED WITH THIS USERNAME ON THE SERVER SIDE

                    for root, dirs, files in os.walk(os.path.join(self.server.twisted_server.dir_path, usernameToDelete)):
                        for f in files:
    	                    os.unlink(os.path.join(root, f))
                        for d in dirs:
    	                    shutil.rmtree(os.path.join(root, d))
                    os.rmdir(os.path.join(self.server.twisted_server.dir_path, usernameToDelete))

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
                    self.request.sendall(adminResults + "\n")