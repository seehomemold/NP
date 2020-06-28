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
    def RECEIVE():
        while True:
            try:
                msg_in = sock.recv(1024).decode('utf-8')
                return msg_in
            except:
                pass
    def SEND(CMD):
        while True:
            try:
                sock.send(CMD.encode('utf-8'))
                return "send success"
            except:
                pass
    
    sock.setblocking(0)

    msg = "Welcome to the BBS !"
    conn = sqlite3.connect('test.db')
    print("open db successful")
    cur = conn.cursor()
    SEND(CMD = msg)

    isLogin = 0
    userName = "None"
    bucketName = "None"
    while True:
        recvMsg = RECEIVE()
        msgArr = recvMsg.split()
        print recvMsg

    #   part of register
        if(msgArr[0]== "register"):
            if(len(msgArr)==4):
                cursor = cur.execute('SELECT * FROM USER WHERE Name = ?;',(msgArr[1],))
                cursor = cursor.fetchone()
                if(cursor != None):
                    msg = "User name is already use.\r\n"
                    SEND(CMD = msg)
                    continue;
                try:
                    msg = "success "
                    print("Insert User ")
                    msg = msg + "Register successfully. \r\n"
                    SEND(CMD = msg)
                    BucketName = RECEIVE()
                    cursor = cur.execute('INSERT INTO user("Name","Email","Password","BucketName")VALUES(?,?,?,?);',(msgArr[1],msgArr[2],msgArr[3],BucketName))
                    conn.commit()
                except Error:
                    msg = "Register Error.\r\n"
                    SEND(CMD = msg)
            else:
                msg = "Usage: register <username> <email> <passsword>\r\n"
                SEND(CMD = msg)
    #   part of logiin
        elif(msgArr[0]=="login"):
            if(isLogin == 1):
                msg = "Please logout first.\r\n" 
                SEND(CMD = msg)
                continue;
            if(len(msgArr)==3):
                cursor = cur.execute('SELECT * FROM USER WHERE Name = ?;',(msgArr[1],))
                cursor = cursor.fetchone()
                if(cursor != None and cursor[3] == msgArr[2]):
                    msg = cursor[4] + "#^#" + "Welcome " + msgArr[1]
                    msg = msg + ".\r\n"
                    SEND(CMD = msg)
                    isLogin = 1
                    userName = msgArr[1]
                    bucketName = cursor[4]
                    print bucketName
                else:
                    msg = "Login failed.\r\n"
                    SEND(CMD = msg)
            else:
                msg = "Usage: login <username> <password>\r\n"
                SEND(CMD = msg)
    #   part of logout
        elif(len(msgArr) == 1 and msgArr[0]== "logout"):
            if(isLogin == 1):
                msg = "Bye "+userName
                print(msg)
                msg = msg + "\r\n"
                SEND(CMD = msg)
                isLogin = 0
            else:
                msg = "Please login first.\r\n"
                SEND(CMD = msg)
    #   part of whoami
        elif(len(msgArr) == 1 and msgArr[0]== "whoami"):
            if(isLogin == 1):
                msg = userName + "\r\n" 
                SEND(CMD = msg)
            else:
                msg = "Please login first.\r\n"
                SEND(CMD = msg)
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
                            SEND(CMD = msg)
                        except Error as e:
                            print("insert fail")
                        conn.commit()
                    else:
                        msg = "Board already exist.\r\n"
                        SEND(CMD = msg)
                    conn.commit()
                except Error as e:
                    msg ="unknown error.\r\n" 
                    SEND(CMD = msg)
                    print(e)
            else:
                msg = "Please login first.\r\n"
                SEND(CMD = msg)
    #   part of list-board
        elif(msgArr[0]== "list-board" ):
            if(len(msgArr) == 1):
                msg ="Index\tName\tModerator\r\n" 
                for row in cur.execute('select * from board;'):
                    msg = msg+ str(row[0])
                    msg = msg+ "\t"+row[1]+"\t"+row[2]+"\r\n"
                SEND(CMD = msg)
            elif(len(msgArr) == 2 and msgArr[1][0]=='#' and msgArr[1][1]=='#'):
                msgKey =  msgArr[1].replace('#','')
                msg ="Index\tName\tModerator\r\n" 
                for row in cur.execute('SELECT * FROM board WHERE Name LIKE ?;',("%"+msgKey+"%",)):
                    msg = msg+ str(row[0])
                    msg = msg+"\t"+row[1]+"\t"+row[2]+"\r\n"
                SEND(CMD = msg)
            else:
                msg = "Command error. \r\n"
                SEND(CMD = msg)
    #   part of create post
        elif(len(msgArr) > 5 and msgArr[0]== "create-post" ):
            if(msgArr[2]== "--title" and recvMsg.rfind(" --content ")!= -1):
                msgTC = recvMsg.split("--title ",1)[1].split(" --content ",1)
                if(isLogin == 1):
                    cursor = cur.execute('SELECT * FROM board WHERE Name = ?', (msgArr[1],)).fetchone()
                    if cursor == None:
                        msg = "Board does not exist.\r\n"
                        SEND(CMD=msg)
                    else:
                        try:
                            sql = 'insert into post("Title","Author","Date","Content","Board","BucketName")values(?,?,?,?,?,?);'
                            now = datetime.datetime.now()
                            dateStr = str(now.month) + "/" + str(now.day)
                            cursor = cur.execute(sql,(msgTC[0],userName,dateStr,msgTC[1],msgArr[1],bucketName,))
                            conn.commit()
                            print bucketName
                            print msgArr[1]
                            Last_post = cur.execute('select * from post where title = ?',(msgTC[0],)).fetchall()
                            PostID = Last_post[-1][0] ## Last post's first element
                            msg = "mark " + str(PostID) + " Create post successfully.\r\n" 
                            SEND(CMD = msg)
                        except Error as e:
                            msg ="Board does not exist.\r\n" 
                            SEND(CMD = msg)
                            print(e)
                else:
                    msg = "Please login first.\r\n"
                    SEND(CMD = msg)
            else:
                msg = "Command Error!\r\n"
                SEND(CMD =msg)
    #   part of list-post
        elif(msgArr[0]== "list-post" ):
            if(len(msgArr) == 2):
                cursor = cur.execute('select * from post where Board = ? ;',(msgArr[1],)).fetchone()
                if(cursor != None):
                    msg = "{:^7} {:^20} {:^20} {:^9}\r\n\r\n".format("ID","Title","Author","Date")
                    cursor = cur.execute('select * from post where Board = ? ;',(msgArr[1],))
                    for row in cursor:
                        msg = msg+"{:>7} {:^20} {:^20} {:^9}\r\n\r\n".format(str(row[0]),row[1],row[2],row[3])
                    SEND(CMD = msg)
                else:
                    msg = "Board does not exit.\r\n"
                    SEND(CMD = msg)
            elif(len(msgArr) == 3 and msgArr[2][0]=='#' and msgArr[2][1]=='#'):
                msgKey =  msgArr[2].replace('#','')
                cursor = cur.execute('select * from post where Board = ? AND Title LIKE ?;',(msgArr[1],"%"+msgKey+"%")).fetchone()
                if(cursor != None):
                    msg = "{:^7} {:^20} {:^20} {:^9}\r\n\r\n".format("ID","Title","Author","Date")
                    cursor = cur.execute('select * from post where Board = ? AND Title LIKE ?;',(msgArr[1],"%"+msgKey+"%"))
                    for row2 in cursor:
                        msg = msg+"{:>7} {:^20} {:^20} {:^9}\r\n\r\n".format(str(row2[0]),row2[1],row2[2],row2[3])
                    SEND(CMD = msg)
                else:
                    msg = "Board does not exit.\r\n"
                    SEND(CMD = msg)
            else:
                msg = "list-post <board-name> ##<key>.\r\n"
                SEND(CMD = msg)
    #   part of read
        elif(len(msgArr) == 2 and msgArr[0]== "read" ):
            cursor = cur.execute('select * from post where ID = ? ;',(msgArr[1],)).fetchone()
            if(cursor != None):
                msg = "readSuc "+ cursor[7] + " \r\nAuthor\t:"+cursor[2]+"\r\n"
                msg = msg+"Title\t:"+cursor[1]+"\r\n"
                msg = msg+"Date\t:"+cursor[3]+"\r\n"
                msg = msg+"----"
                #msg = msg+cursor[4].replace("<br>","\r\n")
                #msg = msg+"----\r\n"
                #if(cursor[6]!=None):
                #    msg = msg+cursor[6] + "\r\n"
                SEND(CMD = msg)
            else:
                msg = "Post does not exit.\r\n"
                SEND(CMD = msg)
        #   part of delete post
        elif(len(msgArr) == 2 and msgArr[0]== "delete-post" ):
            if(isLogin == 1):
                cursor = cur.execute('select * from post where ID = ? ;',(msgArr[1],)).fetchone()
                if(cursor==None):
                    msg = "Post does not exist.\r\n"
                    SEND(CMD = msg)
                elif(cursor[2]!=userName):
                    msg = "Not the post owner.\r\n"
                    SEND(CMD = msg)
                else:
                    cursor = cur.execute('delete from post where ID = ? ;',(msgArr[1],))
                    conn.commit()
                    msg = "del# " + bucketName + " Delete successfully.\r\n"
                    SEND(CMD = msg)
            else:
                msg = "Please login first.\r\n"
                SEND(CMD = msg)
        #   part of update post
        elif(len(msgArr) > 3 and msgArr[0]== "update-post" ):
            if(msgArr[2]=="--title"):
                if(isLogin == 1):
                    cursor = cur.execute('select * from post where ID = ? ;',(msgArr[1],)).fetchone()
                    if(cursor==None):
                        msg = "Post does not exist.\r\n"
                        SEND(CMD = msg)
                    elif(cursor[2]!=userName):
                        msg = "Not the post owner.\r\n"
                        SEND(CMD = msg)
                    else:
                        new = recvMsg.split("--title ",1)[1]
                        cursor = cur.execute('update post set Title = ? where ID = ? ;',(new,msgArr[1]))
                        conn.commit()
                        msg = "Update successfully.\r\n"
                        SEND(CMD = msg)
                else:
                    msg = "Please login first.\r\n"
                    SEND(CMD = msg)
            elif(msgArr[2]=="--content"):
                if(isLogin == 1):
                    cursor = cur.execute('select * from post where ID = ? ;',(msgArr[1],)).fetchone()
                    if(cursor==None):
                        msg = "Post does not exist.\r\n"
                        SEND(CMD = msg)
                    elif(cursor[2]!=userName):
                        msg = "Not the post owner.\r\n"
                        SEND(CMD = msg)
                    else:
                        new = recvMsg.split("--content ",1)[1]
                        cursor = cur.execute('update post set Content = ? where ID = ? ;',(new,msgArr[1]))
                        conn.commit()
                        msg = "updContent# "+ bucketName + " Update successfully.\r\n"
                        SEND(CMD = msg)
                else:
                    msg = "Please login first.\r\n"
                    SEND(CMD = msg)
            else:
                msg = "update-post <post-id> --title/content <new>.\r\n"
                SEND(CMD = msg)
        #   part of comment post
        elif(len(msgArr) > 2 and msgArr[0]== "comment" ):
            if(isLogin == 1):
                cursor = cur.execute('select * from post where ID = ? ;',(msgArr[1],)).fetchone()
                if(cursor==None):
                    msg = "Post does not exist.\r\n"
                    SEND(CMD = msg)
                elif(cursor[6] != None ):
                    comment = cursor[6] + userName+ " :" + recvMsg.split(msgArr[1],1)[1]
                    cursor = cur.execute('update post set Comment = ? where ID = ? ;',(comment,msgArr[1]))
                    conn.commit()
                    cursor = cur.execute('select * from post where ID = ? ;',(msgArr[1],)).fetchone()
                    msg = "ComSuc "+ cursor[7]+ " " + userName + " Comment successfully.\r\n"
                    SEND(CMD = msg)
                else:
                    comment = userName+ " :" + recvMsg.split(msgArr[1],1)[1]
                    cursor = cur.execute('update post set Comment = ? where ID = ? ;',(comment,msgArr[1]))
                    conn.commit()
                    cursor = cur.execute('select * from post where ID = ? ;',(msgArr[1],)).fetchone()
                    msg = "ComSuc "+ cursor[7]+" "+ userName + " Comment successfully.\r\n"
                    SEND(CMD = msg)

            else:
                msg = "Please login first.\r\n"
                SEND(CMD = msg)
        #   part of mail to
        elif(len(msgArr) > 5 and msgArr[0]== "mail-to" ):
            msgArr = recvMsg.split()
            if(isLogin == 1):
                cursor = cur.execute('select * from user where Name = ? ;',(msgArr[1],)).fetchone()
                print cursor
                if(cursor==None):
                    msg = msgArr[1] +" does not exist.\r\n"
                    SEND(CMD = msg)
                elif(msgArr[2] != "--subject" or recvMsg.rfind(" --content ")== -1):
                    msg = "User type error format"
                    print msg
                    SEND(CMD = msg)
                else:
                    recvBucketName = cursor[4]
                    sql = 'insert into mail("Subject","Sender","Receiver","DT")values(?,?,?,?);'
                    now = datetime.datetime.now()
                    dateStr = str(now.month) + "/" + str(now.day)
                    msgSC = recvMsg.split("--subject ",1)[1].split(" --content ",1)
                    cursor = cur.execute(sql,(msgSC[0],userName,msgArr[1],dateStr,))
                    conn.commit()

                    cursor = cur.execute('select * from mail where Subject = ? ;',(msgSC[0],)).fetchone()
                    msg = "MailSuc# "+ recvBucketName + " "+ str(cursor[0]) + " Sent successfully.\r\n"
                    SEND(CMD = msg)

            else:
                msg = "Please login first.\r\n"
                SEND(CMD = msg)
    #   part of list-mail
        elif(msgArr[0]== "list-mail" and len(msgArr) == 1):
            if(isLogin == 1):
                cursor = cur.execute('select * from mail where Receiver = ? ;',(userName,)).fetchone()
                if(cursor != None):
                    msg = "{:^7} {:^20} {:^20} {:^9}\r\n\r\n".format("ID","Subject","From","Date")
                    cursor = cur.execute('select * from mail where Receiver = ? ;',(userName,))
                    i = 1
                    for row in cursor:
                        msg = msg+"{:>7} {:^20} {:^20} {:^9}\r\n\r\n".format(str(i),row[1],row[2],row[4])
                        i = i+1
                    SEND(CMD = msg)
                else:
                    msg = "{:^7} {:^20} {:^20} {:^9}\r\n".format("ID","Subject","From","Date")
                    SEND(CMD = msg)
            else:
                msg = "Please login first.\r\n"
                SEND(CMD=msg)
    #   part of retr-mail
        elif(msgArr[0]== "retr-mail" and len(msgArr) == 2):
            if(isLogin == 1):
                cursor = cur.execute('select * from mail where Receiver = ? ;',(userName,)).fetchone()
                if(cursor != None):
                    msg = "{:^7} {:^20} {:^20} {:^9}\r\n\r\n".format("ID","Subject","From","Date")
                    cursor = cur.execute('select * from mail where Receiver = ? ;',(userName,)).fetchall()
                    mailNum = int(msgArr[1])
                    if(len(cursor) < mailNum ):
                        msg = "No such mail.\r\n"
                        SEND(CMD = msg)
                    else:
                        msg = "showMail# "
                        index = mailNum -1
                        msg = msg+str(cursor[index][0]) + "# #"
                        msg = msg+ "Subject : {:>15}\r\nFrom    : {:>15}\r\nDate    : {:>15}\r\n---".format(cursor[index][1],cursor[index][2],cursor[index][4])
                        print msg
                        SEND(CMD = msg)
                else:
                    msg = "No such mail.\r\n"
                    SEND(CMD = msg)
            else:
                msg = "Please login first.\r\n"
                SEND(CMD=msg)
    #   part of delete-mail
        elif(msgArr[0]== "delete-mail" and len(msgArr) == 2):
            if(isLogin == 1):
                cursor = cur.execute('select * from mail where Receiver = ? ;',(userName,)).fetchone()
                if(cursor != None):
                    msg = "{:^7} {:^20} {:^20} {:^9}\r\n\r\n".format("ID","Subject","From","Date")
                    cursor = cur.execute('select * from mail where Receiver = ? ;',(userName,)).fetchall()
                    mailNum = int(msgArr[1])
                    if(len(cursor) < mailNum ):
                        msg = "No such mail.\r\n"
                        SEND(CMD = msg)
                    else:
                        msg = "delMail# "
                        index = mailNum -1
                        msg = msg+str(cursor[index][0]) + "# #" + "Mail deleted.\r\n"
                        cursordel = cur.execute('delete from mail where ID = ? ;',(cursor[index][0],))
                        conn.commit()
                        print msg
                        SEND(CMD = msg)
                else:
                    msg = "No such mail.\r\n"
                    SEND(CMD = msg)
            else:
                msg = "Please login first.\r\n"
                SEND(CMD=msg)
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
