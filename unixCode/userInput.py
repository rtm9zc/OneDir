import os
import sys
import socket
from uuid import getnode as get_mac
import time

from multiprocessing import Process
from new_client import *
from watchDir import OneDir_Observer
from sendingClient import LocalMachine

HOST, PORT = str(sys.argv[1]), 9999
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.connect((HOST, PORT))

syncState = 'on'
filePath = 'False'
userName = 'user'

watchMachine = LocalMachine('TestUser', 'TestDirectory', HOST)
OneDog = OneDir_Observer(watchMachine)
listenMachine = ListenerMachine('TestDirectory', 'TestUser', str(sys.argv[2]), listen_port=1235)

watch_process = Process(target=OneDog.startWatching)

def sendData(userType, username, password):
    #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    # Connect to server and send data
    #sock.connect((HOST, PORT))

    global filePath
    global userName

    sock.sendall(usertype + "\n")
    response1 = sock.recv(1024)

    sock.sendall(username + "\n")
    isAdminUser = sock.recv(1024)
    isAdminUser = str(isAdminUser).strip()

    sock.sendall(password + "\n")
    correctUsernameAndPassword = sock.recv(1024)
    correctUsernameAndPassword = str(correctUsernameAndPassword).strip()

    if correctUsernameAndPassword == "True":
        newPW = raw_input("Would you like to change your password (if yes enter the new password and if no enter N)?: ")

        sock.sendall(newPW + "\n")
        sock.recv(1024)
        if newPW != "N":
            print "Changed your password to: " + newPW




    if correctUsernameAndPassword == "True" and isAdminUser == "False":

        mac = get_mac()
        mac = str(mac)
        sock.sendall(mac +"\n")
        filePath = sock.recv(1024)
        filePath = str(filePath).strip()

        if filePath == "False":
            filePath = raw_input("Enter the new filepath where you would like your OneDir folder to be stored: ")
            sock.sendall(filePath + "\n")
            response1 = sock.recv(1024)

            os.mkdir(filePath)


    #sock.close()

    return {"correctUsernameAndPassword" : correctUsernameAndPassword, "isAdminUser" : isAdminUser, "filePath" : filePath}


def adminInput():
    adminChoiceNum = "1"
    while adminChoiceNum != "0":

        adminChoiceNum = raw_input("Enter 1 if you would like to view all usernames and passwords, \n"
                             "Enter 2 if you would like to see info about the number and size of files for all users \n"
                             "Enter 3 if you would like to see info about the number and size of files for a given user \n"
                             "Enter 4 if you would like to remove a user's account and their files \n"
                             "Enter 5 if you would like to remove a user's account but not their files \n"
                             "Enter 6 if you would like to change a user's password \n"
                             "Enter 7 if you would like to view a history of connections involving synchronization \n"
                             "Enter 0 if you are finished and want to exit \n")
        adminChoiceNum = str(adminChoiceNum).strip()
        #adminSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Connect to server and send data
            #adminSock.connect((HOST, PORT))

            sock.sendall(adminChoiceNum + "\n")
            print "sent"
            adminResults = sock.recv(65536)
            #adminResults = sock.recv()
            print "received"
            adminResults = str(adminResults).strip()

            if adminChoiceNum == "3":
                userToPrint = raw_input("Enter the username you would like info about: ")
                userToPrint = str(userToPrint).strip()
                sock.sendall(userToPrint + "\n")
                adminResults = sock.recv(65536)
                adminResults = str(adminResults).strip()

            if adminChoiceNum == "4" or adminChoiceNum == "5":
                accountToDelete = raw_input("Enter the username for the account you wish to delete: ")
                accountToDelete = str(accountToDelete).strip()
                sock.sendall(accountToDelete + "\n")
                adminResults = sock.recv(65536)
                adminResults = str(adminResults).strip()

            if adminChoiceNum == "6":
                usernameForPWChange = raw_input("Enter the username for the account for which you wish to change the password: ")
                usernameForPWChange = str(usernameForPWChange).strip()
                sock.sendall(usernameForPWChange + "\n")
                adminResults = sock.recv(65536)

                passwordForPWChange = raw_input("Enter the new password for the account you wish to change: ")
                passwordForPWChange = str(passwordForPWChange).strip()
                sock.sendall(passwordForPWChange + "\n")
                adminResults = sock.recv(65536)

                adminResults = str(adminResults).strip()


        finally:
            print adminResults
            #sock.close()



