import pygame
import pygame.gfxdraw
from GameObject import GameObject
from Constants import *

class Bush(GameObject):
    def __init__(self, x, y, r):
        super().__init__(x, y, r)
        self.hp = 200
        pygame.gfxdraw.filled_circle(self.image, r, r, r, BUSH_GREEN)

    def __repr__(self):
        return f"Bush at {self.x}, {self.y}"


class Tree(GameObject):
    def __init__(self, x, y, r):
        super().__init__(x, y, r)
        self.hp = 300
        pygame.gfxdraw.filled_circle(self.image, r, r, r, TREE_BROWN)
        # pygame.gfxdraw.filled_circle(self.image, r, r, 3*r, BUSH_GREEN)

    def __repr__(self):
        return f"Tree at {self.x}, {self.y}"
