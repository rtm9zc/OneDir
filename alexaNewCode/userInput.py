import os
import threading
import sys
import socket
from uuid import getnode as get_mac

from multiprocessing import Process

#from clientMain import *
from new_client import *

from watchDir import OneDir_Observer
from sendingClient import LocalMachine



#HOST needs to be changed to whatever the server address is (command line argument)

HOST, PORT = "localhost", 9999
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

syncState = 'on'
filePath = 'False'
userName = 'user'

watchMachine = LocalMachine('TestUser', 'TestDirectory', HOST)
OneDog = OneDir_Observer(watchMachine)
listenMachine = ListenerMachine('TestDirectory', listen_port=1235)

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

            # mkdirs??????
            os.mkdir(filePath)


    #sock.close()

    return (correctUsernameAndPassword, isAdminUser)


def adminInput():
    adminChoiceNum = "1"
    while adminChoiceNum != "0":
        adminChoiceNum = raw_input("Enter 1 if you would like to view all usernames and passwords, \n"
                             "Enter 2 if you would like to see the number and size of files stored in total \n"
                             "Enter 3 if you would like to see number and size of files stored per user \n"
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
            adminResults = sock.recv(1024)
            print "received"
            adminResults = str(adminResults).strip()

            if adminChoiceNum == "4" or adminChoiceNum == "5":
                accountToDelete = raw_input("Enter the username for the account you wish to delete: ")
                accountToDelete = str(accountToDelete).strip()
                sock.sendall(accountToDelete + "\n")
                adminResults = sock.recv(1024)
                adminResults = str(adminResults).strip()

            if adminChoiceNum == "6":
                usernameForPWChange = raw_input("Enter the username for the account for which you wish to change the password: ")
                usernameForPWChange = str(usernameForPWChange).strip()
                sock.sendall(usernameForPWChange + "\n")
                adminResults = sock.recv(1024)

                passwordForPWChange = raw_input("Enter the username for the account for which you wish to change the password: ")
                passwordForPWChange = str(passwordForPWChange).strip()
                sock.sendall(passwordForPWChange + "\n")
                adminResults = sock.recv(1024)

                adminResults = str(adminResults).strip()


        finally:
            print adminResults
            #sock.close()



def syncOptions(currentState):
    global syncState
    if currentState == "on":
        syncResponse = raw_input("Synchronization is on, would you like to turn synchronization off (enter yes if so)?")

        # send message to server socket
        # server receives "off" message --> updates local machine sync status boolean

        syncState = "off"

    if currentState == "off":
        syncResponse = raw_input("Synchronization is off, would you like to turn synchronization on (enter yes if so)?")

        # send message to server socket
        # server receives "on" message --> updates local machine sync status boolean syncOn to True
        # files

        syncState = "on"

# add server IP Address as a command line argument

if __name__ == "__main__":

    global syncState
    #syncState = "on"
    global userName

    global watchMachine
    global listenMachine

    global filePath

    usertype = raw_input("Enter 1 if you are a new user and 2 if you are a returning user: ")

    if usertype == "1":
        usertype = "newuser"
        newUsername = raw_input("Please enter the new username: ")
        newPassword = raw_input("Please enter the new password: ")

        userName = newUsername

        #send a newuser marker to the server
        sendData(usertype, newUsername, newPassword)

        # right here we need access to the filepath/directory of THIS user
        # need server IP address --> can be a command line argument (see above)

        # change for whatever user / file path is acquired above
        watchMachine.oneDir = filePath
        watchMachine.username = userName

        # watch_thread = threading.Thread(target=OneDog.startWatching)
        # watch_thread.daemon = True
        # watch_thread.start

        watch_process = Process(target=OneDog.startWatching)
        watch_process.start()

        # port = whichever port we determine will be the client listening port (1235?)
        listenMachine.dir_path = filePath
        reactor.listenTCP(listenMachine.listen_port, listenMachine)

        listen_process = Process(target=reactor.listenTCP, args=(listenMachine.listen_port, listenMachine))
        listen_process.start()

        # listen_thread = threading.Thread(target=reactor.run)
        # listen_thread.daemon = True
        # listen_thread.start

        while True:
            syncOptions(syncState)

    else:
        usertype = "olduser"
        returningUsername = raw_input("Please enter your username: ")
        returningPassword = raw_input("Please enter your password: ")

        userName = returningUsername

        #if it matches the information found on the server: run clientMain.py and new_client.py

        #send the server a returning user marker
        correctEntry, isAdminUser = sendData(usertype, returningUsername, returningPassword)

        if (isAdminUser == "True" and correctEntry == "True"):
            adminInput()

        if (isAdminUser == "False" and correctEntry == "True"):

            # change for whatever user / file path is acquired above
            watchMachine.oneDir = filePath
            watchMachine.username = userName
            OneDog.lm.oneDir = filePath
            OneDog.lm.username = userName

            watch_process = Process(target=OneDog.startWatching)
            watch_process.start()

            # watch_thread = threading.Thread(target=OneDog.startWatching)
            # watch_thread.daemon = True
            # watch_thread.start

            # port = whichever port we determine will be the client listening port (1235?)
            listenMachine.dir_path = filePath
            reactor.listenTCP(listenMachine.listen_port, listenMachine)
            # listen_thread = threading.Thread(target=reactor.run)
            # listen_thread.daemon = True
            # listen_thread.start

            listen_process = Process(target=reactor.listenTCP, args=(listenMachine.listen_port, listenMachine))
            listen_process.start()

            while True:
                syncOptions(syncState)

        if (correctEntry == "False"):
            print "Incorrect username or password"


