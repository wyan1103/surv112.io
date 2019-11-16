import socket
import threading
from queue import Queue

import pygame
from Player import Player
from Nature import *
from Framework import PygameGame


class Game(PygameGame):

    # setUpServer() and handleServerMsg() taken from TP mentor demo code
    # https://drive.google.com/drive/folders/1W4xJyV0oqFcAP6SZNNIYXLYOYXOidEJu

    # @staticmethod
    # def setUpServer():
    #     HOST = "128.237.121.70"  # put your IP address here if playing on multiple computers
    #     PORT = 50003
    #
    #     server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     server.connect((HOST, PORT))
    #     print("connected to server")
    #
    #     serverMsg = Queue(100)
    #     threading.Thread(target=Game.handleServerMsg, args=(server, serverMsg)).start()
    #
    #     return server, serverMsg
    #
    # @staticmethod
    # def handleServerMsg(server, serverMsg):
    #     server.setblocking(1)
    #     msg = ""
    #     command = ""
    #     while True:
    #         msg += server.recv(10).decode("UTF-8")
    #         command = msg.split("\n")
    #         while len(command) > 1:
    #             readyMsg = command[0]
    #             msg = "\n".join(command[1:])
    #             serverMsg.put(readyMsg)
    #             command = msg.split("\n")

    def init(self):
        # self.server, self.serverMsg = self.setUpServer()
        self.player = Player(0, 0, 40)
        self.playerGroup = pygame.sprite.Group(self.player)
        self.otherPlayers = dict()
        self.obstacles = pygame.sprite.Group()
        self.initBushes()
        self.initTrees()

    def timerFired(self, dt):
        self.playerGroup.update(self.isKeyPressed, self.obstacles)
        self.bushGroup.update(self.isKeyPressed, self.player.x, self.player.y)
        self.treeGroup.update(self.isKeyPressed, self.player.x, self.player.y)

        # self.server.send(f"playerPos {self.player.PID} {self.player.x} {self.player.y}")

        self.receiveMessage()


    def redrawAll(self, screen):
        self.playerGroup.draw(screen)
        self.bushGroup.draw(screen)
        self.treeGroup.draw(screen)


    def receiveMessage(self):
        pass
        # while self.serverMsg.qsize() > 0:
        #     msg = self.serverMsg.get(False)
        #     try:
        #         print('received: ' + msg + '\n')
        #         msg = msg.split()
        #         command = msg[0]
        #
        #         if command == 'myIDis':
        #             myPID = msg[1]
        #             self.player.changePID(myPID)
        #
        #         elif command == 'newPlayer':
        #             newPID = msg[1]
        #             self.otherPlayers[newPID] = None
        #
        #         elif command == 'playerPos':
        #             pID = msg[1]
        #             x = int(msg[2])
        #             y = int(msg[3])
        #             self.otherPlayers[pID] = Player(x, y, 40)
        #
        #     except:
        #         print('D:')

    def initBushes(self):
        b1 = Bush(100, 200, 50)
        b2 = Bush(200, 100, 50)
        self.bushGroup = pygame.sprite.Group(b1, b2)

    def initTrees(self):
        t1 = Tree(400, 500, 40)
        t2 = Tree(500, 400, 40)
        self.treeGroup = pygame.sprite.Group(t1, t2)
        self.obstacles.add(t1, t2)


Game(600, 600).run()
