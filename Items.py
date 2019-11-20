import pygame
import pygame.gfxdraw
import math
from GameObject import GameObject

ITEM_RADIUS = 30
BLACK = (0, 0, 0)
HEALTH_COLOR = (0, 102, 255)
ADREN_COLOR = (0, 102, 255)
FOOD_COLOR = (255, 153, 102)


class Item(GameObject):
    def __init__(self, x, y, r=ITEM_RADIUS, color=(0, 0, 0)):
        super().__init__(x, y, r)
        self.color = color
        pygame.gfxdraw.filled_circle(self.image, r, r, r, color)
        pygame.gfxdraw.aacircle(self.image, r, r, r, BLACK)

    # draws the item in the inventory
    def drawItem(self, surface, x, y, r=ITEM_RADIUS):
        x, y, r = round(x), round(y), round(r)
        pygame.draw.circle(surface, self.color, (x, y), r)
        pygame.draw.circle(surface, BLACK, (x, y), r, 3)


class MedKit(Item):
    def __init__(self, x, y, r=ITEM_RADIUS):
        super().__init__(x, y, r, HEALTH_COLOR)
        self.name = "MedKit"
        self.heal = 100


class Adrenaline(Item):
    def __init__(self, x, y, r=ITEM_RADIUS):
        super().__init__(x, y, r, HEALTH_COLOR)
        self.name = "Adrenaline"