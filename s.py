import socket
import traceback
from threading import Thread

import time

import Parser
import sys


class Client:
    def __init__(self, conn, addr):
        self.connection = conn
        self.address = addr
        self.username = ""
        self.isActive = True
        try:
            self.thread = Thread(target=self.manageConnection).start()
        except:
            print("thread did not start")
            traceback.print_exc()

    def sendMessage(self, frame):
        self.connection.sendall(frame)

    def manageConnection(self):
        while self.isActive:
            data = Parser.receiveFrame(self.connection)
            userName, msgTime, msgText, flagsArray = Parser.parseInput(data)  # Calling the parser

            if any("time" == s for s in flagsArray):
                self.sendMessage(frame=Parser.createFrame("server", "real time to return"))
            if any("ping" == s for s in flagsArray):
                self.sendMessage(frame=Parser.createFrame("server", "pong"))
            if any("count" == s for s in flagsArray):
                self.sendMessage(frame=Parser.createFrame("server", "there is "+str(len(buffer))+" messages in the buffer"))
            if any("new" == s for s in flagsArray):
                self.broadcast(frame=Parser.createFrame("server", userName + " has join the chat"))
                #time.sleep(2)
                self.username = userName
                for f in buffer:
                    self.sendMessage(frame=f)
            if any("who" == s for s in flagsArray):
                str = "Online :"
                for c in clientsArray:
                    if c != self:
                        str += c.username+",  "
                self.sendMessage(frame=Parser.createFrame("server", str))
            if any("quit" == s for s in flagsArray):
                self.isActive = False
                self.broadcast(Parser.createFrame("server", userName + " join has left the chat : " + msgText))
                clientsArray.remove(self)
                self.sendMessage(frame=Parser.createFrame("server", "@exit"))
            if flagsArray == ['']:
                buffer.append(data)
                self.broadcast(data)
            else:
                for f in flagsArray:
                    if any(f == c.username for c in clientsArray):
                        c.sendMessage(data)
            print("from " + userName + " at " + msgTime + " :")
            print("\t" + msgText)

    def broadcast(self, frame):
        for c in clientsArray:
            if c != self:
                c.sendMessage(frame=frame)


HOST = '127.0.0.1'
PORT = 50007
chatActive = True
clientsArray = []
buffer = []
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    s.bind((HOST, PORT))
except:
    print("Bind failed")
    sys.exit()
s.listen(100)  # 100 clients max
while chatActive:
    conn, addr = s.accept()
    clientsArray.append(Client(conn=conn, addr=addr))