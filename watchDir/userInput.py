
import os
import sys
import socket
from uuid import getnode as get_mac


HOST, PORT = "localhost", 9999

def sendData(userType, username, password):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to server and send data
        sock.connect((HOST, PORT))

        sock.sendall(usertype + "\n")
        response1 = sock.recv(1024)

        sock.sendall(username + "\n")
        response1 = sock.recv(1024)

        sock.sendall(password + "\n")
        correctUsernameAndPassword = sock.recv(1024)
        correctUsernameAndPassword = str(correctUsernameAndPassword).strip()

        if correctUsernameAndPassword == "True":

            mac = get_mac()
            mac = str(mac)
            sock.sendall(mac +"\n")
            isLocalMachine = sock.recv(1024)
            isLocalMachine = str(isLocalMachine).strip()

            if isLocalMachine == "False":
                filePath = raw_input("Enter the filepath where you would like your OneDir folder to be stored: ")
                sock.sendall(filePath + "\n")
                response1 = sock.recv(1024)

                #os.mkdir(filePath)






    finally:
        sock.close()

    return correctUsernameAndPassword


def syncOptions(currentState):
    global syncState
    if currentState == "on":
        syncResponse = raw_input("Synchronization is on, would you like to turn synchronization off (enter yes if so)?")

        #stop running clientMain.py and new_client.py
        #the below might not work!!!!!!!!
        #os s.system("killall clientMain")
        #os.system("killall new_client")

        syncState = "off"

    if currentState == "off":
        syncResponse = raw_input("Synchronization is off, would you like to turn synchronization on (enter yes if so)?")

        #resume running of clientMain.py and new_client.py
        #os.system("python clientMain.py")
        # os.system("python new_client.py")

        syncState = "on"




if __name__ == "__main__":

    global syncState
    syncState = "on"
    usertype = raw_input("Enter 1 if you are a new user and 2 if you are a returning user: ")

    if usertype == "1":
        usertype = "newuser"
        newUsername = raw_input("Please enter the new username: ")
        newPassword = raw_input("Please enter the new password: ")

        #run clientMain.py and new_client.py
        #os.system("python clientMain.py")
        #os.system("python new_client.py")


        #send a newuser marker to the server
        sendData(usertype, newUsername, newPassword)



        while True:
            syncOptions(syncState)


    else:
        usertype = "olduser"
        returningUsername = raw_input("Please enter your username: ")
        returningPassword = raw_input("Please enter your password: ")


        #if it matches the information found on the server: run clientMain.py and new_client.py

        #send the server a returning user marker
        correctEntry = sendData(usertype, returningUsername, returningPassword)


        if (correctEntry == "True"):

            #os.system("python clientMain.py")
            #os.system("python new_client.py")

            while True:
                syncOptions(syncState)

        else:
            print "Incorrect username or password"






