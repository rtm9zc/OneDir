


import SocketServer
import os



class BabyLocalMachine():

    def __init__(self, username, macAddress, ipAddress, pathToDirectory, port=1235):
        self.username = username
        self.macAddress = macAddress
        self.ipAddress = ipAddress
        self.pathToDirectory = pathToDirectory
        self.port = port


class MyTCPHandler(SocketServer.BaseRequestHandler):

    #override the handle method to allow for back and forth communication
    def handle(self):
        # self.request is the TCP socket connected to the client



        self.usertype = self.request.recv(1024).strip()
        self.usertype = str(self.usertype)
        booleanVal = "True"
        self.request.sendall(booleanVal + "\n")

        self.username = self.request.recv(1024).strip()
        self.username = str(self.username)
        self.request.sendall(booleanVal + "\n")

        self.password = self.request.recv(1024).strip()
        self.password = str(self.password)


        if (self.usertype == "newuser"):
            self.usersToPW[self.username] = self.password
            self.usersToLM[self.username] = []

            # ADD USERNAME DIRECTORY TO SERVER DIRECTORY os.makedirs(self.username)

        print self.usersToPW[self.username]
        if self.password == self.usersToPW[self.username]:
            correctUserandPW = "True"
        else:
            correctUserandPW = "False"

        self.request.sendall(correctUserandPW + "\n")

        if correctUserandPW == "True":

            self.macAddress = self.request.recv(1024).strip()
            self.macAddress = str(self.macAddress)

            isLocalMachine = "False"
            for localM in self.usersToLM[self.username]:
                if self.macAddress == localM.macAddress:
                    isLocalMachine = "True"

            self.request.sendall(isLocalMachine + "\n")

            if isLocalMachine == "False":
                filePath = self.request.recv(1024).strip()
                filePath = str(filePath)
                self.request.sendall(booleanVal + "\n")

                #REPLACE WITH THE IP ADDRESS OF THE LOCAL MACHINE
                lm = BabyLocalMachine(self.username, self.macAddress, 548973759, filePath)
                self.usersToLM[self.username].append(lm)















if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()