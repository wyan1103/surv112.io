import socket
import threading
from queue import Queue

import pygame, random
import pygame.gfxdraw
from Player import Player
from Nature import *
from Items import *
from Weapons import *
from Framework import PygameGame
from Bot import *
from ZombieBot import *

windowWidth = 600
windowHeight = 600

class Game(PygameGame):

    def init(self):
        # self.server, self.serverMsg = self.setUpServer()
        pygame.font.init()
        Weapon.init()

        self.mapSize = 3000
        # self.scrollX, self.scrollY = self.getRandomCoordinates(self.mapSize)
        self.scrollX, self.scrollY = 300, 300

        self.bushGroup = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()      # stuff the player can run into
        self.items = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()

        self.createMap()
        self.player = Player(self.scrollX, self.scrollY, PLAYER_RADIUS)
        self.playerGroup = pygame.sprite.Group(self.player)
        self.allPlayers = pygame.sprite.Group(self.player)
        self.otherPlayers = pygame.sprite.Group()

        self.bots = pygame.sprite.Group()
        self.initBots(self.player.x, self.player.y)

        self.pauseBullets = False
        self.openInventory = False


        # self.initBushes()
        # self.initTrees()
        # self.initHealth()
        # self.initAmmo()
        # self.initBots()

        self.items.add(WeaponItem('9mm', 400, 250))

    def mouseMotion(self, x, y):
        self.player.rotate(x + self.scrollX, y + self.scrollY)

    def mousePressed(self, x, y, button):

        # on left click
        if button == 1:
            # shoot the gun if not in inventory
            if not self.openInventory and self.player.equippedGun is not None:
                bullet = self.player.shoot(x + self.scrollX, y + self.scrollY, pygame.time.get_ticks())
                if bullet is not None:
                    self.bullets.add(bullet)

            if self.openInventory:
                for space in self.inventorySpaces:
                    if space.left < x < space.left + space.width and \
                            space.top < y < space.top + space.height:
                        index = self.inventorySpaces.index(space)
                        if len(self.player.inventory) > index:
                            item = self.player.inventory[index]
                            self.player.useItem(item, pygame.time.get_ticks())

        # on right click
        if button == 3:
            if self.openInventory:
                # check if dropping inventory items
                for space in self.inventorySpaces:
                    if space.left < x < space.left + space.width and \
                       space.top < y < space.top + space.height:
                        index = self.inventorySpaces.index(space)
                        if len(self.player.inventory) > index:
                            self.dropItem(self.player.inventory[index])
                # check if dropping ammo
                for i, space in enumerate(self.inventoryAmmoSpaces):
                    if space.left < x < space.left + space.width and \
                       space.top < y < space.top + space.height:
                        ammoTypes = ['9mm', '7.62', '5.56', '12g']
                        type = ammoTypes[i]
                        self.player.dropAmmo(type, self.items)
                # check if dropping weapons
                primary = self.primaryRect
                secondary = self.secondaryRect
                if primary.left < x < primary.left + primary.width and \
                        primary.top < y < primary.top + primary.height:
                    self.dropWeapon(1)
                elif secondary.left < secondary.left + secondary.width and \
                     secondary.top < y < secondary.top + secondary.height:
                    self.dropWeapon(2)



    def keyPressed(self, keyCode, mod):
        if keyCode == pygame.K_f:
            itemCollisions = pygame.sprite.groupcollide(self.playerGroup, self.items, False, False)
            if self.player in itemCollisions:
                currentWeapon = self.player.equippedGun
                item = itemCollisions[self.player][0]
                pickedUp = self.player.pickUpItem(item, self.items)
                if pickedUp:
                    self.items.remove(item)
                    if isinstance(item, WeaponItem) and currentWeapon is not None:
                        self.dropWeapon(3, currentWeapon)

        if keyCode == pygame.K_i:
            self.openInventory = not self.openInventory

        if keyCode == pygame.K_r:
            self.player.startReload(pygame.time.get_ticks())

        if keyCode == pygame.K_p:
            self.pauseBullets = True
        if keyCode == pygame.K_o:
            self.pauseBullets = False


    def timerFired(self, dt):
        self.scrollX, self.scrollY = self.player.x - windowWidth//2, self.player.y - windowHeight//2
        self.player.update(self.isKeyPressed, pygame.time.get_ticks(), self.obstacles, self.scrollX, self.scrollY)
        self.otherPlayers.update(self.scrollX, self.scrollY)
        self.bushGroup.update(self.scrollX, self.scrollY)
        self.obstacles.update(self.scrollX, self.scrollY)
        self.items.update(self.scrollX, self.scrollY)
        self.bots.update(self.scrollX, self.scrollY)
        for bot in self.bots:
            bot.move(self.obstacles, self.bots, self.player)

        # move and check all bullets in the game (if they're not paused)
        if not self.pauseBullets:
            self.bullets.update(self.scrollX, self.scrollY)
            self.checkBulletCollisions()

            # delete bullets that have gone too far
            for bullet in self.bullets:
                if bullet.distanceTravelled > 500:
                    self.bullets.remove(bullet)

        # execute a random action of the bot
        for bot in self.otherPlayers:
            bot.botAction(self.obstacles, pygame.time.get_ticks(), self.bullets)

        # self.server.send(f"playerPos {self.player.PID} {self.player.x} {self.player.y}")

        # self.receiveMessage()


    def redrawAll(self, screen):
        self.drawGridLines(screen)
        self.items.draw(screen)
        self.bullets.draw(screen)
        self.obstacles.draw(screen)
        self.bots.draw(screen)
        self.otherPlayers.draw(screen)
        if self.player.equippedGun is not None:
            gunGroup = pygame.sprite.Group(self.player.equippedGun)
            gunGroup.draw(screen)
        self.playerGroup.draw(screen)
        self.bushGroup.draw(screen)

        if self.openInventory:
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

    def displayInventory(self, screen):
        self.isInventory = True
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
        self.primaryRect, self.secondaryRect = primaryRect, secondaryRect

        pygame.draw.rect(screen, lightGray, secondaryRect)
        pygame.draw.rect(screen, black, secondaryRect, 3)

        itemsTop = primaryRect.top - 10
        itemsLeft = primaryRect.right + 20
        itemsWidth = (invRect.right - primaryRect.right- 20) / 4 - 20
        itemsHeight = (secondaryRect.bottom - primaryRect.top + 40) / 3 - 20

        # draw item display
        self.inventorySpaces = []
        for r in range(3):
            for c in range(4):
                itemsRect = pygame.Rect(itemsLeft, itemsTop, itemsWidth, itemsHeight)
                self.inventorySpaces.append(itemsRect)
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
        self.inventoryAmmoSpaces = []
        for type, color in AMMO_COLORS.items():
            margin = 10
            ammoRadius = 15

            boxRect = pygame.Rect(left, top, width, 2 * (margin + ammoRadius))
            pygame.draw.rect(screen, lightGray, boxRect)
            pygame.draw.rect(screen, black, boxRect, 3)
            Ammo.drawItem(screen, left+margin, top+margin, color, 15)
            self.inventoryAmmoSpaces.append(boxRect)

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
        b1 = Bush(100, 200, BUSH_RADIUS)
        b2 = Bush(200, 100, BUSH_RADIUS)
        self.bushGroup.add(b1, b2)

    def initTrees(self):
        t1 = Tree(200, 500, TREE_RADIUS)
        t2 = Tree(500, 400, TREE_RADIUS)
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

    def dropItem(self, item, remove=True):
        item.x, item.y = self.player.x, self.player.y
        xSpeed = (random.random() - 0.5) * 20
        ySpeed = (random.random() - 0.5) * 20
        item.dx, item.dy = xSpeed, ySpeed
        self.items.add(item)
        if remove:
            try: self.player.inventory.remove(item)
            except: pass

    def dropWeapon(self, num, item=None):
        xSpeed = (random.random() - 0.5) * 20
        ySpeed = (random.random() - 0.5) * 20

        if item is not None:    # not dropping from player inventory
            newItem = item.createWeaponItem(self.player.x, self.player.y)
            newItem.dx, newItem.dy = xSpeed, ySpeed
            self.items.add(newItem)

        if num == 1 and self.player.primaryGun is not None:
            self.items.add(WeaponItem(self.player.primaryGun.type, self.player.x, self.player.y,
                                      ITEM_RADIUS, xSpeed, ySpeed))
            if self.player.equippedGun == self.player.primaryGun:
                self.player.equippedGun = None
            self.player.primaryGun = None

        if num == 2 and self.player.secondaryGun is not None:
            self.items.add(WeaponItem(self.player.secondaryGun.type, self.player.x, self.player.y,
                                      ITEM_RADIUS, xSpeed, ySpeed))
            if self.player.equippedGun == self.player.secondaryGun:
                self.player.equippedGun = None
            self.player.secondaryGun = None

    def checkBulletCollisions(self):
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
            player[0].takeDmg(bullet.dmg)


    def initBots(self, playerX, playerY):

        b1 = ZombieBot(playerX + 300, playerY + 100)
        b2 = ZombieBot(playerX + 200, playerY - 100)
        # b3 = ZombieBot(playerX + 500, playerY + 100)
        # b4 = ZombieBot(playerX + 200, playerY + 100)
        self.bots.add(b1, b2)


    def createMap(self):
        mapSize = self.mapSize
        treeCount = 20
        bushCount = 50
        medKitCount = 10
        bandageCount = 30
        weaponCount = 15
        ammoCount = 60
        ammoTypes = ['9mm', '7.62', '5.56', '12g']

        for i in range(treeCount):
            x, y = self.getRandomCoordinates(mapSize)
            tree = Tree(x, y, TREE_RADIUS)
            self.obstacles.add(tree)

        for i in range(bushCount):
            x, y = self.getRandomCoordinates(mapSize)
            bush = Bush(x, y, BUSH_RADIUS)
            self.bushGroup.add(bush)
            # undo the bush creation if it spawned inside an obstacle
            while bush in pygame.sprite.groupcollide(self.bushGroup, self.obstacles, True, False):
                x, y = self.getRandomCoordinates(mapSize)
                bush = Bush(x, y, BUSH_RADIUS)
                self.bushGroup.add(bush)

        for i in range(medKitCount):
            x, y = self.getRandomCoordinates(mapSize)
            item = MedKit(x, y)
            self.items.add(item)
            if item in pygame.sprite.groupcollide(self.items, self.obstacles,True, False):
                i -= 1

        for i in range(weaponCount):
            x, y = self.getRandomCoordinates(mapSize)
            item = Bandage(x, y)
            self.items.add(item)
            while item in pygame.sprite.groupcollide(self.items, self.obstacles,True, False):
                x, y = self.getRandomCoordinates(mapSize)
                item = Bandage(x, y)
                self.items.add(item)

        for i in range(bandageCount):
            x, y = self.getRandomCoordinates(mapSize)
            weaponType = random.choice(ammoTypes)
            item = WeaponItem(weaponType, x, y)
            self.items.add(item)
            while item in pygame.sprite.groupcollide(self.items, self.obstacles,True, False):
                x, y = self.getRandomCoordinates(mapSize)
                weaponType = random.choice(ammoTypes)
                item = WeaponItem(weaponType, x, y)
                self.items.add(item)

        for i in range(ammoCount):
            x, y = self.getRandomCoordinates(mapSize)
            ammoType = random.choice(ammoTypes)
            item = Ammo(ammoType, x, y)
            self.items.add(item)
            while item in pygame.sprite.groupcollide(self.items, self.obstacles,True, False):
                x, y = self.getRandomCoordinates(mapSize)
                ammoType = random.choice(ammoTypes)
                item = Ammo(ammoType, x, y)
                self.items.add(item)

    def getRandomCoordinates(self, mapSize):
        x = random.random() * 3000
        y = random.random() * 3000
        return x, y

Game(600, 600).run()
