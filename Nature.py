import pygame
import pygame.gfxdraw
from GameObject import *
from Constants import *

class Bush(GameObject):

    @staticmethod
    def init():
        # image copied from https://www.roblox.com/library/389874929/cartoon-bush
        Bush.baseImage = pygame.image.load('./images/bush.png').convert_alpha()

    def __init__(self, x, y, r):
        super().__init__(x, y, r)
        w, h = self.rect.width, self.rect.height
        self.image = aspect_scale(Bush.baseImage, w, h)
        self.hp = 200
        # pygame.gfxdraw.filled_circle(self.image, r, r, r, BUSH_GREEN)

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

class TreeTop(GameObject):

    @staticmethod
    def init():
        # image copied from https://www.pngfind.com/mpng/Jmhooh_medium-image-cartoon-tree-top-view-hd-png/
        TreeTop.baseImage = pygame.image.load('./images/treetop.png').convert_alpha()

    def __init__(self, tree, game):
        super().__init__(tree.x, tree.y, TREETOP_RADIUS)
        self.hp = 10**9
        self.tree = tree
        self.game = game
        w, h = self.rect.width, self.rect.height
        self.image = aspect_scale(TreeTop.baseImage, w, h)
        alpha = 200
        self.image.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)

    def update(self, scrollX, scrollY):
        super().update(scrollX, scrollY)
        if self.tree.hp <= 0:
            self.game.treeTops.remove(self)


class Rock(GameObject):

    @staticmethod
    def init():
        # image copied from https://cliparts.zone/cartoon-rock-cliparts
        Rock.baseImage = pygame.image.load('./images/rock.png').convert_alpha()

    def __init__(self, x, y, r):
        super().__init__(x, y, r)
        self.hp = 500
        w, h = self.rect.width, self.rect.height
        self.image.blit(aspect_scale(Rock.baseImage.copy(), w, h), (0, 10))
        self.rect = pygame.Rect(x, y, self.image.get_width(), self.image.get_height())
        # pygame.gfxdraw.filled_circle(self.image, r, r, r, ROCK_GRAY)

class Border(pygame.sprite.Sprite):
    def ___init__(self, x, y, width, height):
        super().__init__()
        self.r = 10
        self.x, self.y, self.width, self.height= x, y, width, height
        self.hp = 10**9
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height))
        pygame.draw.rect(self.image, ROCK_GRAY, self.rect)

    def update(self, scrollX, scrollY):
        x = self.x - scrollX
        y = self.y - scrollY
        self.rect = pygame.Rect(x, y, self.width, self.height)
