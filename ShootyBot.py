import pygame
from Player import *

class ShootyBot(GameObject):
    def __init__(self, player, x, y, r=PLAYER_RADIUS):
        super().__init__(x, y, r)
        pygame.gfxdraw.filled_circle(self.image, r, r, r - 2, TAN)
        pygame.draw.circle(self.image, BLACK, (r, r), r, 3)
        self.gun = Weapon(self, 10, '7.62', 50)
        self.gun.ammo = 10000
        self.burst = 10
        self.reloadTime = 4
        self.shotDelay = 0.5
        self.lastShot = 0
        self.shotsFired = 0
        self.reloading = False
        self.accuracy = 0.2
        self.target = player
        self.bulletsFired = []

    def update(self, scrollX, scrollY):
        super().update(scrollX, scrollY)

    def move(self, obstacles, others, player, time):
        pass

    def shoot(self, gameBullets, time):
        print(time)
        if self.reloading and time - self.lastShot > self.reloadTime * 1000:
            self.reloading = False

        # don't do anything if on shooting cooldown
        if time - self.lastShot < self.shotDelay * 1000 or self.reloading:
            return
        else:
            self.lastShot = time
            self.shotsFired += 1

        # add dispersion based to bullets based on where the player is aiming
        tx, ty = self.target.x, self.target.y
        dx, dy = tx - self.x, ty - self.y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        # a random number from -1 to 1 is created and multiplied by the gun's dispersion as a
        # percent offset from the actual target.
        dx *= 1 + (2 * (random.random() - 0.5) * self.accuracy) * dx / dist
        dy *= 1 + (2 * (random.random() - 0.5) * self.accuracy) * dy / dist

        dist = (dx ** 2 + dy ** 2) ** 0.5
        travelTime = dist / 12
        xVelocity, yVelocity = dx / travelTime, dy / travelTime

        bullet = BotBullet(self.x + xVelocity * (4/SCALE), self.y + yVelocity * (4/SCALE),
                           xVelocity, yVelocity, self.gun.dmg, self.gun.type, self)

        gameBullets.add(bullet)
        self.bulletsFired.append(bullet)

        if self.shotsFired % self.burst == 0:
            self.reloading = True


# Taken from https://bryceboe.com/2006/10/23/line-segment-intersection-algorithm/ for
# checking if lines intersect
class Point:
    def __init__(self,x,y):
        self.x = x
        self.y = y

def ccw(A,B,C):
    return (C.y-A.y)*(B.x-A.x) > (B.y-A.y)*(C.x-A.x)

def intersect(A,B,C,D):
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)
