import sys
import socket
import os
from datetime import datetime
import threading
import pickle

PORT = 5102
#HOST = socket.gethostbyname(socket.gethostname())
HOST = socket.gethostbyname(socket.gethostname())
path = os.getcwd() + '\\' + HOST
addresses = []
currentFiles = []



def main():
    # Scans the arp table and finds all connected addresses
    global HOST, path, currentFiles
    print(socket.gethostbyname(socket.gethostname()))
    with os.popen('arp -a') as f:
        data = f.read()

    addresses = []

    print(data)
    data = data.split('\n')
    print()
    for i in range(3, len(data)):
        line = data[i].split(" ")
        for x in line:
            if x and x[0].isdigit():
                addresses.append(x)
                break

    print(addresses)
    
    
    serverThread = threading.Thread(target=acceptConnections, args=())
    serverThread.start()

    print(path)
    if not (os.path.exists(path)):
        os.makedirs(path)
        print("Making directory at " + path)

    currentFiles = os.listdir(path)
    print(currentFiles)
    for dirName in currentFiles:
        if (os.path.isdir(path + '\\' + dirName)):
            print('Is Folder')
        else:
            print("Isn't folder")
    currentFiles = getCurrentFiles(path)
    print(currentFiles)
    # Add Banner 
    print("-" * 50)
    print("Scanning started at:" + str(datetime.now()))
    print("-" * 50)

    for i in range(len(addresses)):
        if (addresses[i] != HOST):
            thread = threading.Thread(target=checkPort, args=(addresses[i],))
            thread.start()


    clientThread = threading.Thread(target=checkForUpdates())
    clientThread.start()
    


def checkPort(address):
    global PORT, path, addresses, currentFiles
    target = address
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(1)
        
        # returns an error indicator
        result = s.connect_ex((target, PORT))
        if result == 0:
            print("{}: Port {} is open".format(target, PORT))
            while True : 
                try:
                    data = pickle.loads(s.recv(2048))
                    print("data: " + data["msg"])
                    print(data["ips"])
                    print(data["fileData"])
                    print("data: " + data["id"])
                    print("data: " + str(data["port"]))
                    receiveNewFiles(path, data["fileData"])
                    currentFiles = data["fileData"]
                    addresses = data["ips"].append(data["id"])
                except EOFError:
                    print("Local Data has been received from address: " + target)
                    break    
        else:
            s.close()
        return
            
    except KeyboardInterrupt:
            print("\n Exitting Program !!!!")
            sys.exit()
    except socket.gaierror:
            print("\n Hostname Could Not Be Resolved !!!!")
            sys.exit()
    except socket.error:
            print("\ Server not responding !!!!")
            sys.exit()

def acceptConnections():
    global HOST, PORT, addresses, path

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            while True:
                s.listen(10)
                conn, (ip, port) = s.accept()
                try:
                    if (addresses.index(ip)):
                        newThread = threading.Thread(target=checkForData, args=(conn,))
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
                    conn.send(pickle.dumps(sendData))
                    conn.close()

                    for peer in addresses:
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
                    continue
    except socket.error as socketerror:
        print("Error: ", socketerror)

def checkForData(conn):
    global path
    while True: 
        try:
            data = pickle.loads(conn.recv(2048))
            receivedMsg = data["msg"]
            receivedData = data["attachment"]
            messageSender = data["id"]

            if (receivedMsg == "update"):
                currentFiles = data["attachment"]
                receiveNewFiles(path, data["attachment"])
                break
            elif (receivedMsg == "newNode"):
                break
            elif (receivedMsg == "leaving"):
                break
        except EOFError:
            print("Exiting!")
            break
    return

def checkForUpdates():
    global currentFiles, addresses, path
    while True:
        time.sleep(5)
        updatedFiles = getCurrentFiles(path)
        if (currentFiles != updatedFiles):
            currentFiles = updatedFiles
            for peer in addresses:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket.setdefaulttimeout(1)

                s.connect_ex((peer, PORT))
                sendData = {
                    "msg": "update",
                    "attachment": updatedFiles,
                    "id": HOST
                }
                s.send(pickle.dumps(sendData))
                s.close()
    return

def getCurrentFiles(path):
    print("Finding current files...")
    files = []
    recursiveGetCurrentFiles(path, files)
    print("Files found:")
    print(files)
    return files

def recursiveGetCurrentFiles(path, fileList):
    currentFiles = os.listdir(path)
    for dirName in currentFiles:
        if (os.path.isdir(path + '\\' + dirName)):
            newFileDir = [dirName]
            recursiveGetCurrentFiles(path + '\\' + dirName, newFileDir)
            fileList.append(newFileDir)
        else:
            f = open(path + '\\' + dirName, 'r')
            name = dirName + '\n'
            content = name + f.read()
            fileList.append(content)
            f.close()
    return

def receiveNewFiles(path, newFileList):
    print("Receiving new files...")
    recursiveReceiveNewFiles(path, newFileList)
    print("Files received.")
    return

def recursiveReceiveNewFiles(path, newFileList):
    for dirName in newFileList:
        if (isinstance(dirName, list)):
            newDirName = dirName.pop(0)
            if not (os.path.exists(path + '\\' + newDirName)):
                os.mkdir(path + '\\' + newDirName)
            recursiveReceiveNewFiles(path + '\\' + newDirName, dirName)
        else:
            fileName = dirName.split('\n', 1)[0]
            content = dirName.split('\n', 1)[1]
            newFile = os.path.join(path, fileName)
            f = open(newFile, 'w')
            f.write(content)
            f.close()
    return

main()