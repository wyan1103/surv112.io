import pygame
from GameObject import *
from Items import *

BULLET_RADIUS = 5
BROWN = (77, 38, 0)
LIGHT_GRAY = (230, 230, 230)
AMMO_COLORS = {'9mm' : (255, 153, 0)}

class Weapon(pygame.sprite.Sprite):

    @staticmethod
    def init():
        Weapon.baseImage = pygame.image.load('./gun-long.png').convert_alpha()

    def __init__(self, player, dmg, type):
        super().__init__()
        self.baseImage = aspect_scale(Weapon.baseImage.copy(), 20, 200)
        self.image = self.baseImage

        self.r = 2*player.r
        self.x, self.y = player.x, player.y
        self.rect = pygame.Rect(player.x-self.r, player.y-self.r, 2*self.r, 2*self.r)

        self.owner = player
        self.angle = 0
        self.type = type
        self.dmg = dmg
        self.color = AMMO_COLORS[type]

    def updateRect(self, scrollX, scrollY):
        w, h = self.image.get_size()
        self.width, self.height = w, h
        self.rect = pygame.Rect(self.owner.x - w/2 - scrollX, self.owner.y - h/2 - scrollY, w, h)

    def update(self, scrollX, scrollY):
        self.image = pygame.transform.rotate(self.baseImage, math.degrees(self.angle))
        self.updateRect(scrollX, scrollY)

    def drop(self, x, y):
        pass

    def rotate(self, cursorX, cursorY):
        self.angle = -math.atan2(cursorY - self.owner.y, cursorX - self.owner.x) - math.pi/2

    def drawWeapon(self, surface, x, y, width, height):
        weaponImage = pygame.image.load('./gun-long-cropped.png').convert_alpha()
        weaponImage = pygame.transform.rotate(weaponImage, 90)
        weaponImage = aspect_scale(weaponImage, width, height)
        x = x - weaponImage.get_rect().width / 2
        surface.blit(weaponImage, (x, y))


class WeaponItem(Item):
    def __init__(self, type, x, y, r=ITEM_RADIUS):
        super().__init__(x, y, r, LIGHT_GRAY)
        self.type = type

    def createWeapon(self, player):
        return Weapon(player, 100, '9mm')


class Bullet(GameObject):
    def __init__(self, x, y, dx, dy, dmg, type):
        super().__init__(x, y, BULLET_RADIUS)
        super().update(self.x, self.y)
        pygame.gfxdraw.filled_circle(self.image, self.r, self.r, self.r, AMMO_COLORS['9mm'])
        self.dx, self.dy = dx, dy
        self.dmg = dmg
        self.type = type
        self.distanceTravelled = 0
        self.bushesSeen = set()

    def update(self, scrollX, scrollY):
        self.x += self.dx
        self.y += self.dy
        self.distanceTravelled += (self.dx**2 + self.dy**2)**0.5
        super().update(scrollX, scrollY)


    def __repr__(self):
        return f"({self.x}, {self.y})"



