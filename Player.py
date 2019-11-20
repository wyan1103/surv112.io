import pygame
import pygame.gfxdraw
import numpy as np
import math, copy, random
from GameObject import GameObject
from Weapons import *

PEACH = (255, 204, 153)
BLACK = (0, 0, 0)

class Player(GameObject):
    def __init__(self, x, y, r):
        super().__init__(x, y, r)
        pygame.gfxdraw.filled_circle(self.image, r, r, r-2, PEACH)
        pygame.draw.circle(self.image, BLACK, (r, r), r, 3)
        self.hp = 100
        self.rect = pygame.Rect(x - r, y - r, 2 * r, 2 * r)
        self.inventory = []
        self.inventorySize = 12
        self.primaryGun = None
        self.secondaryGun = None
        self.equippedGun = None
        self.openInventory = False
        self.gameOver = False
        self.ammo = {'9mm' : 0, '7.62' : 0, '5.56' : 0, '12g' : 0}
        self.ammoLimits = {'9mm' : 150, '7.62' : 120, '5.56' : 120, '12g' : 24}

    def update(self, keysDown, time, obstacles, scrollX, scrollY):
        if keysDown(pygame.K_a):
            print(self.hp)
        if keysDown(pygame.K_LEFT):
            self.move(-5, 0, obstacles)
        if keysDown(pygame.K_RIGHT):
            self.move(5, 0, obstacles)
        if keysDown(pygame.K_UP):
            self.move(0, -5, obstacles)
        if keysDown(pygame.K_DOWN):
            self.move(0, 5, obstacles)

        if self.equippedGun is not None:
            self.equippedGun.update(scrollX, scrollY)

    '''TODO: Fix collision detection to differentiate between polygons and circles'''
    def move(self, dx, dy, obs):
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

    def rotate(self, x, y):
        if self.equippedGun is not None:
            self.equippedGun.rotate(x, y)

    def shoot(self, x, y, time):
        bulletSpeed = self.equippedGun.bulletSpeed
        type = self.equippedGun.type
        dmg = self.equippedGun.dmg

        if self.ammo[type] <= 0 or time - self.equippedGun.lastShot < self.equippedGun.fireDelay:
            return None
        self.ammo[type] -= 1
        self.equippedGun.lastShot = time

        dx, dy = x - self.x, y - self.y
        dx *= 1 + (2 * (random.random()-0.5) * self.equippedGun.bulletSpread)
        dy *= 1 + (2 * (random.random() - 0.5) * self.equippedGun.bulletSpread)

        dist = (dx ** 2 + dy ** 2) ** 0.5
        time = dist / bulletSpeed
        xVelocity, yVelocity = dx / time, dy / time

        return Bullet(self.x + xVelocity*6, self.y + yVelocity*6, xVelocity, yVelocity, dmg, type)


    # adds an item to inventory, returning False if inventory is full
    def pickUpItem(self, item, itemGroup):
        if isinstance(item, WeaponItem):
            if self.primaryGun is not None:
                self.primaryGun.drop(self.x, self.y)
            self.primaryGun = item.createWeapon(self)
            self.equippedGun = self.primaryGun
            return True

        if isinstance(item, Ammo):
            type = item.type
            if self.ammo[type] < self.ammoLimits[type]:
                self.ammo[type] += item.amount
                if self.ammo[type] > self.ammoLimits[type]:
                    excess = self.ammo[type] - self.ammoLimits[type]
                    self.ammo[type] = self.ammoLimits[type]

                return True

        if len(self.inventory) < self.inventorySize:
            self.inventory.append(item)
            return True
        return False

    def changePID(self, PID):
        self.PID = PID


# copied from https://www.pygame.org/pcr/transform_scale/aspect_scale.py
def aspect_scale(img, bx, by):
    """ Scales 'img' to fit into box bx/by.
     This method will retain the original image's aspect ratio """
    ix,iy = img.get_size()
    if ix > iy:
        # fit to width
        scale_factor = bx/float(ix)
        sy = scale_factor * iy
        if sy > by:
            scale_factor = by/float(iy)
            sx = scale_factor * ix
            sy = by
        else:
            sx = bx
    else:
        # fit to height
        scale_factor = by/float(iy)
        sx = scale_factor * ix
        if sx > bx:
            scale_factor = bx/float(ix)
            sx = bx
            sy = scale_factor * iy
        else:
            sy = by

    return pygame.transform.scale(img, (sx, sy))
