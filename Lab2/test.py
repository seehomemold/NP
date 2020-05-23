import socket
import sqlite3
import sys
import threading
import datetime
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
    #   part of search database
        if(msgArr[0]== "search"):
            for row in cur.execute('select * from user;'):
                print(row)
        elif(msgArr[0]== "clearUser"):
            cur.execute('DELETE FROM USER;')

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
    #   part of create board
        elif(len(msgArr) == 2 and msgArr[0]== "create-board" ):
            if(isLogin == 1):
                try:
                    cursor = cur.execute('SELECT * FROM board WHERE name = ?;',(msgArr[1],))
                    cursor = cursor.fetchone()
                    if(cursor == None):
                        try:
                            sql = 'insert into board("name","moderator")values(?,?);'
                            cursor = cur.execute(sql,(msgArr[1],userName))
                            msg = "Create board successfully.\r\n"
                            sock.send(msg.encode('utf-8'))
                        except Error as e:
                            print("insert fail")
                        conn.commit()
                    else:
                        msg = "Board already exist.\r\n"
                        sock.send(msg.encode('utf-8'))
                    conn.commit()
                except Error as e:
                    msg ="unknown error.\r\n" 
                    sock.send(msg.encode('utf-8'))
                    print(e)
            else:
                msg = "Please login first.\r\n"
                sock.send(msg.encode('utf-8'))
    #   part of list-board
        elif(msgArr[0]== "list-board" ):
            if(len(msgArr) == 1):
                msg ="Index\tName\tModerator\r\n" 
                sock.send(msg.encode('utf-8'))
                for row in cur.execute('select * from board;'):
                    msg = str(row[0])
                    sock.send(msg)
                    msg = "\t"+row[1]+"\t"+row[2]+"\r\n"
                    sock.send(msg.encode('utf-8'))
            if(len(msgArr) == 2 and msgArr[1][0]=='#' and msgArr[1][1]=='#'):
                msgKey =  msgArr[1].replace('#','')
                msg ="Index\tName\tModerator\r\n" 
                sock.send(msg.encode('utf-8'))
                for row in cur.execute('SELECT * FROM board WHERE Name LIKE ?;',("%"+msgKey+"%",)):
                    msg = str(row[0])
                    sock.send(msg)
                    msg = "\t"+row[1]+"\t"+row[2]+"\r\n"
                    sock.send(msg.encode('utf-8'))

    #   part of create post
        elif(len(msgArr) > 5 and msgArr[0]== "create-post" ):
            if(msgArr[2]== "--title" and recvMsg.rfind(" --content ")!= -1):
                msgTC = recvMsg.split("--title ",1)[1].split(" --content ",1)
                if(isLogin == 1):
                    try:
                        sql = 'insert into post("Title","Author","Date","Content","Board" )values(?,?,?,?,?);'
                        now = datetime.datetime.now()
                        dateStr = str(now.month) + "/" + str(now.day)
                        cursor = cur.execute(sql,(msgTC[0],userName,dateStr,msgTC[1],msgArr[1]))
                        conn.commit()
                        msg ="Create post successfully.\r\n" 
                        sock.send(msg.encode('utf-8'))
                    except Error as e:
                        msg ="Board does not exist.\r\n" 
                        sock.send(msg.encode('utf-8'))
                        print(e)
                else:
                    msg = "Please login first.\r\n"
                    sock.send(msg.encode('utf-8'))
    #   part of list-post
        elif(msgArr[0]== "list-post" ):
            if(len(msgArr) == 2):
                cursor = cur.execute('select * from post where Board = ? ;',(msgArr[1],)).fetchone()
                if(cursor != None):
                    msg = "{:^7} {:^20} {:^20} {:^9}\r\n\r\n".format("ID","Title","Author","Datey")
                    sock.send(msg.encode('utf-8'))
                    cursor = cur.execute('select * from post where Board = ? ;',(msgArr[1],))
                    for row in cursor:
                        msg = "{:>7} {:^20} {:^20} {:^9}\r\n\r\n".format(str(row[0]),row[1],row[2],row[3])
                        sock.send(msg.encode('utf-8'))
                else:
                    msg = "Board does not exit.\r\n"
                    sock.send(msg.encode('utf-8'))
            elif(len(msgArr) == 3 and msgArr[2][0]=='#' and msgArr[2][1]=='#'):
                msgKey =  msgArr[2].replace('#','')
                cursor = cur.execute('select * from post where Board = ? AND Title LIKE ?;',(msgArr[1],"%"+msgKey+"%")).fetchone()
                if(cursor != None):
                    msg = "{:^7} {:^20} {:^20} {:^9}\r\n\r\n".format("ID","Title","Author","Datey")
                    sock.send(msg.encode('utf-8'))
                    cursor = cur.execute('select * from post where Board = ? ;',(msgArr[1],))
                    for row in cursor:
                        msg = "{:>7} {:^20} {:^20} {:^9}\r\n\r\n".format(str(row[0]),row[1],row[2],row[3])
                        sock.send(msg.encode('utf-8'))
                else:
                    msg = "Board does not exit.\r\n"
                    sock.send(msg.encode('utf-8'))
            else:
                msg = "list-post <board-name> ##<key>.\r\n"
                sock.send(msg.encode('utf-8'))
    #   part of read
        elif(len(msgArr) == 2 and msgArr[0]== "read" ):
            cursor = cur.execute('select * from post where ID = ? ;',(msgArr[1],)).fetchone()
            if(cursor != None):
                msg = "\r\nAuthor\t:"+cursor[2]+"\r\n"
                sock.send(msg.encode('utf-8'))
                msg = "Title\t:"+cursor[1]+"\r\n"
                sock.send(msg.encode('utf-8'))
                msg = "Date\t:"+cursor[3]+"\r\n"
                sock.send(msg.encode('utf-8'))
                msg = "----\r\n"
                sock.send(msg.encode('utf-8'))
                msg = cursor[4].replace("<br>","\r\n")
                sock.send(msg.encode('utf-8'))
                msg = "----\r\n"
                sock.send(msg.encode('utf-8'))
                if(cursor[6]!=None):
                    msg = cursor[6] + "\r\n"
                    sock.send(msg.encode('utf-8'))
            else:
                msg = "Post does not exit.\r\n"
                sock.send(msg.encode('utf-8'))
        #   part of delete post
        elif(len(msgArr) == 2 and msgArr[0]== "delete-post" ):
            if(isLogin == 1):
                cursor = cur.execute('select * from post where ID = ? ;',(msgArr[1],)).fetchone()
                if(cursor==None):
                    msg = "Post does not exist.\r\n"
                    sock.send(msg.encode('utf-8'))
                elif(cursor[2]!=userName):
                    msg = "Not the post owner.\r\n"
                    sock.send(msg.encode('utf-8'))
                else:
                    cursor = cur.execute('delete from post where ID = ? ;',(msgArr[1],))
                    conn.commit()
                    msg = "Delete successfully.\r\n"
                    sock.send(msg.encode('utf-8'))
            else:
                msg = "Please login first.\r\n"
                sock.send(msg.encode('utf-8'))
        #   part of update post
        elif(len(msgArr) > 3 and msgArr[0]== "update-post" ):
            if(msgArr[2]=="--title"):
                if(isLogin == 1):
                    cursor = cur.execute('select * from post where ID = ? ;',(msgArr[1],)).fetchone()
                    if(cursor==None):
                        msg = "Post does not exist.\r\n"
                        sock.send(msg.encode('utf-8'))
                    elif(cursor[2]!=userName):
                        msg = "Not the post owner.\r\n"
                        sock.send(msg.encode('utf-8'))
                    else:
                        new = recvMsg.split("--title ",1)[1]
                        cursor = cur.execute('update post set Title = ? where ID = ? ;',(new,msgArr[1]))
                        conn.commit()
                        msg = "Update successfully.\r\n"
                        sock.send(msg.encode('utf-8'))
                else:
                    msg = "Please login first.\r\n"
                    sock.send(msg.encode('utf-8'))
            elif(msgArr[2]=="--content"):
                if(isLogin == 1):
                    cursor = cur.execute('select * from post where ID = ? ;',(msgArr[1],)).fetchone()
                    if(cursor==None):
                        msg = "Post does not exist.\r\n"
                        sock.send(msg.encode('utf-8'))
                    elif(cursor[2]!=userName):
                        msg = "Not the post owner.\r\n"
                        sock.send(msg.encode('utf-8'))
                    else:
                        new = recvMsg.split("--content ",1)[1]
                        cursor = cur.execute('update post set Content = ? where ID = ? ;',(new,msgArr[1]))
                        conn.commit()
                        msg = "Update successfully.\r\n"
                        sock.send(msg.encode('utf-8'))
                else:
                    msg = "Please login first.\r\n"
                    sock.send(msg.encode('utf-8'))
            else:
                msg = "update-post <post-id> --title/content <new>.\r\n"
                sock.send(msg.encode('utf-8'))
        #   part of comment post
        elif(len(msgArr) > 2 and msgArr[0]== "comment" ):
            if(isLogin == 1):
                cursor = cur.execute('select * from post where ID = ? ;',(msgArr[1],)).fetchone()
                if(cursor==None):
                    msg = "Post does not exist.\r\n"
                    sock.send(msg.encode('utf-8'))
                elif(cursor[6] != None ):
                    comment = cursor[6] + userName+ " :" + recvMsg.split(msgArr[1],1)[1]
                    cursor = cur.execute('update post set Comment = ? where ID = ? ;',(comment,msgArr[1]))
                    conn.commit()
                    msg = "Comment successfully.\r\n"
                    sock.send(msg.encode('utf-8'))
                else:
                    comment = userName+ " :" + recvMsg.split(msgArr[1],1)[1]
                    cursor = cur.execute('update post set Comment = ? where ID = ? ;',(comment,msgArr[1]))
                    conn.commit()
                    msg = "Comment successfully.\r\n"
                    sock.send(msg.encode('utf-8'))

            else:
                msg = "Please login first.\r\n"
                sock.send(msg.encode('utf-8'))
    # # # # # part of exit
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
