import socket
import sqlite3
import sys
import threading
from sqlite3 import Error


def startTcpServer(ip,port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverAddr = (ip, port)
    print(serverAddr)
    sock.bind(serverAddr)
    sock.listen(10)
    return sock

def ServeClient(sock,addr):
    msg = "Welcome to the BBS !\r\n"
    conn = sqlite3.connect('test.db')
    print("open db successful")
    cur = conn.cursor()
    sock.send(msg.encode('utf-8'))
    isLogin = 0
    userName = "None"
    while True:
        msg = "% "
        sock.send(msg.encode('utf-8'))
        recvMsg = sock.recv(1024).decode('utf-8')
        msgArr = recvMsg.split()
    #   part of register
        if(msgArr[0]== "register"):
            if(len(msgArr)==4):
                cursor = cur.execute('SELECT * FROM USER WHERE Name = ?;',(msgArr[1],))
                cursor = cursor.fetchone()
                if(cursor != None):
                    msg = "User name is already use.\r\n"
                    sock.send(msg.encode('utf-8'))
                    continue;
                try:
                    cursor = cur.execute('INSERT INTO user("Name","Email","Password")VALUES(?,?,?);',(msgArr[1],msgArr[2],msgArr[3]))
                    conn.commit()
                    print("Insert User ")
                    msg = "Register successfully. \r\n"
                    sock.send(msg.encode('utf-8'))
                except Error:
                    msg = "Register Error.\r\n"
                    sock.send(msg.encode('utf-8'))
            else:
                msg = "Usage: register <username> <email> <passsword>\r\n"
                sock.send(msg.encode('utf-8'))
    #   part of logiin
        elif(msgArr[0]=="login"):
            if(isLogin == 1):
                msg = "Please logout first.\r\n"              
                sock.send(msg.encode('utf-8'))
                continue;
            if(len(msgArr)==3):
                cursor = cur.execute('SELECT * FROM USER WHERE Name = ?;',(msgArr[1],))
                cursor = cursor.fetchone()
                if(cursor != None and cursor[3] == msgArr[2]):
                    msg = "Welcome " + msgArr[1]
                    print(msg)
                    msg = msg + ".\r\n"
                    sock.send(msg.encode('utf-8'))
                    isLogin = 1
                    userName = msgArr[1]
                else:
                    msg = "Login failed.\r\n"
                    sock.send(msg.encode('utf-8'))
            else:
                msg = "Usage: login <username> <password>\r\n"
                sock.send(msg.encode('utf-8'))
    #   part of logout
        elif(len(msgArr) == 1 and msgArr[0]== "logout"):
            if(isLogin == 1):
                msg = "Bye "+userName
                print(msg)
                msg = msg + "\r\n"
                sock.send(msg.encode('utf-8'))
                isLogin = 0
            else:
                msg = "Please login first.\r\n"
                sock.send(msg.encode('utf-8'))
    #   part of whoami
        elif(len(msgArr) == 1 and msgArr[0]== "whoami"):
            if(isLogin == 1):
                msg = userName + "\r\n" 
                sock.send(msg.encode('utf-8'))
            else:
                msg = "Please login first.\r\n"
                sock.send(msg.encode('utf-8'))
        elif(len(msgArr) == 1 and msgArr[0]== "exit" ):
            sock.close()
            break;
        else:
            msg = "Command Error, please type again.\r\n"
            sock.send(msg.encode('utf-8'))

bind_ip = ""
bind_port = 3110
mySer =  startTcpServer(bind_ip,bind_port)

while True:
    client,addr = mySer.accept()
    print ("New connection from: ",addr)
    thrd = threading.Thread(target = ServeClient,args =  (client, addr))
    thrd.start()
