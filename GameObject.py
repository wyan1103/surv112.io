import pygame

WIDTH = 600
HEIGHT = 600

pygame.font.init()

class GameObject(pygame.sprite.Sprite):
    def __init__(self, x, y, r):
        super().__init__()
        self.x, self.y, self.r = x, y, r
        self.rect = pygame.Rect(x - r, y - r, 2 * r, 2 * r)
        self.image = pygame.Surface((2 * r, 2 * r,), pygame.SRCALPHA).convert_alpha()
        self.imageCopy = self.image

    def update(self, scrollX, scrollY):
        x = self.x - scrollX
        y = self.y - scrollY
        self.rect = pygame.Rect(x - self.r, y - self.r,
                                2 * self.r, 2 * self.r)

# copied from https://www.pygame.org/pcr/transform_scale/aspect_scale.py
def aspect_scale(img, bx, by):
    """ Scales 'img' to fit into box bx/by.
     This method will retain the original image's aspect ratio """
    ix,iy = img.get_size()
    if ix > iy:
        # fit to width
        scale_factor = bx/float(ix)
        sy = scale_factor * iy
        if sy > by:
            scale_factor = by/float(iy)
            sx = scale_factor * ix
            sy = by
        else:
            sx = bx
    else:
        # fit to height
        scale_factor = by/float(iy)
        sx = scale_factor * ix
        if sx > bx:
            scale_factor = bx/float(ix)
            sx = bx
            sy = scale_factor * iy
        else:
            sy = by

    return pygame.transform.scale(img, (int(sx), int(sy)))