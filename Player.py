import pygame
import pygame.gfxdraw
from GameObject import GameObject

GRAY = (150, 150, 150)
WHITE = (0, 0, 0)

class Player(GameObject):
    def __init__(self, x, y, r):
        super().__init__(x, y, r)
        self.rect = pygame.Rect(x - r + 300, y - r + 300, 2 * r, 2 * r)
        pygame.gfxdraw.filled_circle(self.image, r, r, r, GRAY)
        pygame.gfxdraw.aacircle(self.image, r, r, r, WHITE)
        self.hasMoved = False

    def update(self, keysDown, obstacles):
        if keysDown(pygame.K_LEFT):
            self.x -= 5
        if keysDown(pygame.K_RIGHT):
            self.x += 5
        if keysDown(pygame.K_UP):
            self.y -= 5
        if keysDown(pygame.K_DOWN):
            self.y += 5

        # for _ in range(5):
        #     # do the move, saving previous position
        #     player = pygame.sprite.Group(self)
        #     prevX, prevY = self.x, self.y
        #     dx, dy = 0, 0
        #
        #     if keysDown(pygame.K_LEFT):
        #         dx = -1
        #     if keysDown(pygame.K_RIGHT):
        #         dx = 1
        #
        #     self.x += dx
        #     collisions = pygame.sprite.groupcollide(player, obstacles, False, False)
        #     if self in collisions:
        #         hasCollided = True
        #         self.x -= dx
        #
        #     if keysDown(pygame.K_DOWN):
        #         dy = 1
        #     if keysDown(pygame.K_UP):
        #         dy = -1
        #
        #     self.y += dy
        #     collisions = pygame.sprite.groupcollide(player, obstacles, False, False)
        #     if self in collisions:
        #         hasCollided = True
        #         self.y -= dy
        #
        #     if hasCollided:
        #         self.fixCollisions(dx, dy)
        #         print(self.x, self.y)
        #         break

    def fixCollisions(self, dx, dy):
        self.x -= dx
        self.y -= dy

    def changePID(self, PID):
        self.PID = PID
