import sys
import socket
import os
from datetime import datetime
import threading

def main():
    # Scans the arp table and finds all connected addresses
    with os.popen('arp -a') as f:
        data = f.read()

    data = data.split('\n')
    print()
    addresses = []
    for i in range(3, len(data)):
        line = data[i].split(" ")
        for x in line:
            if x:
                addresses.append(x)
                break

    print(addresses)
    
    # Add Banner 
    print("-" * 50)
    print("Scanning started at:" + str(datetime.now()))
    print("-" * 50)

    for i in range(len(addresses)):
        thread = threading.Thread(target=checkPort, args=(addresses[i],))
        thread.start()
   


def checkPort(address):
    target = address
    try:
        # will scan ports between 1 to 65,535
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(1)
        
        # returns an error indicator
        result = s.connect_ex((target, 134))
        if result == 0:
            print("{}: Port 134 is open".format(target))
        else:
            print("{}: Port 134 is closed".format(target))
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

main()