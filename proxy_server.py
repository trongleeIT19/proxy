import socket
import threading
import tkinter as tk
from tkinter import messagebox
import os

BUFFER_SIZE = 4096
file_index="index.html"
index_size=os.path.getsize(file_index)


def getBlacklist(blacklist):  
#get file blacklist.conf
    f=open("blacklist.conf","rt")
    for x in f:
        blacklist.append(x)

def sendFile(file_name,file_size):
    with open(file_name, "rb") as f:
        for _ in range(file_size):
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            conn.sendall(b'''HTTP/1.1 403 Forbidden\n\n'''+bytes_read)   

        
def handle_client(conn,blacklist):
    #get request as a HTTP message
    request2=conn.recv(10000)
    request=request2.decode('latin-1')
    print(" \n========== Request:==========")
    print(request)
    

    #Get the first line of HTTP message
    first_line=request.split('\n')[0]
    print("========== First_line: ==========")
    print(first_line)


    #Get URL
    url=first_line.split(' ')[1]

    #find position of "://"
    http_pos=url.find("://")
    if http_pos==-1:
        temp=url
    else:
        temp=url[(http_pos+3):]
    

    #find the end of web sever
    websever_pos=temp.find("/")
    if websever_pos==-1:
        websever_pos=len(temp)
    websever=""

    port=80

    print("\n\n========== URL:  ==========")
    print(url)
    websever=temp[:websever_pos]
    port_pos=websever.find(":")
    if port_pos==-1:
        port=80
    else:
        port=int(websever[port_pos+1:])
        print(port)
        websever=websever[:port_pos]
    
    blocked=False
    status="Unblocked!"
    for str in blacklist:
        if str[:len(str)-1] == websever:
            blocked=True
            status="Blocked!"
    
    print("\n\n========== Status: ==========")

    if blocked==False:
        print(status)
        so=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        so.settimeout(300)
        so.connect((websever,port))
        so.sendall(request2)
        while True:
            data=so.recv(10000)
            if(len(data)>0):
                conn.sendall(data)
            else:
                #print('out!')
                break
        so.close()
    else:
        print(status)
        sendFile(file_index,index_size)                                              
    print("\n\n\n")
    conn.close()


HOST="127.0.0.1"
PORT=8888
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST,PORT))
s.listen(1000)
#change working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
blacklist=[]
getBlacklist(blacklist)  
print("Waiting for server...")

while True:
    conn,addr=s.accept()
    t=threading.Thread(target=handle_client, args=(conn,blacklist))
    t.setDaemon(True)
    t.start()
    
    
