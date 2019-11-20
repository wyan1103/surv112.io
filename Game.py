import socket
import threading
from queue import Queue

import pygame
import pygame.gfxdraw
from Player import Player
from Nature import *
from Items import *
from Weapons import *
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
        pygame.font.init()

        Weapon.init()
        self.initX, self.initY = 300, 300
        self.player = Player(self.initX, self.initY, 40)
        self.scrollX, self.scrollY = 0, 0
        self.pauseBullets = False

        self.playerGroup = pygame.sprite.Group(self.player)
        self.allPlayers = pygame.sprite.Group(self.player)

        self.bushGroup = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()      # stuff the player can run into
        self.items = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()

        self.initBushes()
        self.initTrees()
        self.initHealth()
        self.initAmmo()

        Weapon.init()
        self.items.add(WeaponItem('9mm', 400, 250))

    def mouseMotion(self, x, y):
        self.player.rotate(x + self.scrollX, y + self.scrollY)

    def mousePressed(self, x, y):
        if self.player.equippedGun is not None:
            bullet = self.player.shoot(x + self.scrollX, y + self.scrollY, pygame.time.get_ticks())
            if bullet is not None:
                self.bullets.add(bullet)

    def keyPressed(self, keyCode, mod):
        if keyCode == pygame.K_f:
            itemCollisions = pygame.sprite.groupcollide(self.playerGroup, self.items, False, False)
            if self.player in itemCollisions:
                item = itemCollisions[self.player][0]
                pickedUp = self.player.pickUpItem(item, self.items)
                if pickedUp:
                    self.items.remove(item)
        if keyCode == pygame.K_i:
            self.player.openInventory = not self.player.openInventory
        if keyCode == pygame.K_p:
            self.pauseBullets = True
        if keyCode == pygame.K_o:
            self.pauseBullets = False


    def timerFired(self, dt):
        self.scrollX, self.scrollY = self.player.x - self.initX, self.player.y - self.initY
        self.player.update(self.isKeyPressed, pygame.time.get_ticks(), self.obstacles, self.scrollX, self.scrollY)
        self.bushGroup.update(self.scrollX, self.scrollY)
        self.obstacles.update(self.scrollX, self.scrollY)
        self.items.update(self.scrollX, self.scrollY)

        if not self.pauseBullets:
            self.bullets.update(self.scrollX, self.scrollY)

            # check for collisions between bullets and walls
            bulletCollisions = pygame.sprite.groupcollide(self.bullets, self.obstacles, True, False)
            for bullet, target in bulletCollisions.items():
                target[0].hp -= bullet.dmg
                if target[0].hp <= 0:
                    self.obstacles.remove(target[0])

            bulletBushCollisions = pygame.sprite.groupcollide(self.bullets, self.bushGroup, False, False)
            for bullet, bush in bulletBushCollisions.items():
                if bush[0] not in bullet.bushesSeen:
                    bush[0].hp -= bullet.dmg
                    if bush[0].hp <= 0:
                        self.bushGroup.remove(bush[0])
                bullet.bushesSeen.add(bush[0])

            bulletPlayerCollisions = pygame.sprite.groupcollide(self.bullets, self.allPlayers, True, False)
            for bullet, player in bulletPlayerCollisions.items():
                player[0].hp -= bullet.dmg

            # delete bullets that have gone too far
            for bullet in self.bullets:
                if bullet.distanceTravelled > 500:
                    self.bullets.remove(bullet)

        # self.server.send(f"playerPos {self.player.PID} {self.player.x} {self.player.y}")

        # self.receiveMessage()


    def redrawAll(self, screen):
        self.drawGridLines(screen)
        self.items.draw(screen)
        self.bullets.draw(screen)
        if self.player.equippedGun is not None:
            gunGroup = pygame.sprite.Group(self.player.equippedGun)
            gunGroup.draw(screen)
        self.playerGroup.draw(screen)
        self.obstacles.draw(screen)
        self.bushGroup.draw(screen)

        if self.player.openInventory:
            self.displayInventory(screen)

        self.drawHealthBar(screen)

    def drawGridLines(self, screen):

        gridSize = 200
        scrollX = round(self.scrollX)
        scrollY = round(self.scrollY)
        lineScrollX = scrollX % gridSize
        lineScrollY = scrollY % gridSize

        for i in range(600):
            if (i + lineScrollX) % gridSize == 0:
                pygame.draw.line(screen, BLACK, (i, 0), (i, 600), 2)

        for i in range(600):
            if (i + lineScrollY) % gridSize == 0:
                pygame.draw.line(screen, BLACK, (0, i), (600, i), 2)


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

    def displayInventory(self, screen):
        leftMargin = 40
        topMargin = 100
        invWidth = self.width - 2*leftMargin
        invHeight = self.height - 2*topMargin
        invRect = pygame.Rect(leftMargin, topMargin, invWidth, invHeight)

        black = (0, 0, 0)
        darkGray = (166, 166, 166)
        lightGray = (217, 217, 217)

        # draw basic inventory layout
        pygame.draw.rect(screen, darkGray, invRect)
        pygame.draw.rect(screen, black, invRect, 5)

        # draw primary and secondary weapon displays
        primaryRect = pygame.Rect(leftMargin + 20, topMargin + 30, 2*invWidth/5, 2 * invHeight / 7)
        secondaryRect = pygame.Rect(leftMargin + 20, topMargin + 50 + invHeight/3, 2*invWidth/5, 2 * invHeight / 7)
        pygame.draw.rect(screen, lightGray, primaryRect)
        pygame.draw.rect(screen, black, primaryRect, 3)

        pygame.draw.rect(screen, lightGray, secondaryRect)
        pygame.draw.rect(screen, black, secondaryRect, 3)

        itemsTop = primaryRect.top - 10
        itemsLeft = primaryRect.right + 20
        itemsWidth = (invRect.right - primaryRect.right- 20) / 4 - 20
        itemsHeight = (secondaryRect.bottom - primaryRect.top + 40) / 3 - 20

        # draw item display
        for r in range(3):
            for c in range(4):
                itemsRect = pygame.Rect(itemsLeft, itemsTop, itemsWidth, itemsHeight)
                pygame.draw.rect(screen, lightGray, itemsRect)
                pygame.draw.rect(screen, black, itemsRect, 3)

                x, y = itemsRect.centerx, itemsRect.centery
                if 4*r+c < len(self.player.inventory):
                    item = self.player.inventory[4*r+c]
                    item.drawItem(screen, x, y, item.color, itemsWidth/3)

                itemsLeft += itemsWidth + 20
            itemsTop += itemsHeight + 20
            itemsLeft = primaryRect.right + 20

        if self.player.primaryGun is not None:
            self.player.primaryGun.drawWeapon(screen, primaryRect.centerx, primaryRect.centery,
                                              2*primaryRect.width/3, 2*primaryRect.height/3)

        # draw ammo display
        left = primaryRect.left
        top = invRect.bottom - 70
        width = (invWidth - 20) / 4 - 20
        for type, color in AMMO_COLORS.items():
            margin = 10
            ammoRadius = 15

            boxRect = pygame.Rect(left, top, width, 2 * (margin + ammoRadius))
            pygame.draw.rect(screen, lightGray, boxRect)
            pygame.draw.rect(screen, black, boxRect, 3)
            Ammo.drawItem(screen, left+margin, top+margin, color, 15)

            ammoFont = pygame.font.SysFont('Arial', 32, True, False)
            ammoSurface = ammoFont.render(str(self.player.ammo[type]), True, black)
            screen.blit(ammoSurface, (boxRect.left + 2 * (margin + ammoRadius), boxRect.top + 2*margin/3))

            left += 20 + width

    def drawHealthBar(self, screen):
        left = screen.get_rect().width / 4
        top = 9 * screen.get_rect().height / 10
        barWidth = screen.get_rect().width/2
        barHeight = screen.get_rect().height/20

        ratio = self.player.hp/100
        if ratio < 0: ratio = 0
        r, g, b = 255, 255 * math.sqrt(ratio), 255 * math.sqrt(ratio)
        pygame.draw.rect(screen, (r, g, b), pygame.Rect(left, top, barWidth * ratio, barHeight))
        pygame.draw.rect(screen, BLACK, pygame.Rect(left, top, barWidth, barHeight), 4)

    def initBushes(self):
        b1 = Bush(100, 200, 50)
        b2 = Bush(200, 100, 50)
        self.bushGroup.add(b1, b2)

    def initTrees(self):
        t1 = Tree(200, 500, 40)
        t2 = Tree(500, 400, 40)
        self.obstacles.add(t1, t2)

    def initHealth(self):
        h1 = MedKit(300, 500)
        h2 = MedKit(300, 100)
        self.items = pygame.sprite.Group(h1, h2)

    def initAmmo(self):
        a1 = Ammo('9mm', 500, 500)
        a2 = Ammo('9mm', 300, 300)
        a3 = Ammo('9mm', 400, 150, 50)
        self.items.add(a1, a2, a3)

Game(600, 600).run()
