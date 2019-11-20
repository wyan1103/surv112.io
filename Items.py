import pygame
import pygame.gfxdraw
import math
from GameObject import GameObject

ITEM_RADIUS = 25
AMMO_RADIUS = 20
BLACK = (0, 0, 0)
HEALTH_COLOR = (0, 102, 255)
ADREN_COLOR = (0, 102, 255)
FOOD_COLOR = (255, 153, 102)


class Item(GameObject):

    # draws the item in the inventory
    @staticmethod
    def drawItem(surface, x, y, color, r=ITEM_RADIUS):
        x, y, r = round(x), round(y), round(r)
        pygame.draw.circle(surface, color, (x, y), r)
        pygame.draw.circle(surface, BLACK, (x, y), r, 3)

    def __init__(self, x, y, r=ITEM_RADIUS, color=(0, 0, 0)):
        super().__init__(x, y, r)
        self.color = color
        pygame.draw.circle(self.image, color, (r, r), r)
        pygame.draw.circle(self.image, BLACK, (r, r), r, 3)


class MedKit(Item):
    def __init__(self, x, y, r=ITEM_RADIUS):
        super().__init__(x, y, r, HEALTH_COLOR)
        self.name = "MedKit"
        self.heal = 100


class Adrenaline(Item):
    def __init__(self, x, y, r=ITEM_RADIUS):
        super().__init__(x, y, r, HEALTH_COLOR)
        self.name = "Adrenaline"