from ShootyBot import *
import numpy as np

'''
Bot actions are learned through a reward system 
The emphasis placed on spacing and ability to remove randomly are determined
based on previous trials and their results
'''

# distance to player (emphasis placed on spreading out vs. pursuing player)
dtpStates = np.array([1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9])
# random move chance (to evade shots)
rmcStates = np.array([0.025, 0.05, 0.075, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06])
# random move duration (in seconds)
rmdStates = np.array([0.1, 0.2, 0.3, 0.4, 0.5])


def convertToProbability(rewards):
    total = np.sum(rewards)
    probabilities = rewards / total
    return probabilities

class ZombieBot(GameObject):
    learnRate = 1
    waveCount = 0
    dtp = None
    rmc = None
    rmd = None
    currentState = (0, 0, 0)
    stateIndices = (0, 0, 0)
    currentReward = 0
    numBots = 0
    difficulty = 0

    # create reward vector
    dtpRewards = np.zeros(len(dtpStates))
    rmcRewards = np.zeros(len(rmcStates))
    rmdRewards = np.zeros(len(rmdStates))

    @staticmethod
    def startWave(numBots):
        ZombieBot.waveCount += 1
        # normalize the lowest reward to 1 (to prevent nonpositive values) and convert to probability distribution
        ZombieBot.numBots = numBots
        dtpProbability = convertToProbability(ZombieBot.dtpRewards - np.min(ZombieBot.dtpRewards) + 1)
        rmcProbability = convertToProbability(ZombieBot.rmcRewards - np.min(ZombieBot.rmcRewards) + 1)
        rmdProbability = convertToProbability(ZombieBot.rmdRewards - np.min(ZombieBot.rmdRewards) + 1)

        # priority given to pursuing the player vs. spreading out
        dtpInd = np.where(dtpStates == np.random.choice(dtpStates, p=dtpProbability))[0][0]
        # odds that the bot makes a random move
        rmcInd = np.where(rmcStates == np.random.choice(rmcStates, p=rmcProbability))[0][0]
        # how long each random move lasts, in ticks
        rmdInd = np.where(rmdStates == np.random.choice(rmdStates, p=rmdProbability))[0][0]

        # store the results for later use after each wave
        ZombieBot.dtp = dtpStates[dtpInd]
        ZombieBot.rmc = rmcStates[rmcInd]
        ZombieBot.rmd = rmdStates[rmdInd]

        ZombieBot.currentState = (ZombieBot.dtp, ZombieBot.rmc, ZombieBot.rmd)
        ZombieBot.stateIndices = (dtpInd, rmcInd, rmdInd)

        ZombieBot.currentReward = 0

    @staticmethod
    def finishWave():
        dtp, rmc, rmd = ZombieBot.currentState
        reward = ZombieBot.currentReward / ZombieBot.numBots
        lr = ZombieBot.learnRate

        dtpIndex = list(dtpStates).index(dtp)
        rmcIndex = list(rmcStates).index(rmc)
        rmdIndex = list(rmdStates).index(rmd)


        # modify the reward table, taking the average of historical and recent rewards
        ZombieBot.dtpRewards[dtpIndex] = (ZombieBot.dtpRewards[dtpIndex] + reward * lr) / (1 + lr)
        ZombieBot.rmcRewards[rmcIndex] = (ZombieBot.rmcRewards[rmcIndex] + reward * lr) / (1 + lr)
        ZombieBot.rmdRewards[rmdIndex] = (ZombieBot.rmdRewards[rmdIndex] + reward * lr) / (1 + lr)

    def __init__(self, x, y, r=ZOMBIE_RADIUS):
        super().__init__(x, y, r)
        pygame.gfxdraw.filled_circle(self.image, r, r, r - 2, TAN)
        pygame.draw.circle(self.image, BLACK, (r, r), r, 3)
        self.moveSpeed = np.random.normal(4 + self.difficulty * 0.75, 1)
        self.dmg = 5
        self.hp = 50
        self.prevDistToPlayer = 0
        self.randomMoveStart = 0
        self.isInRandomMove = False
        self.randomMove = (0, 0)


    def update(self, scrollX, scrollY):
        ZombieBot.currentReward += 0.1  # reward bots for surviving longer
        super().update(scrollX, scrollY)


    def move(self, obstacles, others, target, time, score):
        dx, dy = self.getBotMove(obstacles, others, target, time)
        self.x += dx
        self.y += dy

        # if the bot is about to collide with something stop moving randomly
        if self.checkCollisions(obstacles, dx, dy):
            self.isInRandomMove = False

        dist = ((target.x - self.x) ** 2 + (target.y - self.y) ** 2) ** 0.5
        if dist <= self.r * 1.2 + target.r:
        # if near enough to attack, do damage and get rewarded
            target.takeDmg(self.dmg)
            self.x -= dx * 3
            self.y -= dy * 3
            ZombieBot.currentReward += 10

        if dist >= self.prevDistToPlayer:
            ZombieBot.currentReward -= 0.1      # punish bots for running away
        else:
            ZombieBot.currentReward += 0.1      # and reward them for going closer

        if dist > 800:
            ZombieBot.currentReward -= 40
            others.remove(self)                 # "Lose track" of the player if out of sight range
            # increase score for 'kills'
            score[0] += 10 + 2 * ZombieBot.waveCount

    def takeDmg(self, dmg, bots, score):
        # update score based on dmg dealt
        score[0] += min(dmg, self.hp) + ZombieBot.waveCount
        self.hp -= dmg
        ZombieBot.currentReward -= 5       # punish them for getting shot
        if self.hp <= 0:
            ZombieBot.currentReward -= 30   # and dying
            # increase score for kills
            score[0] += 10 + 2 * ZombieBot.waveCount
            bots.remove(self)

    def getBotMove(self, obstacles, others, target, time):
        bestMove = (0, 0)
        highestScore = -10**9

        # stop moving randomly after some time
        if time - self.randomMoveStart >= self.rmd * 1000:
            self.isInRandomMove = False

        # do the random move if it's already doing it
        if self.isInRandomMove:
            return self.randomMove

        # move in a random direction (to prevent too much pattern recognition)
        if random.random() < self.rmc:
            randX = 2 * (random.random() - 0.5) * self.moveSpeed
            randY = (self.moveSpeed ** 2 - randX ** 2) ** 0.5 * random.choice([-1, 1])
            self.randomMove = (randX, randY)
            self.isInRandomMove = True
            self.randomMoveStart = time
            return self.randomMove


        for i in range(20):
            # create a random dx and dy move, ignoring those that result in a collision
            randX = 2 * (random.random() - 0.5) * self.moveSpeed
            randY = (self.moveSpeed ** 2 - randX ** 2) ** 0.5 * random.choice([-1, 1])

            hasCollided = self.checkCollisions(obstacles, randX, randY)

            if not hasCollided:
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
        distanceToPlayer = ((target.y - moveY) ** 2 + (target.x - moveX) ** 2) ** 0.5
        return  minBotDistance - distanceToPlayer * ZombieBot.dtp

    def getDistanceToPlayer(self, player):
        return ((self.x - player.x) ** 2 + (self.y - player.y) ** 2) ** 0.5

    def checkCollisions(self, obstacles, dx, dy):
        for obstacle in obstacles:
            dx, dy = obstacle.x - (self.x + dx), obstacle.y - (self.y + dy)
            if (dx ** 2 + dy ** 2) ** 0.5 <= self.r * 1.5 + obstacle.r:
                return True
        return False

