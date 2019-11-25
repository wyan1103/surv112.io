import pygame
from Player import *

class Bot(Player):
    def __init__(self, x, y, r=PLAYER_RADIUS):
        super().__init__(x, y, r)
        self.bullets = []
        self.reward = 0
        self.primaryGun = Weapon(self, 10, '7.62', 50)
        self.equippedGun = self.primaryGun
        self.ammo = {'9mm' : 1000, '7.62' : 1000, '5.56' : 1000, '12g' : 1000}
        self.equippedGun.ammo = 10000

    def update(self, scrollX, scrollY):
        super(Player, self).update(scrollX, scrollY)

    def botShoot(self, angle, time, gameBullets):
        x, y = math.cos(math.radians(angle)) * 10, math.sin(math.radians(angle)) * 10
        bullet = super().shoot(self.x + x, self.y + y, time, True)
        if bullet is not None:
            self.bullets.append(bullet)
            gameBullets.add(bullet)

    # move unless the move will cause the bot to hit another object
    def botMove(self, dx, dy, obstacles):
        playerGroup = pygame.sprite.Group(self)
        prevCoords = (self.x, self.y)

        self.x += dx
        self.y += dy

        if self in pygame.sprite.groupcollide(playerGroup, obstacles, False, False):
            self.x -= dx * 2
            self.y -= dy * 2

        if (self.x, self.y) != prevCoords:
            self.isMoving = True
        else:
            self.isMoving = False

    # randomly pick an action and a direction for the action
    def botAction(self, obstacles, time, gameBullets):
        possibleMovements = [(-5, 0), (5, 0), (0, -5), (0, 5)]
        moveChance = 0.8
        shootChance = 0.9

        if random.random() < moveChance:
            movement = random.choice(possibleMovements)
            self.botMove(movement[0], movement[1], obstacles)

        if random.random() < shootChance:
            print('._.')
            angle = random.random() * 360
            self.botShoot(angle, time, gameBullets)


