import pygame
from GameObject import *
from Items import *
from Constants import *


class Weapon(pygame.sprite.Sprite):

    @staticmethod
    def init():
        # copied from surviv.io
        Weapon.baseImage = pygame.image.load('./images/gun-long.png').convert_alpha()

    def __init__(self, player, dmg, type, fireDelay, ammo=0, magSize=10, reloadTime=2000,
                 bulletSpeed=15, bulletSpread=0.2, auto=False):
        super().__init__()
        self.baseImage = aspect_scale(Weapon.baseImage.copy(), 20, 200)
        w, h = self.baseImage.get_size()
        self.image = aspect_scale(self.baseImage, int(w // SCALE),
                                  int(h // SCALE))

        self.r = 2*player.r
        self.x, self.y = player.x, player.y
        self.rect = pygame.Rect(player.x-self.r, player.y-self.r, 2*self.r, 2*self.r)

        self.owner = player
        self.angle = 0
        self.ammo = ammo
        self.magSize = magSize
        self.reloadTime = reloadTime
        self.type = type
        self.dmg = dmg
        self.fireDelay = fireDelay        # time per shot in ms
        self.lastShot = 0
        self.bulletSpeed = bulletSpeed
        self.bulletSpread = bulletSpread
        self.color = AMMO_COLORS[type]
        self.auto = auto

    def updateRect(self, scrollX, scrollY):
        w, h = self.image.get_size()
        self.width, self.height = w, h
        self.rect = pygame.Rect(self.owner.x - w/2 - scrollX, self.owner.y - h/2 - scrollY, w, h)

    def update(self, scrollX, scrollY):
        w, h = self.baseImage.get_size()
        self.image = aspect_scale(self.baseImage, int(w // SCALE),
                                  int(h // SCALE))
        self.image = pygame.transform.rotate(self.image, math.degrees(self.angle))
        self.updateRect(scrollX, scrollY)

    def rotate(self, cursorX, cursorY):
        self.angle = -math.atan2(cursorY - self.owner.y, cursorX - self.owner.x) - math.pi/2

    def drawWeapon(self, surface, x, y, width, height):
        # copied from surviv.io
        weaponImage = pygame.image.load('./images/gun-long-cropped.png').convert_alpha()
        weaponImage = pygame.transform.rotate(weaponImage, 90)
        weaponImage = aspect_scale(weaponImage, width, height)
        x = x - weaponImage.get_rect().width / 2
        surface.blit(weaponImage, (x, y))

    def createWeaponItem(self, x, y):
        return WeaponItem(self.type, x, y)


class WeaponItem(Item):
    def __init__(self, type, x, y, r=ITEM_RADIUS, dx=0, dy=0):
        super().__init__(x, y, r, AMMO_COLORS[type], dx, dy, True)
        self.type = type

    def createWeapon(self, player):
        if self.type == '9mm':
            # smg-type weapon
            return Weapon(player, 10, self.type, 100, magSize=32, reloadTime=1500, bulletSpread=0.5,
                          bulletSpeed=12, auto=True)
        elif self.type == '7.62':
            # dmr-type weapon
            return Weapon(player, 30, self.type, 300, magSize=20, bulletSpread=0.1, bulletSpeed=20)
        elif self.type == '5.56':
            # ar-type weapon
            return Weapon(player, 20, self.type, 160, magSize=30, auto=True)
        elif self.type == '12g':
            # sniper-type weapon
            return Weapon(player, 60, self.type, 1000, magSize=4, reloadTime=2500, bulletSpread=0.05,
                          bulletSpeed=25)


class Bullet(GameObject):

    pauseBullets = False

    def __init__(self, x, y, dx, dy, dmg, type):
        super().__init__(x, y, BULLET_RADIUS)
        super().update(self.x, self.y)
        pygame.draw.circle(self.image, AMMO_COLORS[type], (self.r, self.r), self.r)
        pygame.draw.circle(self.image, AMMO_COLORS[type], (self.r, self.r), self.r, 2)
        self.dx, self.dy = dx, dy
        self.dmg = dmg
        self.type = type
        self.distanceTravelled = 0
        self.bushesSeen = set()

    def update(self, scrollX, scrollY):
        if not self.pauseBullets:
            self.x += self.dx
            self.y += self.dy
            self.distanceTravelled += (self.dx**2 + self.dy**2)**0.5
        super().update(scrollX, scrollY)

    def __repr__(self):
        return f"({self.x}, {self.y})"

# special type of bullet that can return information back to its creator
# (for bot training)
class BotBullet(Bullet):
    def __init__(self, x, y, dx, dy, dmg, type, owner):
        super().__init__(x, y, dx, dy, dmg, type)
        self.owner = owner

class Ammo(Item):

    @staticmethod
    def drawItem(surface, x, y, color, r=AMMO_RADIUS):
        x, y, r = round(x), round(y), round(r)
        pygame.draw.rect(surface, color, pygame.Rect(x, y, 2 * r, 2 * r))
        pygame.draw.rect(surface, BLACK, pygame.Rect(x, y, 2 * r, 2 * r), 3)

    def __init__(self, type, x, y, amount=30, r=AMMO_RADIUS, dx=0, dy=0):
        super().__init__(x, y, r, AMMO_COLORS[type], dx, dy)
        pygame.draw.rect(self.image, self.color, pygame.Rect(0, 0, self.rect.width, self.rect.height))
        pygame.draw.rect(self.image, BLACK, pygame.Rect(0, 0, self.rect.width, self.rect.height), 4)
        self.type = type
        if type == '12g':
            amount = 6
        elif type == '9mm':
            amount = 40
        self.amount = amount


