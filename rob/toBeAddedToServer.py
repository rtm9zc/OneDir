


import SocketServer
import os



class BabyLocalMachine():

    def __init__(self, username, macAddress, ipAddress, pathToDirectory, port=1235):
        self.username = username
        self.macAddress = macAddress
        self.ipAddress = ipAddress
        self.pathToDirectory = pathToDirectory
        self.port = port

adminUser = ["admin"]
usersToPW = {"admin": "pw", "julie": "1"}
usersToLM = {"admin": "pw", "julie": "1"}

class MyTCPHandler(SocketServer.BaseRequestHandler):

    #override the handle method to allow for back and forth communication
    def handle(self):
        # self.request is the TCP socket connected to the client

        global adminUser
        global usersToPW
        global usersToLM

        self.usertype = self.request.recv(1024).strip()
        self.usertype = str(self.usertype)
        booleanVal = "True"
        self.request.sendall(booleanVal + "\n")

        self.username = self.request.recv(1024).strip()
        self.username = str(self.username)
        isAdminUser = "False"
        if self.username in adminUser:
            isAdminUser = "True"
        self.request.sendall(isAdminUser + "\n")

        self.password = self.request.recv(1024).strip()
        self.password = str(self.password)


        if (self.usertype == "newuser"):
            usersToPW[self.username] = self.password
            usersToLM[self.username] = []
            print usersToPW

            # ADD USERNAME DIRECTORY TO SERVER DIRECTORY os.makedirs(self.username)


        if self.password == usersToPW[self.username]:
            correctUserandPW = "True"
        else:
            correctUserandPW = "False"

        self.request.sendall(correctUserandPW + "\n")


        if correctUserandPW == "True" and isAdminUser == "False":


            self.macAddress = self.request.recv(1024).strip()
            self.macAddress = str(self.macAddress)

            isLocalMachine = "False"
            for localM in usersToLM[self.username]:
                if self.macAddress == localM.macAddress:
                    isLocalMachine = "True"

            self.request.sendall(isLocalMachine + "\n")

            if isLocalMachine == "False":
                filePath = self.request.recv(1024).strip()
                filePath = str(filePath)
                self.request.sendall(booleanVal + "\n")

                #REPLACE WITH THE IP ADDRESS OF THE LOCAL MACHINE
                lm = BabyLocalMachine(self.username, self.macAddress, 548973759, filePath)
                usersToLM[self.username].append(lm)

        if isAdminUser == "True" and correctUserandPW == "True":



            self.adminUserRequest = "1"

            while (self.adminUserRequest != "0"):

                self.adminUserRequest = self.request.recv(1024).strip()
                self.adminUserRequest = str(self.adminUserRequest)

                trueResponse = "True"
                print self.adminUserRequest

                if (self.adminUserRequest == "1"):
                    adminResults = str(usersToPW)
                    self.request.sendall(adminResults + "\n")
                if (self.adminUserRequest == "2"):
                    #number of total files and filesizes stored as a string and put into self.adminResults
                    self.request.sendall(adminResults + "\n")
                if (self.adminUserRequest == "3"):
                    #number of per user total files and filesizes stored as a string and put into self.adminResults
                    self.request.sendall(adminResults + "\n")
                if (self.adminUserRequest == "4"):
                    self.request.sendall(trueResponse + "\n")
                    usernameToDelete = self.request.recv(1024).strip()
                    usernameToDelete = str(usernameToDelete)
                    del usersToPW[usernameToDelete]
                    del usersToLM[usernameToDelete]
                    #DELETE THE FILES ASSOCIATED WITH THIS USERNAME ON THE SERVER SIDE
                    self.request.sendall(trueResponse + "\n")
                if (self.adminUserRequest == "5"):
                    self.request.sendall(trueResponse + "\n")
                    usernameToDelete = self.request.recv(1024).strip()
                    usernameToDelete = str(usernameToDelete)
                    del usersToPW[usernameToDelete]
                    del usersToLM[usernameToDelete]
                    print str(usersToPW)
                    print str(usersToLM)
                    self.request.sendall(trueResponse + "\n")
                if (self.adminUserRequest == "6"):
                    self.request.sendall(trueResponse + "\n")
                    usernameToChangePW = self.request.recv(1024).strip()
                    usernameToChangePW = str(usernameToChangePW)

                    self.request.sendall(trueResponse + "\n")
                    passwordToChange = self.request.recv(1024).strip()
                    passwordToChange = str(passwordToChange)
                    usersToPW[usernameToChangePW] = passwordToChange
                    print str(usersToPW)
                    self.request.sendall(trueResponse + "\n")
                if (self.adminUserRequest == "7"):
                    #get history of connections involving synchronization stored as a string and put into self.adminResults
                    self.request.sendall(adminResults + "\n")



















if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()