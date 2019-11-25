from Bot import *
import numpy

'''
Bot actions be learned as the game progresses using Q-learning,
where states represent the number of bots active (3-10) and actions represent
parameters for random movement and group actions (distToPlayerWeight), with
a discount factor of 0.
'''

distToPlayerStates = [i // 100 for i in range(110, 300, 10)]
distToPlayerProbabilities = [1 / len(distToPlayerStates) for _ in range(len(distToPlayerStates))]


randomMoveChanceStates = [i // 10 for i in range(1, 10)]
randomMoveDuration = [i for i in range(5, 20)]

class ZombieBot(Player):

    distToPlayerWeight = 1.5    # priority given to pursuing the player vs. spreading out
    randomMoveChance = 0.5      # odds that the bot makes a random move
    randomMoveDuration = 10     # how long each random move lasts, in ticks

    def __init__(self, x, y, r=ZOMBIE_RADIUS):
        super().__init__(x, y, r)
        self.moveSpeed = 8
        self.isInRandomMove = False


    def update(self, scrollX, scrollY):
        super(Player, self).update(scrollX, scrollY)

    def move(self, obstacles, others, target):
        dx, dy = self.getBotMove(obstacles, others, target)
        self.x += dx
        self.y += dy

    def getBotMove(self, obstacles, others, target):
        bestMove = (0, 0)
        highestScore = -10**9
        for i in range(100):

            # create a random dx and dy move, ignoring those that result in a collision
            randX = 2 * (random.random() - 0.5) * self.moveSpeed
            randY = (self.moveSpeed ** 2 - randX ** 2) ** 0.5 * random.choice([-1, 1])
            # tempBot = pygame.sprite.Group(ZombieBot(self.x + randX, self.y + randY))
            # while tempBot in pygame.sprite.groupcollide(tempBot, obstacles, True, False):
            #     randX = random.random() * 5
            #     randY = (self.moveSpeed ** 2 - randX ** 2) ** 0.5
            #     tempBot = pygame.sprite.Group(ZombieBot(self.x + randX, self.y + randY))

            # calculate the score of the move based on distance to target and other bots
            moveScore = self.getMoveScore(randX, randY, others, target)
            if moveScore > highestScore:
                highestScore = moveScore
                bestMove = (randX, randY)
        return bestMove

    def getMoveScore(self, dx, dy, others, target):
        moveX, moveY = self.x + dx, self.y + dy
        minBotDistance = 10**9
        for bot in others:
            if bot == self: continue
            distance = ((bot.y - moveY) ** 2 + (bot.x - moveX) ** 2) ** 0.5
            if distance < minBotDistance:
                minBotDistance = distance

        print(minBotDistance)
        distanceToPlayer = ((target.y - moveY) ** 2 + (target.x - moveX) ** 2) ** 0.5
        return  minBotDistance - distanceToPlayer * self.distToPlayerWeight
