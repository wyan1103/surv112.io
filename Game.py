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
from ShootyBot import *
from ZombieBot import *
from Constants import *

class Game(PygameGame):

    @staticmethod
    def setMode(difficulty, gamemode):
        Game.difficulty = difficulty
        Game.gamemode = gamemode

    def init(self):
        # self.server, self.serverMsg = self.setUpServer()
        pygame.font.init()
        Weapon.init()
        Bush.init()
        Rock.init()
        TreeTop.init()

        self.scrollX, self.scrollY = self.getRandomCoordinates(MAPSIZE)

        self.borderWalls = pygame.sprite.Group()
        self.bushGroup = pygame.sprite.Group()
        self.treeTops = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()      # stuff the player can run into
        self.items = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.bots = pygame.sprite.Group()

        # self.createTestMap()  # uncomment for a test map with fixed objects
        self.createMap()        # uncomment for a randomized map

        self.allPlayers = pygame.sprite.Group(self.player)
        self.otherPlayers = pygame.sprite.Group()

        self.pauseBullets = False
        self.openInventory = False
        self.isWave = False
        self.wavesPassed = 0
        self.mouseDown = False
        self.mouseCoords = [0, 0]
        self.isPaused = False

        self.lastWave = pygame.time.get_ticks()
        self.waveCooldown = 15
        self.score = [0]    # list aliasing to allow the bot classes to update the list

    def mouseMotion(self, x, y):
        self.mouseCoords = [x, y]
        self.player.rotate(x + self.scrollX, y + self.scrollY)

    def mouseDragged(self, x, y):
        self.mouseCoords = [x, y]
        self.player.rotate(x + self.scrollX, y + self.scrollY)

    def mouseReleased(self, x, y):
        self.mouseDown = False

    def mousePressed(self, x, y, button):
        self.mouseDown = True
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
            if self.player.equippedGun is not None and \
                self.player.equippedGun.ammo < self.player.equippedGun.magSize:
                self.player.startReload(pygame.time.get_ticks())

        if keyCode == pygame.K_p:
            if not self.isPaused:
                self.pauseStartTime = pygame.time.get_ticks()
                self.player.isSlow = False
                self.player.itemInUse = None
                self.player.itemTimer = 0
            else:
                self.lastWave += pygame.time.get_ticks() - self.pauseStartTime
            self.isPaused = not self.isPaused

        if keyCode == pygame.K_ESCAPE:
            HomeScreen(windowWidth, windowHeight).run()

        if keyCode == pygame.K_COMMA:
            self.player.ammo = copy.deepcopy(self.player.ammoLimits)
            self.player.primaryGun = Weapon(self.player, 10, '9mm', 50, magSize=32, reloadTime=1500,
                                            bulletSpread=0.3, bulletSpeed=12, auto=True)
            self.player.secondaryGun = Weapon(self.player, 30, '7.62', 300, magSize=20, bulletSpread=0.1,
                                              bulletSpeed=20)
            self.player.equippedGun = self.player.primaryGun

        if keyCode == pygame.K_PERIOD:
            self.player.hp = 10**9

    def timerFired(self, dt):
        if self.isPaused:
            return

        if self.player.gameOver:
            self.isPaused = True

        if not self.isWave and pygame.time.get_ticks() - self.lastWave >= self.waveCooldown * 1000:
            self.spawnWave(self.player.x, self.player.y)

        if self.player.equippedGun is not None and self.mouseDown and self.player.equippedGun.auto:
            bullet = self.player.shoot(self.mouseCoords[0] + self.scrollX,
                                       self.mouseCoords[1] + self.scrollY, pygame.time.get_ticks())
            if bullet is not None:
                self.bullets.add(bullet)

        if self.isWave and len(self.bots) <= 0:
            self.wavesPassed += 1
            self.waveCooldown *= 0.8
            ZombieBot.finishWave()          # when all bots are dead, account for reward
            # print('WAVE OVER!')
            # print('\nBot Reward Table:', ZombieBot.dtpRewards, ZombieBot.rmcRewards, ZombieBot.rmdRewards)
            self.isWave = False
            self.lastWave = pygame.time.get_ticks()

        # update all the objects to their new scrolled positions
        self.scrollX, self.scrollY = self.player.x - windowWidth//2, self.player.y - windowHeight//2
        self.player.update(self.isKeyPressed, pygame.time.get_ticks(), self.obstacles, self.scrollX, self.scrollY)
        self.otherPlayers.update(self.scrollX, self.scrollY)
        self.bushGroup.update(self.scrollX, self.scrollY)
        self.treeTops.update(self.scrollX, self.scrollY)
        self.obstacles.update(self.scrollX, self.scrollY)
        self.items.update(self.scrollX, self.scrollY)
        self.bots.update(self.scrollX, self.scrollY)
        self.borderWalls.update(self.scrollX, self.scrollY)
        for bot in self.bots:
            bot.move(self.obstacles, self.bots, self.player, pygame.time.get_ticks(), self.score)
            if isinstance(bot, ShootyBot):
                bot.shoot(self.bullets, pygame.time.get_ticks())

        # move and check all bullets in the game
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
        self.bots.draw(screen)
        self.otherPlayers.draw(screen)
        if self.player.equippedGun is not None:
            gunGroup = pygame.sprite.Group(self.player.equippedGun)
            gunGroup.draw(screen)
        self.playerGroup.draw(screen)
        self.bushGroup.draw(screen)
        self.obstacles.draw(screen)
        self.treeTops.draw(screen)
        self.borderWalls.draw(screen)

        if self.openInventory:
            self.displayInventory(screen)
        self.drawHealthBar(screen)
        self.drawAmmoDisplay(screen)
        self.drawSlowTimer(screen)
        self.drawWaveTimer(screen)
        self.drawScore(screen)

        # draw the gameover screen
        if self.player.gameOver:
            self.drawGameOver(screen)


    def drawGameOver(self, screen):
        left = windowWidth // 4
        top = windowHeight // 3
        width = windowWidth // 2
        height = windowHeight // 3
        gameOverRect = pygame.Rect(left, top, width, height)
        pygame.gfxdraw.box(screen, gameOverRect, (26, 26, 26, 150))
        pygame.draw.rect(screen, (0, 0, 0), gameOverRect, 3)
        gameOverFont = pygame.font.SysFont("comicsansms", 48, True, True)
        gameOverText = gameOverFont.render(f"You Died!", True, (255, 0, 0))
        restartFont = pygame.font.SysFont("comicsansms", 30, True, True)
        scoreText = restartFont.render(f"Score: {self.score}", True, (255, 255, 255))
        restartText = restartFont.render(f"Press 'Esc' to return home!", True, (255, 255, 255))

        screen.blit(gameOverText, (windowWidth // 2 - gameOverText.get_width() // 2,
                                   gameOverRect.top + gameOverRect.height // 6))

        screen.blit(scoreText, (windowWidth // 2 - scoreText.get_width() // 2,
                                   gameOverRect.top + 2 * gameOverRect.height // 4))

        screen.blit(restartText, (windowWidth // 2 - restartText.get_width() // 2,
                                   gameOverRect.top + 3 * gameOverRect.height // 4))

    def drawGridLines(self, screen):
        gridSize = 200
        scrollX = round(self.scrollX)
        scrollY = round(self.scrollY)
        lineScrollX = scrollX % gridSize
        lineScrollY = scrollY % gridSize

        for i in range(windowWidth):
            if (i + lineScrollX) % gridSize == 0:
                pygame.draw.line(screen, BLACK, (i, 0), (i, windowHeight), 2)

        for i in range(windowHeight):
            if (i + lineScrollY) % gridSize == 0:
                pygame.draw.line(screen, BLACK, (0, i), (windowWidth, i), 2)

    # shows how much time remains before the next wave
    def drawWaveTimer(self, screen):
        width = windowWidth // 3
        height = windowHeight // 15
        timerRect = pygame.Rect(0, 0, width, height)
        pygame.draw.rect(screen, BLACK, timerRect, 3)
        pygame.gfxdraw.box(screen, timerRect, (26, 26, 26, 150))

        timeRemaining = max(0, (self.waveCooldown * 1000 - (pygame.time.get_ticks() - self.lastWave)) / 1000)

        # store the last known timer for when the game is paused
        if self.isPaused:
            timeRemaining = self.lastTime
        else:
            self.lastTime = timeRemaining
        seconds = int(timeRemaining)
        milliseconds = int((timeRemaining - seconds) * 100)

        if milliseconds < 10: milliseconds = '0' + str(milliseconds)
        if milliseconds == 0: milliseconds = '00'

        timerFont = pygame.font.SysFont('Arial', 22, True, False)
        if self.isWave:
            timerSurface = timerFont.render(f"Enemies Left: {len(self.bots)}", True, (255, 255, 255))
        else:
            timerSurface = timerFont.render(f"Time Until Next Wave: {seconds}.{milliseconds}", True, (255, 255, 255))
        screen.blit(timerSurface, (width // 2 - timerSurface.get_width() // 2,
                                   (height - timerSurface.get_height()) // 2))

    def drawScore(self, screen):
        width = windowWidth // 3
        height = windowHeight // 15
        left = windowWidth - width
        top = 0
        scoreRect = pygame.Rect(left, top, width, height)
        pygame.draw.rect(screen, BLACK, scoreRect, 3)
        pygame.gfxdraw.box(screen, scoreRect, (26, 26, 26, 150))

        scoreFont = pygame.font.SysFont('Arial', 22, True, False)
        scoreSurface = scoreFont.render(f"Score: {self.score[0]}", True, (255, 255, 255))
        screen.blit(scoreSurface, (left + width // 2 - scoreSurface.get_width() // 2,
                                   (height - scoreSurface.get_height()) // 2))

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
            screen.blit(ammoSurface, (boxRect.left + margin * 2 + ammoRadius * 2,
                                      boxRect.centery - ammoSurface.get_height() // 2))

            left += 20 + width

    def drawHealthBar(self, screen):
        left = screen.get_rect().width // 4
        top = 9 * screen.get_rect().height // 10
        barWidth = screen.get_rect().width // 2
        barHeight = screen.get_rect().height // 20

        ratio = self.player.hp/100
        ratio = max(0, ratio)
        ratio = min(ratio, 1)
        r, g, b = 255, 255 * math.sqrt(ratio), 255 * math.sqrt(ratio)

        pygame.draw.rect(screen, (r, g, b), pygame.Rect(left, top, barWidth * ratio, barHeight))
        pygame.draw.rect(screen, BLACK, pygame.Rect(left, top, barWidth, barHeight), 4)

    def drawAmmoDisplay(self, screen):
        if self.player.equippedGun is None:
            return

        width = windowWidth // 3
        height = windowHeight // 12
        left = screen.get_rect().centerx - width // 2
        top = 7.75 * screen.get_rect().height // 10
        displayRect = pygame.Rect(left, top, width, height)

        weaponColor = ITEM_COLORS[self.player.equippedGun.type]
        boxColor = pygame.Color(weaponColor[0], weaponColor[1], weaponColor[2], 150)
        pygame.gfxdraw.box(screen, displayRect, boxColor)
        pygame.draw.rect(screen, BLACK, displayRect, 3)

        ammoFont = pygame.font.SysFont('Arial', 40, True, False)
        currentAmmo = self.player.equippedGun.ammo
        maxAmmo = self.player.equippedGun.magSize
        ammoSurface = ammoFont.render(f"{currentAmmo} / {maxAmmo}", True, (255, 255, 255))
        screen.blit(ammoSurface, (displayRect.centerx - ammoSurface.get_width() // 2,
                                  displayRect.centery - ammoSurface.get_height() // 2))

    def drawSlowTimer(self, screen):
        player = self.player
        if not player.isSlow:
            return

        slowDuration = player.slowDuration
        timePassed = player.itemTimer
        ratio = timePassed / slowDuration

        # draw sliding bar with changing color
        cyan = (255 * (1-ratio), 255, 255)
        timerRect = pygame.Rect(windowWidth // 2 - 1.5 * player.r, windowHeight // 2 + 1.2 * player.r,
                                3 * player.r * ratio, 0.5 * player.r)
        pygame.draw.rect(screen, cyan, timerRect)

        # draw border of timer
        timerRect = pygame.Rect(windowWidth // 2 - 1.5 * player.r, windowHeight // 2 + 1.2 * player.r,
                                3 * player.r, 0.5 * player.r)
        pygame.draw.rect(screen, (0, 0, 0), timerRect, 2)

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
        h3 = Bandage(120, 300)
        h4 = Bandage(150, 250)
        self.items.add(h1, h2, h3, h4)

    def initWeapons(self):
        w1 = WeaponItem('12g', 400, 250)
        a11 = Ammo('12g', 400, 210, 50)
        a12 = Ammo('12g', 350, 240, 50)

        w2 = WeaponItem('9mm', 520, 490)
        a21 = Ammo('9mm', 460, 500, 50)
        a22 = Ammo('9mm', 550, 480, 50)

        w3 = WeaponItem('7.62', 410, 130)
        a31 = Ammo('7.62', 380, 110, 50)
        a32 = Ammo('7.62', 400, 90, 50)

        w4 = WeaponItem('5.56', 150, 120)
        a41 = Ammo('5.56', 130, 105, 50)
        a42 = Ammo('5.56', 160, 90, 50)
        self.items.add(w1, w2, w3, w4, a11, a12, a21, a22,
                       a31, a32, a41, a42)

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

    # check for collisions between bullets and all sorts of stuff in the game
    def checkBulletCollisions(self):
        bulletCollisions = pygame.sprite.groupcollide(self.bullets, self.obstacles, True, False)
        for bullet, target in bulletCollisions.items():
            target[0].hp -= bullet.dmg
            if target[0].hp <= 0:
                self.obstacles.remove(target[0])    # obstacles are destructible

        bulletBushCollisions = pygame.sprite.groupcollide(self.bullets, self.bushGroup, False, False)
        for bullet, bush in bulletBushCollisions.items():
            if bush[0] not in bullet.bushesSeen:
                bush[0].hp -= bullet.dmg
                if bush[0].hp <= 0:
                    self.bushGroup.remove(bush[0])  # bushes too
            bullet.bushesSeen.add(bush[0])          # so bullets pass through bushes but don't damage them twice

        bulletPlayerCollisions = pygame.sprite.groupcollide(self.bullets, self.allPlayers, True, False)
        for bullet, player in bulletPlayerCollisions.items():
            player[0].takeDmg(bullet.dmg)

        bulletBotCollisions = pygame.sprite.groupcollide(self.bullets, self.bots, True, False)
        for bullet, bot in bulletBotCollisions.items():
            bot[0].takeDmg(bullet.dmg, self.bots, self.score)

    # spawn a wave of melee bots
    def spawnWave(self, playerX, playerY):
        self.isWave = True
        difficulty = Game.difficulty
        ZombieBot.difficulty = difficulty
        if difficulty == 0:
            botCount = random.randint(3, 4)
        elif difficulty == 1:
            botCount = random.randint(4, 6)
        elif difficulty == 2:
            botCount = random.randint(5, 7)
            ZombieBot.learnRate = 2
        botCount += int(self.wavesPassed)
        ZombieBot.startWave(botCount)
        # print('Bot Params:', ZombieBot.dtp, ZombieBot.rmc, ZombieBot.rmd, '\n')
        for bot in range(botCount):
            # randomize the position the bot spawns in
            xOffset = (random.random() * 50 + windowWidth/2) * random.choice([1, -1])
            yOffset = (random.random() * 50 + windowWidth/2) * random.choice([1, -1])
            newBot = ZombieBot(playerX + xOffset, playerY + yOffset)
            self.bots.add(newBot)
        self.botCount = botCount

    def createMap(self):
        treeCount = 35
        bushCount = 60
        rockCount = 45
        medKitCount = 10
        bandageCount = 20
        weaponCount = 10
        ammoCount = 80
        ammoTypes = ['9mm', '7.62', '5.56', '12g']

        for i in range(treeCount):
            x, y = self.getRandomCoordinates(MAPSIZE)
            tree = Tree(x, y, TREE_RADIUS)
            self.obstacles.add(tree)
            self.treeTops.add(TreeTop(tree, self))

        for i in range(bushCount):
            x, y = self.getRandomCoordinates(MAPSIZE)
            bush = Bush(x, y, BUSH_RADIUS)
            self.bushGroup.add(bush)

        for i in range(rockCount):
            x, y = self.getRandomCoordinates(MAPSIZE)
            rock = Rock(x, y, ROCK_RADIUS)
            self.obstacles.add(rock)

        for i in range(medKitCount):
            x, y = self.getRandomCoordinates(MAPSIZE)
            item = MedKit(x, y)
            self.items.add(item)

        for i in range(weaponCount):
            x, y = self.getRandomCoordinates(MAPSIZE)
            item = Bandage(x, y)
            self.items.add(item)

        for i in range(bandageCount):
            x, y = self.getRandomCoordinates(MAPSIZE)
            weaponType = random.choice(ammoTypes)
            item = WeaponItem(weaponType, x, y)
            self.items.add(item)

        for i in range(ammoCount):
            x, y = self.getRandomCoordinates(MAPSIZE)
            ammoType = random.choice(ammoTypes)
            item = Ammo(ammoType, x, y)
            self.items.add(item)

        self.scrollX, self.scrollY = self.getRandomCoordinates(MAPSIZE)
        self.player = Player(self.scrollX, self.scrollY, PLAYER_RADIUS, game=self)
        self.playerGroup = pygame.sprite.Group(self.player)
        # prevent the player from spawning inside an obstacle
        collisions = pygame.sprite.groupcollide(self.playerGroup, self.obstacles, False, False)
        count = 0
        while self.player in collisions.keys():
            self.player.x += 10
            self.scrollX += 10
            collisions = pygame.sprite.groupcollide(self.playerGroup, self.obstacles, False, False)
            count += 1
            if count > 50:
                break


    def createTestMap(self):
        self.initBushes()
        self.initTrees()
        self.initWeapons()
        self.initHealth()
        self.scrollX = 300
        self.scrollY = 300

        self.player = Player(self.scrollX, self.scrollY, PLAYER_RADIUS)
        # self.bots = pygame.sprite.Group(ShootyBot(self.player, 500, 500))


    def getRandomCoordinates(self, MAPSIZE):
        x = random.random() * MAPSIZE
        y = random.random() * MAPSIZE
        return x, y

gameInstructions = [
    'Instructions',
    'F: Pick up items       R: Reload',
    'WASD: Movement         I: Open Inventory',
    'P: Pause               Esc: Restart',
    'Left Click: Shoot / Use Item',
    'Right Click: Drop Item',
    ' '
    'You can only pick up two weapons at a time and a limited',
    'amount of ammo and items.',
    'Blue circles are healing items, there are two different',
    'types and using them slows you down for a bit.',
    'Other  circles and squares represent weapons and ammo',
    'Waves will get harder, but you will get more points!'
]

class HomeScreen(PygameGame):
    def init(self):
        self.buttonColor = (51, 51, 153)
        self.black = (0, 0, 0)
        self.isInstructions = False

        self.gameModeColors = dict()
        self.difficultyColors = dict()
        self.gamemode = -1
        self.difficulty = -1

        self.instructionsRect = None
        self.playRect = None

        # store dictionaries mapping button positions to border colors (for mode selection)
        # positions are based on menu dimensions
        self.menuWidth = windowWidth // 2
        self.menuHeight = windowHeight * 2 // 3 + 20
        menuRect = pygame.Rect(windowWidth // 4, windowHeight // 6, self.menuWidth, self.menuHeight)
        self.margin = self.menuWidth // 20       # space between buttons
        self.buttonWidth = self.menuWidth - 2 * self.margin
        self.buttonHeight = (self.menuHeight - 2 * self.margin) // 8
        left = menuRect.left + self.margin
        top = menuRect.top + self.menuHeight // 4

        self.gameModeColors[(left, top)] = self.black
        self.gameModeColors[(left, top + self.buttonHeight + self.margin)] = self.black

        self.difficultyWidth = (self.menuWidth - 4 * self.margin) // 3     # difficulty buttons are smaller
        top += 2 * (self.buttonHeight + self.margin)
        for i in range(3):
            self.difficultyColors[(left, top)] = self.black
            left += self.difficultyWidth + self.margin


    def mouseMotion(self, x, y):
        pass

    def mouseDragged(self, x, y):
        pass

    def mouseReleased(self, x, y):
        pass

    def mousePressed(self, x, y, key):
        if key == 1:
            # check if a gamemode button was pressed
            for i, (left, top) in enumerate(self.gameModeColors.keys()):
                if left < x < left + self.buttonWidth and top < y < top + self.buttonHeight:
                    # reset all colors then change the one that was clicked
                    for key in self.gameModeColors.keys():
                        self.gameModeColors[key] = self.black
                    self.gameModeColors[(left, top)] = (255, 0, 0)
                    self.gamemode = i
                    break

            # check if a difficulty button was pressed
            for i, (left, top) in enumerate(self.difficultyColors.keys()):
                if left < x < left + self.difficultyWidth and top < y < top + self.buttonHeight:
                    # reset all colors then change the one that was clicked
                    for key in self.difficultyColors.keys():
                        self.difficultyColors[key] = self.black
                    self.difficultyColors[(left, top)] = (255, 0, 0)
                    self.difficulty = i
                    break

            # check if play button is clicked
            if self.playRect is not None:
                left, top = self.playRect.topleft
                right, bottom = self.playRect.bottomright
                if left < x < right and top < y < bottom:
                    Game.setMode(self.difficulty, self.gamemode)
                    Game(windowWidth, windowHeight).run()

            # check if instructions 'return' button is clicked
            if self.isInstructions:
                left, top = self.instructionsRect.topleft
                right, bottom = self.instructionsRect.bottomright
                if left < x < right and top < y < bottom:
                    self.isInstructions = False

            # check if instructions button is clicked
            else:
                left, top = self.instructionsRect.topleft
                right, bottom = self.instructionsRect.bottomright
                if left < x < right and top < y < bottom:
                    self.isInstructions = True


    def keyPressed(self, keyCode, mod):
        pass

    def timerFired(self, dt):
        pass

    def redrawAll(self, screen):
        fontSize = 32
        mainFont = pygame.font.SysFont('Arial', fontSize, True, False)
        buttonColor = (71, 71, 173)
        white = (255, 255, 255)
        black = (0, 0, 0)

        # draw background image
        baseImage = pygame.image.load('./images/background.png').convert_alpha()
        baseImage = aspect_scale(baseImage, windowWidth, windowHeight)
        screen.blit(baseImage, (0, 0))


        # draw menu background
        menuRect = pygame.Rect(windowWidth // 4, windowHeight // 6, self.menuWidth, self.menuHeight)
        pygame.gfxdraw.box(screen, menuRect, (210, 210, 210, 200))
        pygame.draw.rect(screen, black, menuRect, 3)

        margin = self.menuWidth // 20
        buttonWidth = self.menuWidth - 2 * margin
        buttonHeight = (self.menuHeight - 2 * margin) // 8
        left = menuRect.left + margin
        top = menuRect.top + menuRect.height // 4

        fontSize = 18
        instructionsFont = pygame.font.SysFont('Arial', fontSize, False, False)
        buttonRect = pygame.Rect(left, top, buttonWidth, buttonHeight)

        instructionsRect = buttonRect.copy()
        instructionsRect.y += 4 * (buttonHeight + margin)
        self.instructionsRect = instructionsRect

        # draw the instructions screen
        if self.isInstructions:
            for i, instruction in enumerate(gameInstructions):
                if i == 0:
                    instructionsFont.set_bold(True)
                textSurface = instructionsFont.render(instruction, True, BLACK)
                screen.blit(textSurface, (menuRect.centerx - textSurface.get_width() / 2,
                                          menuRect.top + margin + fontSize * 2 * i))
                instructionsFont.set_bold(False)

            pygame.draw.rect(screen, (110, 110, 110), instructionsRect)
            pygame.draw.rect(screen, black, instructionsRect, 3)
            textSurface = mainFont.render("Return", True, white)
            screen.blit(textSurface, (instructionsRect.centerx - textSurface.get_width() / 2,
                                      instructionsRect.centery - textSurface.get_height() / 2))
            self.instructionsRect = instructionsRect
            return

        # kawaii waifu miku copied from
        # https://www.deviantart.com/synergicstar/art/Smol-Miku-HD-REMASTERED-631700575
        logo = pygame.image.load('./images/logo.png').convert_alpha()
        width = 380 * windowWidth / 800
        height = 240 * windowHeight / 800
        logo = aspect_scale(logo, width, height)
        screen.blit(logo, (menuRect.centerx - logo.get_width() // 2 + 5,
                                menuRect.top + 15))

        # "SOLO" button
        pygame.draw.rect(screen, buttonColor, buttonRect)
        pygame.draw.rect(screen, self.gameModeColors[(buttonRect.left, buttonRect.top)], buttonRect, 3)
        textSurface = mainFont.render("Solo", True, white)
        screen.blit(textSurface, (buttonRect.centerx - textSurface.get_width() / 2,
                                  buttonRect.centery - textSurface.get_height() / 2))

        # "SQUADS" button
        buttonRect.y += buttonHeight + margin
        pygame.draw.rect(screen, buttonColor, buttonRect)
        pygame.draw.rect(screen, self.gameModeColors[(buttonRect.left, buttonRect.top)], buttonRect, 3)
        textSurface = mainFont.render("Squads (Coming Soon)", True, white)
        screen.blit(textSurface, (buttonRect.centerx - textSurface.get_width() / 2,
                                  buttonRect.centery - textSurface.get_height() / 2))

        # Difficulty buttons
        difficultyRect = pygame.Rect(buttonRect.left, buttonRect.bottom + margin,
                                     (menuRect.width - 4 * margin) // 3, buttonRect.height)

        difficulties = ['Easy', 'Normal', 'Hard']
        diffColors = [(0, 153, 0), (51, 102, 255), (128, 0, 0)]
        for i in range(3):
            pygame.draw.rect(screen, diffColors[i], difficultyRect)
            pygame.draw.rect(screen, self.difficultyColors[(difficultyRect.left, difficultyRect.top)],
                             difficultyRect, 3)
            textSurface = mainFont.render(difficulties[i], True, white)
            screen.blit(textSurface, (difficultyRect.centerx - textSurface.get_width() / 2,
                                      difficultyRect.centery - textSurface.get_height() / 2))
            difficultyRect.x += difficultyRect.width + margin

        # "How to Play" button
        buttonRect.y += (buttonHeight + margin) * 2
        pygame.draw.rect(screen, (110, 110, 110), buttonRect)
        pygame.draw.rect(screen, black, buttonRect, 3)
        textSurface = mainFont.render("How To Play", True, white)
        screen.blit(textSurface, (buttonRect.centerx - textSurface.get_width() / 2,
                                  buttonRect.centery - textSurface.get_height() / 2))
        self.instructionsRect = buttonRect

        # "Start" button (only displays once game mode and difficulty are chosen)
        if self.difficulty != -1 and self.gamemode != -1:
            buttonRect.y += buttonHeight + margin
            pygame.draw.rect(screen, (0, 230, 230), buttonRect)
            pygame.draw.rect(screen, black, buttonRect, 3)
            textSurface = mainFont.render("Play", True, white)
            screen.blit(textSurface, (buttonRect.centerx - textSurface.get_width() / 2,
                                      buttonRect.centery - textSurface.get_height() / 2))
            self.playRect = buttonRect


HomeScreen(windowWidth, windowHeight).run()
