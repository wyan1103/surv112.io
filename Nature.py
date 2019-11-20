import pygame
import pygame.gfxdraw
from GameObject import GameObject

BUSH_GREEN = (0, 102, 0, 220)
BROWN = (102, 51, 0)

class Bush(GameObject):
    def __init__(self, x, y, r):
        super().__init__(x, y, r)
        self.hp = 500
        pygame.gfxdraw.filled_circle(self.image, r, r, r, BUSH_GREEN)

    def __repr__(self):
        return f"Bush at {self.x}, {self.y}"


class Tree(GameObject):
    def __init__(self, x, y, r):
        super().__init__(x, y, r)
        self.hp = 1000
        pygame.gfxdraw.filled_circle(self.image, r, r, r, BROWN)
        # pygame.gfxdraw.filled_circle(self.image, r, r, 3*r, BUSH_GREEN)

    def __repr__(self):
        return f"Tree at {self.x}, {self.y}"
