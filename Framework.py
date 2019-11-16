import pygame
import Player

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                       #
#   Taken with modifications from:                                      #
#   http://blog.lukasperaza.com/getting-started-with-pygame/            #
#                                                                       #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class PygameGame(object):

    """
    a bunch of stuff is left out of this file, but you can check it out in the Github repo
    """

    def isKeyPressed(self, key):
        ''' return whether a specific key is being held '''
        return self._keys.get(key, False)

    def __init__(self, width=600, height=400, fps=50, title="112 Pygame Game"):
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title
        pygame.init()

    def run(self):

        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((self.width, self.height))
        # set the title of the window
        pygame.display.set_caption(self.title)

        # stores all the keys currently being held down
        self._keys = dict()

        # call game-specific initialization
        self.init()
        playing = True
        while playing:
            time = clock.tick(self.fps)
            self.timerFired(time)
            for event in pygame.event.get():
                # if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                #     self.mousePressed(*(event.pos))
                # elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                #     self.mouseReleased(*(event.pos))
                # elif (event.type == pygame.MOUSEMOTION and
                #       event.buttons == (0, 0, 0)):
                #     self.mouseMotion(*(event.pos))
                # elif (event.type == pygame.MOUSEMOTION and
                #       event.buttons[0] == 1):
                #     self.mouseDrag(*(event.pos))
                if event.type == pygame.KEYDOWN:
                    self._keys[event.key] = True
                    # self.keyPressed(event.key, event.mod)
                elif event.type == pygame.KEYUP:
                    self._keys[event.key] = False
                    # self.keyReleased(event.key, event.mod)
                if event.type == pygame.QUIT:
                    playing = False
            screen.fill((140, 217, 140))
            self.redrawAll(screen)
            pygame.display.flip()

        pygame.quit()
