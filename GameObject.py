import pygame

WIDTH = 600
HEIGHT = 600

class GameObject(pygame.sprite.Sprite):
    def __init__(self, x, y, r):
        super().__init__()
        self.x, self.y, self.r = x, y, r
        self.rect = pygame.Rect(x - r, y - r, 2 * r, 2 * r)
        self.image = pygame.Surface((2 * r, 2 * r,), pygame.SRCALPHA)
        self.image = self.image.convert_alpha()

    def update(self, keysDown, scrollX, scrollY):
        x = self.x - scrollX
        y = self.y - scrollY
        self.rect = pygame.Rect(x - self.r, y - self.r,
                                2 * self.r, 2 * self.r)