import sys
import socket
import os
from datetime import datetime
import threading

PORT = 5102

def main():
    # Scans the arp table and finds all connected addresses
    with os.popen('arp -a') as f:
        data = f.read()

    print(data)
    data = data.split('\n')
    print()
    addresses = []
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
        if (addresses[i] != (socket.gethostbyname(socket.gethostname()))):
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
        else:
            print("{}: Port {} is closed".format(target, PORT))
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
    HOST = ''
    global PORT

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((socket.gethostbyname(socket.gethostname()), PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
    except socket.error as socketerror:
        print("Error: ", socketerror)

main()