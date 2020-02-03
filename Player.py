import pygame
import pygame.gfxdraw
import numpy as np
import math, copy, random
from GameObject import GameObject
from Weapons import *
from Items import *
from Constants import *


class Player(GameObject):
    def __init__(self, x, y, r, color=PEACH, game=None):
        super().__init__(x, y, r)
        self.rect = pygame.Rect(windowWidth // 2 - r, windowWidth // 2 - r, 2 * r, 2 * r)
        pygame.gfxdraw.filled_circle(self.image, r, r, r-2, color)
        pygame.draw.circle(self.image, BLACK, (r, r), r, 3)
        self.hp = 100
        self.speed = 5
        self.inventory = []
        self.inventorySize = 12
        self.primaryGun = None
        self.secondaryGun = None
        self.equippedGun = None
        self.gameOver = False
        self.isSlow = False
        self.isMoving = False
        self.itemInUse = None
        self.slowDuration = 0
        self.timerStart = 0
        self.itemTimer = 0
        self.ammo = {'9mm' : 0, '7.62' : 0, '5.56' : 0, '12g' : 0}
        self.ammoLimits = {'9mm' : 240, '7.62' : 120, '5.56' : 120, '12g' : 24}
        self.game = game

    # Updates the player's in-game position
    def update(self, keysDown, time, obstacles, scrollX, scrollY):
        if self.isSlow:
            self.itemTimer = time - self.timerStart
            if self.itemTimer >= self.slowDuration:
                self.finishUseItem()
                self.isSlow = False
                self.itemInUse = None
                self.itemTimer = 0

        if keysDown(pygame.K_a):
            pass
        speed = self.speed // 2 if self.isSlow else self.speed

        if keysDown(pygame.K_a):
            self.move(-speed, 0, obstacles)
        if keysDown(pygame.K_d):
            self.move(speed, 0, obstacles)
        if keysDown(pygame.K_w):
            self.move(0, -speed, obstacles)
        if keysDown(pygame.K_s):
            self.move(0, speed, obstacles)

        # moving left and right simultaneously is equivalent to not moving
        if keysDown(pygame.K_LEFT) == keysDown(pygame.K_RIGHT) and \
                keysDown(pygame.K_UP) == keysDown(pygame.K_DOWN):
            self.isMoving = False

        if self.equippedGun is not None:
            self.equippedGun.update(scrollX, scrollY)

    '''TODO: Fix collision detection to differentiate between polygons and circles'''
    def move(self, dx, dy, obs):
        self.isMoving = True
        obstacles = copy.copy(obs)
        for obstacle in obstacles:

            # decomposes player movement into components pointing towards and tangent to an obstacle
            v_player = np.array([dx, dy])
            v_cc = np.array([self.x - obstacle.x, self.y - obstacle.y])
            v_center = np.dot(v_player, v_cc) / ((np.linalg.norm(v_cc)**2)) * v_cc
            v_tangent = v_player - v_center

            # if directly making the move causes a collision, move as close as possible to the
            # obstacle then make the remaining move tangent to the obstacle
            dist_between_centers = np.linalg.norm(v_cc)
            dist_between_circles = dist_between_centers - self.r - obstacle.r
            if dist_between_circles < np.linalg.norm(v_center):
                v_center = v_cc / (np.linalg.norm(v_cc)) * dist_between_circles

                # recursively call move with the new movement vectors
                # in case player bumps into a second object at the same time
                dx, dy = v_center[0] * 0.9, v_center[1] * 0.9
                try:
                    self.move(v_center[0] * 0.9, v_center[1] * 0.9, obs)
                    if abs(v_tangent[0]) > 1 or abs(v_tangent[1]) > 1:
                    # if not (math.isclose(v_tangent[0], dx) and math.isclose(v_tangent[1], dy)):
                        self.move(v_tangent[0], v_tangent[1], obstacles)
                except:
                    return

        self.x += dx
        self.y += dy
        self.game.mouseCoords[0] += dx
        self.game.mouseCoords[1] += dy

        if self.x > 3200:
            self.x -= 5
        elif self.x < -200:
            self.x += 5
        if self.y > 3200:
            self.y -= 5
        elif self.y < -200:
            self.y += 5

    def rotate(self, x, y):
        if self.equippedGun is not None:
            self.equippedGun.rotate(x, y)

    def startReload(self, time):
        weapon = self.equippedGun
        if self.itemInUse is not None or weapon.ammo == weapon.magSize or \
            self.ammo[weapon.type] == 0:
            return

        self.isSlow = True
        self.slowDuration = weapon.reloadTime
        self.itemTimer = 0
        self.timerStart= time
        self.itemInUse = weapon

    def finishReload(self):
        weapon = self.equippedGun
        type = weapon.type

        # if out of ammo, do nothing
        if self.ammo[type] <= 0:
            return
        # if cannot reload to full, put the rest of the ammo into the gun
        elif self.ammo[type] + weapon.ammo <= weapon.magSize:
            weapon.ammo = self.ammo[type] + weapon.ammo
            self.ammo[type] = 0
        # otherwise, deduct the necessary amount from player inventory and add to gun ammo
        else:
            self.ammo[type] -= weapon.magSize - weapon.ammo
            weapon.ammo = weapon.magSize


    # if the player has a weapon, creates a new bullet based on weapon properties and dispersion.
    def shoot(self, x, y, time, isBot=False):
        bulletSpeed = self.equippedGun.bulletSpeed
        type = self.equippedGun.type
        dmg = self.equippedGun.dmg

        # do nothing if out of ammo or if the gun is on cooldown
        if self.equippedGun.ammo <= 0 or time - self.equippedGun.lastShot < self.equippedGun.fireDelay:
            return None
        self.equippedGun.ammo -= 1
        self.equippedGun.lastShot = time

        # add dispersion based to bullets based on where the player is aiming
        dx, dy = x - self.x, y - self.y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        # a random number from -1 to 1 is created and multiplied by the gun's dispersion as a
        # percent offset from the actual target.
        dx *= 1 + (2 * (random.random()-0.5) * self.equippedGun.bulletSpread) * dx / dist
        dy *= 1 + (2 * (random.random() - 0.5) * self.equippedGun.bulletSpread) * dy / dist

        # calculate velocity by dividing distance travelled by time for both x and y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        time = dist / bulletSpeed
        xVelocity, yVelocity = dx / time, dy / time
        # return different types of bullets depending on if the shooter is a bot or
        if isBot:
            return BotBullet(self.x + xVelocity * (5/SCALE), self.y + yVelocity * (5/SCALE),
                             xVelocity, yVelocity, dmg, type, self)
        else:
            return Bullet(self.x + xVelocity*(5/SCALE), self.y + yVelocity*(5/SCALE),
                          xVelocity, yVelocity, dmg, type)

    def takeDmg(self, dmg):
        self.hp -= dmg
        if self.hp < 0:
            self.hp = 0
            self.gameOver = True

    # adds an item to inventory, returning False if inventory is full
    def pickUpItem(self, item, itemGroup):
        # for picking up weapons, requires a free slot
        if isinstance(item, WeaponItem):
            if self.primaryGun is None or self.secondaryGun is None:
                self.equippedGun = item.createWeapon(self)
            else:
                return False
            if self.primaryGun is None:
                self.primaryGun = self.equippedGun
            else:
                self.secondaryGun = self.equippedGun
            return True

        elif isinstance(item, Ammo):
            type = item.type
            self.ammo[type] += item.amount
            if self.ammo[type] > self.ammoLimits[type]:
                excess = self.ammo[type] - self.ammoLimits[type]
                self.ammo[type] = self.ammoLimits[type]
                self.dropAmmo(type, itemGroup, excess)
            return True

        elif len(self.inventory) < self.inventorySize:
            self.inventory.append(item)
            return True
        return False

    def dropAmmo(self, type, gameItems, amount=None):
        xSpeed = (random.random() - 0.5) * 20
        ySpeed = (random.random() - 0.5) * 20
        if amount is not None:
            gameItems.add(Ammo(type, self.x, self.y, amount, AMMO_RADIUS, xSpeed, ySpeed))
            return

        if self.ammo[type] > 90:
            amount = 30
        elif self.ammo[type] <= 2:
            amount = self.ammo[type]
        else:
            amount = self.ammo[type] // 3
        self.ammo[type] -= amount
        gameItems.add(Ammo(type, self.x, self.y, amount, AMMO_RADIUS, xSpeed, ySpeed))

    def useItem(self, item, time):
        if self.itemInUse is not None:
            return
        self.isSlow = True
        self.slowDuration = item.time
        self.itemTimer = 0
        self.timerStart= time
        self.itemInUse = item

        try: self.inventory.remove(item)
        except: pass  # avoid a tragedy if something wrong happens

    def finishUseItem(self, failed=False):
        if failed:
            return
        # if reloading a gun, do that
        if self.itemInUse.type in AMMO_COLORS:
            self.finishReload()
        # if healing, restore hp
        if self.itemInUse.type == 'health':
            self.hp += self.itemInUse.heal
            if self.hp > 100:
                self.hp = 100

    def changePID(self, PID):
        self.PID = PID
