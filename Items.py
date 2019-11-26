import pygame
import pygame.gfxdraw
import math
from GameObject import GameObject
from Constants import *


class Item(GameObject):

    # draws the item in the inventory
    @staticmethod
    def drawItem(surface, x, y, color, r=ITEM_RADIUS):
        x, y, r = round(x), round(y), round(r)
        pygame.draw.circle(surface, color, (x, y), r)
        pygame.draw.circle(surface, BLACK, (x, y), r, 3)

    def __init__(self, x, y, r, color, dx, dy):
        super().__init__(x, y, r)
        self.color = color
        self.type = 'item'
        self.dx, self.dy = dx, dy
        pygame.draw.circle(self.image, color, (r, r), r)
        pygame.draw.circle(self.image, BLACK, (r, r), r, 3)

    def update(self, scrollX, scrollY):
        self.x += self.dx * 5
        self.y += self.dy * 5
        self.dx /= 2
        self.dy /= 2

        if abs(self.dx) < 10**-3: self.dx = 0
        if abs(self.dy) < 10**-3: self.dy = 0

        super().update(scrollX, scrollY)


class MedKit(Item):
    def __init__(self, x, y, r=ITEM_RADIUS, dx=0, dy=0):
        super().__init__(x, y, r, MEDKIT_COLOR, dx, dy)
        pygame.draw.line(self.image, BLACK, (self.r / 2, self.r),
                         (self.r * 3 / 2, self.r), 2)
        pygame.draw.line(self.image, BLACK, (self.r, self.r / 2),
                         (self.r, self.r  * 3 / 2), 2)
        self.name = "MedKit"
        self.type = "health"
        self.heal = 80
        self.time = 3000


class Bandage(Item):
    def __init__(self, x, y, r=ITEM_RADIUS, dx=0, dy=0):
        super().__init__(x, y, r, BANDAGE_COLOR, dx, dy)
        pygame.draw.line(self.image, BLACK, (self.r / 2, self.r),
                         (self.r * 3 / 2, self.r), 2)
        pygame.draw.line(self.image, BLACK, (self.r, self.r / 2),
                         (self.r, self.r * 3 / 2), 2)
        self.name = "Bandage"
        self.type = "health"
        self.heal = 20
        self.time = 1000


class Adrenaline(Item):
    def __init__(self, x, y, r=ITEM_RADIUS, dx=0, dy=0):
        super().__init__(x, y, r, BANDAGE_COLOR, dx, dy)
        self.name = "Adrenaline"
        self.type = 'adrenaline'