def syncOptions(currentState):

    global watch_process

    if currentState == "on":
        syncResponse = raw_input("Synchronization is on. \nTo turn sync off, enter yes.\nTo log out, enter quit.\n")

        if syncResponse == 'yes':
            message = "syncOff"
            #p = Process(target=moveMessage.sendMessage, args=(message, HOST, watchMachine.port,))
            #p.start()
            watchMachine.sendMessage(message)
            watch_process.terminate()
            syncState = "off"

        if syncResponse == 'quit':
            message = "syncOff"
            watchMachine.sendMessage(message)
            watch_process.terminate()
            listen_process.terminate()
            #sys.exit(0)
            os.system("pkill python")

    if currentState == "off":
        syncResponse = raw_input("Synchronization is off. \nTo turn sync on, enter yes.\nTo log out, enter quit.\n")

        if syncResponse == 'yes':
            message = "syncOn"
            watchMachine.sendMessage(message)
            watch_process = Process(target=OneDog.startWatching)
            watch_process.start()
            syncState = "on"

        if syncResponse == 'quit':
            message = "syncOff"
            watchMachine.sendMessage(message)
            listen_process.terminate()
            #sys.exit(0)
            os.system("pkill python")


    return syncState

# add server IP Address as a command line argument

if __name__ == "__main__":


    syncState = "on"

    #global watchMachine
    #global listenMachine

    usertype = raw_input("Enter 1 if you are a new user and 2 if you are a returning user: ")

    if usertype == "1":
        usertype = "newuser"
        newUsername = raw_input("Please enter the new username: ")
        newPassword = raw_input("Please enter the new password: ")

        userName = newUsername

        #send a newuser marker to the server
        dictFromInput = sendData(usertype, newUsername, newPassword)

        isAdminUser = dictFromInput["isAdminUser"]
        correctEntry = dictFromInput["correctUsernameAndPassword"]

        if correctEntry == "Invalid":
            print "This username already exists."
            #sys.exit(0)
            os.system("pkill python")

        filePath = dictFromInput["filePath"]

        # change for whatever user / file path is acquired above
        watchMachine.oneDir = dictFromInput["filePath"]
        watchMachine.username = userName

        watch_process.start()

        # port = whichever port we determine will be the client listening port (1235?)
        listenMachine.dir_path = filePath
        listenMachine.username = userName
        reactor.listenTCP(listenMachine.listen_port, listenMachine)

        listen_process = Process(target=reactor.run)
        listen_process.start()


        while True:
            syncState = syncOptions(syncState)

    else:
        usertype = "olduser"
        returningUsername = raw_input("Please enter your username: ")
        returningPassword = raw_input("Please enter your password: ")

        userName = returningUsername

        #if it matches the information found on the server: run clientMain.py and new_client.py

        #send the server a returning user marker
        dictFromInput = sendData(usertype, returningUsername, returningPassword)

        isAdminUser = dictFromInput["isAdminUser"]
        correctEntry = dictFromInput["correctUsernameAndPassword"]
        filePath = dictFromInput["filePath"]

        if (isAdminUser == "True" and correctEntry == "True"):
            adminInput()

        if (isAdminUser == "False" and correctEntry == "True"):

            # change for whatever user / file path is acquired above
            watchMachine.oneDir = filePath
            watchMachine.username = userName
            OneDog.lm.oneDir = filePath
            OneDog.lm.username = userName

            message = "syncOn"
            watchMachine.sendMessage(message)

            watch_process.start()

            # port = whichever port we determine will be the client listening port (1235?)
            listenMachine.dir_path = filePath
            listenMachine.username = userName
            reactor.listenTCP(listenMachine.listen_port, listenMachine)

            listen_process = Process(target=reactor.run)
            listen_process.start()

            while True:
                syncState = syncOptions(syncState)

        if (correctEntry == "False"):
            print "Incorrect username or password"


