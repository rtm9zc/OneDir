import os
import sys
import socket
from uuid import getnode as get_mac


HOST, PORT = "localhost", 9999
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

def sendData(userType, username, password):
    #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    # Connect to server and send data
    #sock.connect((HOST, PORT))

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
        isLocalMachine = sock.recv(1024)
        isLocalMachine = str(isLocalMachine).strip()

        if isLocalMachine == "False":
            filePath = raw_input("Enter the filepath where you would like your OneDir folder to be stored: ")
            sock.sendall(filePath + "\n")
            response1 = sock.recv(1024)

            #os.mkdir(filePath)


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

        #stop running clientMain.py and new_client.py
        #the below might not work!!!!!!!!
        #os s.system("killall clientMain")
        #os.system("killall new_client")

        syncState = "off"

    if currentState == "off":
        syncResponse = raw_input("Synchronization is off, would you like to turn synchronization on (enter yes if so)?")

        #resume running of clientMain.py and new_client.py
        os.system("python clientMain.py")
        os.system("python new_client.py")

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
        os.system("python clientMain.py")
        os.system("python new_client.py")


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
        correctEntry, isAdminUser = sendData(usertype, returningUsername, returningPassword)

        if (isAdminUser == "True" and correctEntry == "True"):
            adminInput()

        if (isAdminUser == "False" and correctEntry == "True"):

            os.system("python clientMain.py")
            os.system("python new_client.py")

            while True:
                syncOptions(syncState)

        if (correctEntry == "False"):
            print "Incorrect username or password"


