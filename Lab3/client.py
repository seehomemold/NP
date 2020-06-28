import socket
import os
import boto3
import time
import datetime

def RECEIVE():
    while True:
        try:
            msg_get = s.recv(1024).decode('utf-8')
            return msg_get
        except:
            pass

def SEND(CMD):
    while True:
        try:
            s.send(CMD.encode('utf-8'))
            break
        except:
            pass

def CmdLine():
    cmd = raw_input("% ")
    test = cmd.replace(' ', '')
    while test == "":
        cmd = input("% ")
        test = cmd.replace(' ', '')
    SEND(CMD = cmd)
    return cmd

def MKDIR():
    Path = ".data"
    if not os.path.exists(Path):
        os.mkdir(Path)
    Ppost = ".data/post"
    Pcomment = ".data/comment"
    Pmail = ".data/mail"
    if not os.path.exists(Ppost):
        os.mkdir(Ppost)
    if not os.path.exists(Pcomment):
        os.mkdir(Pcomment)
    if not os.path.exists(Pmail):
        os.mkdir(Pmail)

Host = "18.204.221.141"
Port = 3110

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((Host,Port))
s.setblocking(0)
print( RECEIVE())
s3 = boto3.resource('s3')
targetBucket = None
userName = None
MKDIR()

while True:
    cmd = CmdLine();
    if cmd == "exit":
        break
    elif cmd.startswith("register"):
        get = RECEIVE()
        if(get.startswith("success")):
            get = get.replace("success ","",1)
            print(get)
            msgArr = cmd.split()
            bucketName = "lab3user" + str(time.time())
            SEND(CMD = bucketName)
            s3.create_bucket(Bucket = bucketName)
        else:
            print(get)
    elif cmd.startswith("login"):
        get = RECEIVE()
        if(get.startswith("lab3user")):
            splitArr = get.split("#^#")
            print splitArr[1]
            userName = splitArr[1].replace("Welcome ","",1)
            targetBucket = s3.Bucket(splitArr[0])
        else:
            print(get)
    elif cmd.startswith("logout"):
        targetBucket = None
        userName = None
        get = RECEIVE()
        print(get)
    elif cmd.startswith("create-post "):
        get = RECEIVE()
        if(get.startswith("mark ")):
            get = get.replace("mark ","",1)
            postID = get.split()[0]
            get = get.replace(postID+" ","",1)
            print get
            msgTC = cmd.split("--title ",1)[1].split(" --content ",1)
            ContentArr =  msgTC[1].replace("<br>","\r\n")
            Content = ""
            for iter_content in ContentArr:
                ## print iter_content
                Content = Content + iter_content
            fp = open(".data/post/P{}".format(postID),"w")
            fp.write(Content)
            fp.close()
            os.system("echo "" >> .data/comment/C{}".format(postID))
            targetBucket.upload_file(".data/post/P{}".format(postID), "P{}".format(postID))
            targetBucket.upload_file(".data/comment/C{}".format(postID), "C{}".format(postID))
        else:
            print get
    elif cmd.startswith("read "):
        get = RECEIVE()
        if(get.startswith("readSuc ")):
            get = get.replace("readSuc ","",1)
            postID = cmd.split()[1]
            bucketName = get.split()[0]
            get = get.replace(bucketName+" ","",1)
            print get
            readBucket = s3.Bucket(bucketName)
            target_obj1 = readBucket.Object("P{}".format(postID))
            objContent = target_obj1.get()["Body"].read().decode()
            print(objContent)
            writeLine = "-----"
            print writeLine
            target_obj2 = readBucket.Object("C{}".format(postID))
            objComment = target_obj2.get()["Body"].read().decode()
            print(objComment)
        else:
            print get
    elif cmd.startswith("delete-post "):
        get = RECEIVE()
        if(get.startswith("del# ")):
            get = get.replace("del# ","",1)
            bucketName = get.split()[0]
            get = get.replace(bucketName+" ","",1)
            postID = cmd.split()[1]
            readBucket = s3.Bucket(bucketName)
            os.remove(".data/post/P{}".format(postID))
            os.remove(".data/comment/C{}".format(postID))
            target_obj1 = readBucket.Object("P{}".format(postID))
            target_obj1.delete()
            target_obj2 = readBucket.Object("C{}".format(postID))
            target_obj2.delete()
            print get
        else:
            print get
    elif cmd.startswith("update-post "):
        get = RECEIVE()
        if(get.startswith("updContent# ")):
            get = get.replace("updContent# ","",1)
            bucketName = get.split()[0]
            get = get.replace(bucketName+" ","",1)
            postID = cmd.split()[1]
            readBucket = s3.Bucket(bucketName)
            if os.path.isfile(".data/post/P{}"):
                os.remove(".data/post/P{}".format(postID))
            target_obj1 = readBucket.Object("P{}".format(postID))
            msgTitle = cmd.split("--content ",1)[1]
            ContentArr = msgTitle.replace("<br>","\r\n")
            Content = ""
            for iter_content in ContentArr:
                ## print iter_content
                Content = Content + iter_content
            fp = open(".data/post/P{}".format(postID),"w")
            fp.write(Content)
            fp.close()
            targetBucket.upload_file(".data/post/P{}".format(postID), "P{}".format(postID))
            print get
        else:
            print get
    elif cmd.startswith("comment "):
        get = RECEIVE()
        if(get.startswith("ComSuc ")):
            get = get.replace("ComSuc ","",1)
            bucketName = get.split()[0]
            get = get.replace(bucketName+" ","",1)
            whoComment = get.split()[0]
            get = get.replace(whoComment+" ","",1)


            postID = cmd.split()[1]
            readBucket = s3.Bucket(bucketName)
            target_obj1 = readBucket.Object("C{}".format(postID))
            objComment = target_obj1.get()["Body"].read().decode()
            objComment = objComment + whoComment + "\t: "

            msgComment = cmd.replace("comment "+postID+" ","",1)
            ContentArr = msgComment.replace("<br>","\r\n")
            Content = ""
            for iter_content in ContentArr:
                Content = Content + iter_content
            if os.path.isfile("data./comment/C{}".format(postID)):
                os.remove(".data/comment/C{}".format(postID))
            fp = open(".data/comment/C{}".format(postID),"w")
            fp.write(objComment)
            fp.write(Content)
            fp.close()
            readBucket.upload_file(".data/comment/C{}".format(postID), "C{}".format(postID))
            print get
        else:
            print get
    elif cmd.startswith("mail-to "):
        get = RECEIVE()
        if(get.startswith("MailSuc# ")):
            get = get.replace("MailSuc# ","",1)
            bucketName = get.split()[0]
            MID = get.split()[1]
            get = get.replace(bucketName+" ","",1)
            get = get.replace(MID+" ","",1)
            readBucket = s3.Bucket(bucketName)
            msgSC = cmd.split("--subject ",1)[1].split(" --content ",1)
            ContentArr = msgSC[1].replace("<br>","\r\n")
            os.system("echo {} > ./.data/mail/M".format(msgSC[0]))
            Content = ""
            for iter_content in ContentArr:
                Content = Content + iter_content
            fp = open(".data/mail/M","w")
            fp.write(Content)
            fp.close()
            readBucket.upload_file(".data/mail/M", "M{}".format(MID))
            print get
        else:
            print get
    elif cmd.startswith("retr-mail "):
        get = RECEIVE()
        if(get.startswith("showMail# ")):
            get = get.replace("showMail# ","",1)
            MID = get.split("# #")[0]
            get = get.replace(MID+"# #","",1)
            target_obj1 = targetBucket.Object("M{}".format(MID))
            objContent = target_obj1.get()["Body"].read().decode()
            print(get)
            print(objContent)
            writeLine = "-----"
            print(writeLine)
        else:
            print get
    elif cmd.startswith("delete-mail "):
        get = RECEIVE()
        if(get.startswith("delMail# ")):
            get = get.replace("delMail# ","",1)
            MID = get.split("# #")[0]
            get = get.replace(MID+"# #","",1)

            target_obj1 = targetBucket.Object("M{}".format(MID))
            target_obj1.delete()
            print(get)
        else:
            print get
    else:
        get = RECEIVE()
        print(get)

