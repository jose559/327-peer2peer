import sys
import socket
import os
from datetime import datetime
import threading

PORT = 5102
HOST = socket.gethostbyname(socket.gethostname())
addresses = []
threads = []
connections = []



def main():
    # Scans the arp table and finds all connected addresses
    global addresses, HOST
    print(socket.gethostbyname(socket.gethostname()))
    with os.popen('arp -a') as f:
        data = f.read()

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
            s.sendall(b'Hello world')
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
                newThread = threading.Thread(target=checkForData, args=(conn, ip, port,))
                newThread.start()
                connections.append(conn)
                threads.append(newThread)
                addresses.append(ip)
    except socket.error as socketerror:
        print("Error: ", socketerror)

def checkForData(conn, ip, port):
    print("[+] New server socket thread started for " + ip + ":" + str(port))
 
    while True : 
        data = conn.recv(2048) 
        print("Server received data:", data)
        MESSAGE = b"Multithreaded Python server : Enter Response from Server/Enter exit:"
        if MESSAGE == 'exit':
            break
        conn.send(MESSAGE)  # echo 


main()