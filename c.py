import socket
import Parser
from threading import Thread

HOST = '127.0.0.1'  # The remote host
PORT = 50007  # The same port as used by the server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))


def receptionThread(connection, temp):
    global isActive
    while isActive:
        data = Parser.receiveFrame(connection)
        userName, msgTime, msgText, flagsArray = Parser.parseInput(data)  # Calling the parser

        if any("exit" == s for s in flagsArray):
            isActive = False
            connection.close()  # shutdown is no longer required
        else:
            print("from " + userName + " at " + msgTime + " :")
            print("\t" + msgText)


print "user name:"
name = raw_input()
text = Parser.createFrame(name, "@new")
s.sendall(text)

isActive = True
while isActive:
    Thread(target=receptionThread, args=(s, "toto")).start()

    print "msg :"
    userInput = raw_input()
    text = Parser.createFrame(name, userInput)

    s.sendall(text)
    if "@quit" in userInput:
        isActive = False
        print("You've been disconnected")
print("THE END")
