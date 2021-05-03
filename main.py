import sys
import socket
import os
from datetime import datetime
import threading
import pickle
import time

PORT = 5102 #chosen port 
#HOST = socket.gethostbyname(socket.gethostname())
HOST = socket.gethostbyname(socket.gethostname())
path = os.getcwd() + '\\' + HOST #current working directory 
addresses = []
currentFiles = []



def main():
    try:
        # Scans the arp table and finds all connected addresses
        global HOST, path, currentFiles
        print(socket.gethostbyname(socket.gethostname()))
        with os.popen('arp -a') as f:
            data = f.read()

        arpAddresses = []

        print(data) #split data 
        data = data.split('\n')
        print()
        for i in range(3, len(data)):
            line = data[i].split(" ")
            for x in line:
                if x and x[0].isdigit():
                    arpAddresses.append(x)
                    break

        print(arpAddresses)

        #create path if path doesnt exsist 
        print(path)
        if not (os.path.exists(path)):
            os.makedirs(path)
            print("Making directory at " + path)

        #get the files from one path to another 
        currentFiles = getCurrentFiles(path)
        print(currentFiles)
        
        #start the threads for server 
        serverThread = threading.Thread(target=acceptConnections, args=())
        serverThread.start()
        
        #checks address in range 
        for i in range(len(arpAddresses)):
            if (arpAddresses[i] != HOST):
                thread = threading.Thread(target=checkPort, args=(arpAddresses[i],))
                thread.start()

        #create client thread 
        clientThread = threading.Thread(target=checkForUpdates())
        clientThread.start()
    except KeyboardInterrupt as e:
        sys.exit(0)
    

#port checking for available ports that are currently stated at the top
def checkPort(address):
    global PORT, path, addresses, currentFiles
    target = address
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(1) #socket time out 
        
        #Attempts to connect to the port
        result = s.connect_ex((target, PORT))
        if result == 0:
            print("{}: Port {} is open".format(target, PORT))
            while True : 
                try:
                    data = pickle.loads(s.recv(2048))#bytes like obj that is returned  with reconstituted hierarchy 
                    receiveNewFiles(path, data["fileData"])
                    currentFiles = data["fileData"]
                    addresses = data["ips"]
                    addresses.append(data["id"])
                except EOFError:
                    print("Local Data has been received from address: " + target) #When all data is up to date 
                    break
        else:
            s.close()
        return
     
    except KeyboardInterrupt:
            print("\n Exitting Program !!!!")#when the program is done 
            sys.exit()
    except socket.gaierror:
            print("\n Hostname Could Not Be Resolved !!!!")#error management
            sys.exit()
    except socket.error:
            print("\ Server not responding !!!!")#error management
            sys.exit()

#listens for connections 
def acceptConnections():
    global HOST, PORT, addresses, path

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: # start the socket stream 
            s.bind((HOST, PORT))
            while True:
                s.listen(10) #listens for 10s
                conn, (ip, port) = s.accept()
                print("Receiving new connection...")
                try:
                    if (addresses.index(ip) != -1): #checks if ip isnt on the list 
                        newThread = threading.Thread(target=checkForData, args=(conn,))#if it isnt create a new thread
                        newThread.start()
                except ValueError:
                    print("Sending file data to: " + ip)
                    print("Adding to network")
                    sendData = {
                        "msg": "Initial data",
                        "ips": addresses,
                        "fileData": getCurrentFiles(path),
                        "id": HOST,
                        "port": PORT
                    }
                    conn.send(pickle.dumps(sendData))# sends data as byte instead of a file 
                    conn.close()

                    for peer in addresses: #for a peer witha new node to be updated 
                        print("Updating peers with new node...")
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        socket.setdefaulttimeout(1)

                        s.connect_ex((peer, PORT))
                        sendData = {
                            "msg": "newNode",
                            "attachment": ip,
                            "id": HOST
                        }
                        s.send(pickle.dumps(sendData))
                        s.close()
                    addresses.append(ip)
                    print("Updating complete.")
                    continue
    except socket.error as socketerror:
        print("Error: ", socketerror)
    except KeyboardInterrupt as e:
        sys.exit(0)

#checks the file and moves a file from one client to another if the file exsists 
def checkForData(conn):
    print("Data being retrieved...")
    global path, currentFiles
    while True: 
        try:
            data = pickle.loads(conn.recv(2048))
            receivedMsg = data["msg"]
            receivedData = data["attachment"]
            messageSender = data["id"]
            print("Data message: " + receivedMsg)

            if (receivedMsg == "update"):
                print("Updating files...")
                currentFiles = data["attachment"]
                receiveNewFiles(path, data["attachment"])
                break
            elif (receivedMsg == "newNode"):
                print("Adding new address...")
                addresses.append(data["attachment"])
                break
            elif (receivedMsg == "leaving"):
                print("Removing node...")
                addresses.remove(data["id"])
                break
        except EOFError:
            print("Data retrieval complete.")
            break
    return

def checkForUpdates(): #checks for new files in the between client and server if they exsist they will be added
    global currentFiles, addresses, path
    while True:
        try:
            time.sleep(5)
            print("Checking local files...")
            updatedFiles = getCurrentFiles(path)
            if (currentFiles != updatedFiles):
                currentFiles = updatedFiles
                print("Sending updated information")
                for peer in addresses:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    socket.setdefaulttimeout(1)

                    s.connect_ex((peer, PORT)) #remote socket connection  
                    sendData = {
                        "msg": "update",
                        "attachment": updatedFiles,
                        "id": HOST
                    }
                    s.send(pickle.dumps(sendData))
                    s.close()
                print("Sending complete.")
        except KeyboardInterrupt as e: # closes the data 
            print("Sending exit messages...")
            for peer in addresses:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket.setdefaulttimeout(1)

                s.connect_ex((peer, PORT))
                sendData = {
                    "msg": "leaving",
                    "attachment": HOST,
                    "id": HOST
                }
                s.send(pickle.dumps(sendData))
                s.close()
            print("Messages sent. Closing.")
            sys.exit(0)
    return

def getCurrentFiles(path):
    files = []
    recursiveGetCurrentFiles(path, files)
    return files

def recursiveGetCurrentFiles(path, fileList): # recursion through the files to check current patj and list of files 
    currentFiles = os.listdir(path)
    for dirName in currentFiles:
        if (os.path.isdir(path + '\\' + dirName)):
            newFileDir = [dirName]
            recursiveGetCurrentFiles(path + '\\' + dirName, newFileDir)
            fileList.append(newFileDir)
        else:
            f = open(path + '\\' + dirName, encoding="ISO-8859-1")
            name = dirName + '\n'
            content = name + f.read()#read 
            fileList.append(content)
            f.close()
    return

def receiveNewFiles(path, newFileList): #receving new file small fucntion 
    print("Receiving new files...")
    recursiveReceiveNewFiles(path, newFileList)
    print("Files received.")
    return

def recursiveReceiveNewFiles(path, newFileList):#recurse through the new files if the exist or path 
    for dirName in newFileList:
        if (isinstance(dirName, list)): #creates new path and file list if needed 
            newDirName = dirName.pop(0)
            if not (os.path.exists(path + '\\' + newDirName)):
                os.mkdir(path + '\\' + newDirName)
            recursiveReceiveNewFiles(path + '\\' + newDirName, dirName)
        else:
            fileName = dirName.split('\n', 1)[0]
            content = dirName.split('\n', 1)[1]
            newFile = os.path.join(path, fileName)
            f = open(newFile, 'w') #write to new file 
            f.write(content)
            f.close()
    return

main()