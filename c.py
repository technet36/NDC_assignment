
# Echo client program
import socket
import hashlib
import re
import time

HOST = '127.0.0.1'    # The remote host
PORT = 50007          # The same port as used by the server


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))


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
    return myName, myTime, textMsg, myFlags


def createFrame (userName, userInput):
    metaTag = "<meta>" + userName + "-" + str(int(time.time())) + "</meta>"
    hashTag = "<hash>" + hashlib.sha512(userInput.encode()).hexdigest() + "</hash>"
    #allWords = userInput.split(" ")
    cmdArray = re.findall(r'@(\w+)', userInput)
    myFlags = "-".join(cmdArray)
    allFrame = metaTag + "<msg>" + userInput + "-"+myFlags+"</msg>" + hashTag
    return allFrame




print "user name:"
name = raw_input()
text = createFrame(name, "@new")
s.sendall(text)
data = s.recv(80000)

userName, serverTime, msgText, flagsArray = parseInput(data)
print("from " + userName + " at " + serverTime + " :")
print("\t" + msgText)

isActive = True
while isActive:

    print "msg :"
    userInput = raw_input()
    text = createFrame(name, userInput)

    s.sendall(text)
    data = s.recv(80000)
    userName, serverTime, msgText, flagsArray = parseInput(data)
    print("from " + userName + " at " + serverTime + " :")
    print("\t" + msgText)

    if "@quit" in userInput:
        isActive = False

s.close()
