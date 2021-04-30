import sys
import socket
import os
from datetime import datetime
import threading
import pickle

PORT = 5102
HOST = socket.gethostbyname(socket.gethostname())
addresses = []
threads = []
connections = []



def main():
    # Scans the arp table and finds all connected addresses
    global HOST
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


    # Add Banner 
    print("-" * 50)
    print("Scanning started at:" + str(datetime.now()))
    print("-" * 50)

    for i in range(len(addresses)):
        if (addresses[i] != HOST):
            thread = threading.Thread(target=checkPort, args=(addresses[i],))
            thread.start()
    


def checkPort(address):
    global PORT
    target = address
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(1)
        
        # returns an error indicator
        result = s.connect_ex((target, PORT))
        if result == 0:
            print("{}: Port {} is open".format(target, PORT))
            newThread = threading.Thread(target=checkForData, args=(s,))
            newThread.start()
            print("data: " + str(data))
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
    global HOST, PORT, threads, connections, addresses

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
                        connections.append(conn)
                        threads.append(newThread)
                        addresses.append(ip)
                except ValueError:
                    print("Sending file data to: " + ip)
                    print("Adding to network")
                    sendData = {
                        "msg": "test dictionary",
                        "ips": "list of ips",
                        "fileData": "file data for the client",
                        "id": HOST,
                        "port": PORT
                    }
                    conn.send(pickle.dumps(sendData))
                    addresses.append(ip)
                    conn.close()
                    continue
    except socket.error as socketerror:
        print("Error: ", socketerror)

def checkForData(conn):
    while True : 
        try:
            data = pickle.loads(conn.recv(2048))
            print("data: " + data["msg"])
            print("data: " + data["ips"])
            print("data: " + data["fileData"])
            print("data: " + data["id"])
            print("data: " + str(data["port"]))
        except EOFError:
            print("Exiting!")
            break


main()