import socket
import threading
import tkinter as tk
from tkinter import messagebox
import os
import tqdm

BUFFER_SIZE = 4096
file_index="index.html"
file_css="style.css"
index_size=os.path.getsize(file_index)
css_size=os.path.getsize(file_css)


def getFile(a):  
    #Lay file blacklist.conf
    f=open("blacklist.conf","rt")
    for x in f:
        a.append(x)

def sendFile(file_name,file_size):
    
    progress = tqdm.tqdm(range(file_size), f"Sending {file_name}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(file_name, "rb") as f:
        for _ in progress:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            # we use sendall to assure transimission in 
            # busy networks
            conn.sendall(b'''HTTP/1.1 \n\n'''+bytes_read)   
            # update the progress bar
            progress.update(len(bytes_read))


        

def handle_client(conn,a):

    #Lay request la 1 thong diep HTTP
    
    request2=conn.recv(10000)
    request=request2.decode('latin-1')
    print('request:')
    print(request)


    #Lay dong dau thong diep HTTP
    first_line=request.split('\n')[0]
    print('first_line:')
    print(first_line)


    #Lay URL
    url=first_line.split(' ')[1]
    print('url:')
    print(url)


    #find pos of "://"
    http_pos=url.find("://")
    if http_pos==-1:
        temp=url
    else:
        temp=url[(http_pos+3):]
    
    print('temp:')
    print(temp)
    #find end of web sever
    websever_pos=temp.find("/")
    if websever_pos==-1:
        websever_pos=len(temp)
    websever=""

    port=80

    #print(url)
    websever=temp[:websever_pos]
    port_pos=websever.find(":")
    if port_pos==-1:
        port=80
    else:
        port=int(websever[port_pos+1:])
        print(port)
        websever=websever[:port_pos]
    print('websever:')
    print(websever)
    blocked=False
    for str in a:
        if str[:len(str)-1] == websever:
            blocked=True

    if blocked==False:
        print('Unblocked')
        so=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        so.settimeout(300)
        so.connect((websever,port))
        so.sendall(request2)
        while True:
            data=so.recv(10000)
            if(len(data)>0):
                conn.sendall(data)
            else:
                print('out!')
                break
        so.close()
    else:
        print('Blocked')
        sendFile(file_index,index_size)
        sendFile(file_css,css_size)                                              
        
    conn.close()


HOST="192.168.30.174"
PORT=8888
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST,PORT))
s.listen(1000)

a=[]
getFile(a)  

while True:
    conn,addr=s.accept()
    t=threading.Thread(target=handle_client, args=(conn,a))
    t.setDaemon(True)
    t.start()
    
    