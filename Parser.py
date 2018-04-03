import hashlib
import re
import time


def parseMeta(metaString):
    myMetaArray = metaString.split("-")
    myMetaArray[1] = time.strftime("%a %d/%m/%Y  %H:%M:%S", time.localtime(float(int(myMetaArray[1]))))
    return myMetaArray


def parseCore(coreString):
    myCoreArray = coreString.split("-")

    return myCoreArray


def get(tagName, data):
    return re.search(r"<"+tagName+">(.*)</"+tagName+">", data).group(1)


def parseInput(data):

    #data format <user>toto-1570004</user><msg>'some text'-flag1-flag2</msg><hash>951D753E6842</hash>

    # format <cmd>'some text'-flag1-flag2-myHash789456</cmd>
    try:
        meta = get("meta", data)
        myHash = get("hash", data)
        core = get("msg", data)

        myMessageArray = parseCore(core)
        textMsg = myMessageArray[0]
        myFlags = myMessageArray[1:]

        myMetaArray = parseMeta(meta)
        myName = myMetaArray[0]
        myTime = myMetaArray[-1]
        if myHash != hashlib.sha512((data[13:-141]).encode()).hexdigest():
            print "Error : hash not equals"
            raise Exception("Error : hash not equals")
    except:
        print("error parser")
        print(data)
        return "error", "0", "//error//", []
    return myName, myTime, textMsg, myFlags


def createFrame(userName, userInput):
    metaTag = "<meta>" + userName + "-" + str(int(time.time())) + "</meta>"
    cmdArray = re.findall(r'@(\w+)', userInput)
    myFlags = "-".join(cmdArray)
    coreTag = "<msg>" + userInput + "-"+myFlags+"</msg>"
    hashTag = "<hash>" + hashlib.sha512((metaTag+coreTag).encode()).hexdigest() + "</hash>"

    allFrame = metaTag + coreTag + hashTag
    size = len(allFrame)
    size += 1000000
    sizeString = str(size)
    sizeString = sizeString[1:]
    sTag = "<s>"+sizeString+"</s>"
    return sTag+allFrame


def receiveFrame(connection):
    #<s>000000</s> size=13
    sizeFrame = connection.recv(13)
    dataSize = get("s", sizeFrame)
    size = int(dataSize)
    return sizeFrame+connection.recv(size)
