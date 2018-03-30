import socket
import traceback
from threading import Thread
import Queue
import hashlib
import re
import time
import sys


def parseMeta (metaString):
    myMetaArray = metaString.split("-")
    myMetaArray[1] = time.strftime("%a %d/%m/%Y  %H:%M:%S", time.localtime(float(int(myMetaArray[1]))))
    return myMetaArray


def parseCore (coreString):
    myCoreArray = coreString.split("-")

    return myCoreArray


def get(tagName, data):
    return re.search(r"<"+tagName+">(.*)</"+tagName+">", data).group(1)


def parseInput(data):

    #data format <user>toto</user><msg>'some text'-flag1-flag2</msg><hash>951D753E6842</hash>

    # format <cmd>'some text'-flag1-flag2-myHash789456</cmd>
    meta = get("meta", data)
    myHash = get("hash", data)
    core = get("msg", data)

    myMessageArray = parseCore(core)
    textMsg = myMessageArray[0]
    myFlags = myMessageArray[1:]

    myMetaArray = parseMeta(meta)
    myName = myMetaArray[0]
    myTime = myMetaArray[-1]

    if myHash != hashlib.sha512(textMsg.encode()).hexdigest():
        print "Error : hash not equals"
        exit(0)
    else:
        print "Hash ok"

    return myName, myTime, textMsg, myFlags



def createFrame (text):
    metaTag = "<meta>server-" + str(int(time.time())) + "</meta>"
    hashTag = "<hash>" + hashlib.sha512(text.encode()).hexdigest() + "</hash>"
    allWords = text.split(" ")
    cmdArray = re.findall(r'@(\w+)', text)
    myFlags = "-".join(cmdArray)
    allFrame = metaTag + "<msg>" + text + "-"+myFlags+"</msg>" + hashTag
    return allFrame


def manageConnection(conn, addr):
    isActive = True
    while isActive:
        data = conn.recv(1024)
        userName, msgTime, msgText, flagsArray = parseInput(data)# Calling the parser

        response = "recieved"

        if any("time" == s for s in flagsArray):
            response = " real time to return"
        if any("ping" == s for s in flagsArray):
            response = "pong"
        if any("count" == s for s in flagsArray):
            response = "there is 3 message in the buffer"
        if any("new" == s for s in flagsArray):
            response = userName + " is now connected"
        if any("quit" == s for s in flagsArray):
            isActive = False
            response = userName + " left the chat"

        print("from " + userName + " at " + msgTime + " :")
        print("\t" + msgText)
        conn.sendall(createFrame(response))
    conn.close()


HOST = '127.0.0.1'
PORT = 50007
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    s.bind((HOST, PORT))
except:
    print("Bind failed")
    sys.exit()
s.listen(5)  # 5 clients max
while 1:
    conn, addr = s.accept()

    try:
        Thread(target=manageConnection, args=(conn, addr)).start()
    except:
        print("thread did not start")
        traceback.print_exc()
