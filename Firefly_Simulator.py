import pygame, random, time, math, sys
from pygame.locals import *
import threading as t
from io import StringIO


INITIATEEXIT = False


def getRandomTime(max=1.5):

    maxInt = int(max/0.02)
    toReturn = round(random.randint(12, maxInt) * 0.02, 2)
    print(toReturn)
    return toReturn

    #return min + round(max * random.random(), 2)


def rotatePolygon(polygon=[], angle=0, point=(0, 0)):
    newPolygon = []
    for i in polygon:
        x, y = i[0] - point[0], i[1] - point[1]
        x1 = x * math.cos(angle) - y * math.sin(angle) + point[0]
        y1 = x * math.sin(angle) + y * math.cos(angle) + point[1]
        newPolygon.append((x1, y1))

    return newPolygon


def randomRotatePolygon(polygon=[], point=(0, 0)):
    newPolygon = []
    angle = round(random.random(), 2) * 2 * round(math.pi, 2)
    for i in polygon:
        x, y = i[0] - point[0], i[1] - point[1]
        x1 = x * math.cos(angle) - y * math.sin(angle) + point[0]
        y1 = x * math.sin(angle) + y * math.cos(angle) + point[1]
        newPolygon.append((x1, y1))

    return newPolygon


occupiedLocations = []
def computeRandomUnoccupiedLocations():
    pass


def collide(polygon1=[], polygon2=[]):
    
    #checking if polygon2(Rect) pokes into polygon1(Triangle)
    pairsOfLines1 = []
    for i in polygon1:
        for j in polygon1:
            if i != j:
                pairsOfLines1.append([i, j])
    collisionBools = []
    for i in pairsOfLines1:
        x11, y11 = i[0][0], i[0][1]
        x21, y21 = i[1][0], i[1][1]
        for j in polygon2:
            x2, y2 = j[0], j[1]
            #ra = -1/()


class LinkRenderer:

    def __init__(self, flies=[]):
        self.flies = flies
        self.links = []
        self.drawSurface = pygame.Surface((600, 600), pygame.SRCALPHA)
        t.Thread(target=self.computeLinks).start()

    def computeLinks(self):

        global INITIATEEXIT
        value = round(1/60, 2)
        while not(INITIATEEXIT):
            time.sleep(3)
            self.links = []
            s = time.time()

            for i in self.flies:
                for j in self.flies:
                    if i != j and i.neighbour == j and [j, i] not in self.links and [i, j] not in self.links:
                        self.links.append([i, j])

            e = time.time()
            dt = round(e-s)
            if dt < value:
                time.sleep(value - dt)
            

    def draw(self, dis):
        links = list(self.links)
        for i in links:
            pygame.draw.aaline(self.drawSurface, (0, 255, 0, 255), i[0].pos, i[1].pos)
        dis.blit(self.drawSurface, (0, 0))

class Firefly:

    def __init__(self, pos=(200, 200)):

        self.pos = pos
        self.internalClock = getRandomTime()
        self.fireflyRadius = 10
        self.precerptionRadius = 60
        self.perceptionPolygon = []
        self.collisionRectangle = None
        self.percetptionRect = None
        self.neighbour = None
        self.static = False

        self.debug = True
        self.drawSurface = pygame.Surface((600, 600), pygame.SRCALPHA)

        self.computeGeometry()

        self.isFlashing = False
        self.timeSinceLastFlash = 0

        t.Thread(target=self.synchronize).start()


    def computeGeometry(self, angle=None):

        radius = self.precerptionRadius
        perceptionRect = pygame.Rect(
            self.pos[0] - radius,
            self.pos[1] - radius,
            2 * radius,
            2 * radius
        )
        PerceptionTriangle = [
            perceptionRect.topleft,
            perceptionRect.topright,
            self.pos
        ]
        if angle != None:
            self.static = True
            self.perceptionPolygon = rotatePolygon(PerceptionTriangle, angle, self.pos)
        else:
            self.perceptionPolygon = randomRotatePolygon(PerceptionTriangle, self.pos)
        self.collisionRectangle = pygame.Rect(
            self.pos[0] - self.fireflyRadius,
            self.pos[1] - self.fireflyRadius,
            2 * self.fireflyRadius,
            2 * self.fireflyRadius
        )

        self.percetptionRect = pygame.draw.polygon(self.drawSurface, (0, 0, 255, 100), self.perceptionPolygon)

    def synchronize(self):

        global INITIATEEXIT, timeCount

        while not(INITIATEEXIT):

            s = time.time()
            
            if self.isFlashing:
                if self.timeSinceLastFlash >= self.internalClock:
                    self.timeSinceLastFlash = 0
                    self.isFlashing = False
                else:
                    self.timeSinceLastFlash += round(1/60, 2)
            else:
                if self.timeSinceLastFlash >= self.internalClock:
                    self.timeSinceLastFlash = 0
                    self.isFlashing = True
                else:
                    self.timeSinceLastFlash += round(1/60, 2)

            e = time.time()
            dt = round(e - s, 2)
            if dt < 1/60:
                time.sleep(1/60 - dt)

    def percieve(self, flies=[]):

        global INITIATEEXIT

        flies = list(flies) 
        flies.remove(self)
        neighbour = None

        count = False
        value = round(1/60, 2)
        neighbourStates = []
        totalNumTrues, neighbourClock = 0, 0
        neighbourTries = 0
        calculateClock = False

        lookForSync = False
        syncStates = []
        syncTries = 0
        syncedOnce = False

        neighbourClockRecords = []

        while not(INITIATEEXIT):

            s = time.time()
            sr = self.getPerceptionRect()
            if not(neighbour):
                if self.debug: print("looking for neighbour")
                for i in flies:
                    otr = i.getCollisionRect()
                    if sr.colliderect(otr) and i.neighbour != self:
                        self.neighbour = i
                        neighbour = i
                        if self.debug: print("Neighbour locked!")
                        break
                else:
                    if not(self.static):
                        neighbourTries += 1
                        if neighbourTries >= 100:
                            neighbourTries = 0
                            self.computeGeometry()
            else:
                state = neighbour.isFlashing
                if len(neighbourStates) == 2:
                    neighbourStates.remove(neighbourStates[0])
                neighbourStates.append(state)

                if count:
                    if neighbourStates == [True, False]:
                        count = False
                        if self.debug: print("Stopped Counting")
                        calculateClock = True
                    totalNumTrues += 1
                    if self.debug: print("Total Trues -", totalNumTrues)

                #if not(neighbourClock) and neighbourStates and not(count) and not(lookForSync):
                if calculateClock:
                    totalNumTrues += 6
                    neighbourClock = round(totalNumTrues * 0.02, 2)
                    if self.debug: print("Neighbour's clock -", neighbourClock , "Trues -", totalNumTrues)
                    lookForSync = True
                    calculateClock = False

                if neighbourStates == [False, True] and not(totalNumTrues):
                    count = True
                    totalNumTrues += 1
                    if self.debug: print("Counting internal clock :", totalNumTrues)

                if lookForSync:
                    state = neighbour.isFlashing
                    if len(syncStates) == 2:
                        syncStates.remove(syncStates[0])
                    syncStates.append([self.isFlashing, state])
                    if self.debug: print("Syncing", syncStates)

                    if syncStates == [[False, False], [True, True]]:
                        self.internalClock = neighbourClock
                        if self.debug: print("Done")
                        syncedOnce = True
                        lookForSync = False

                    syncTries += 1
                    if lookForSync and syncTries >= 1500:
                        syncTries = 0
                        self.internalClock = getRandomTime(max=0.4)
                        if self.debug: print("Tries exceeded -", self.internalClock)

                    if syncedOnce:
                        if len(neighbourClockRecords) == 2:
                            neighbourClockRecords.remove(neighbourClockRecords[0])
                        nc = neighbour.internalClock
                        if neighbourClockRecords and nc not in neighbourClockRecords:
                            if self.debug: print("Found change in neighbour's internal clock")
                            #Reset back to tracking phase
                            if self.debug: print("Resetting...")
                            count = False
                            neighbourStates = []
                            totalNumTrues, neighbourClock = 0, 0
                            neighbourTries = 0
                            calculateClock = False
                            
                            syncStates = []
                            syncTries = 0
                            if self.debug: print("Reset complete reverting back to tracking phase")
                        else:
                            neighbourClockRecords.append(nc)

            e = time.time()
            dt = round(e - s, 2)
            if dt < value:
                time.sleep(value - dt)

    def getPerceptionRect(self):
        return self.percetptionRect

    def getCollisionRect(self):
        return self.collisionRectangle

    def draw(self, dis):
        
        self.drawSurface.fill((0, 0, 0, 0))
        if self.debug:
            pygame.draw.rect(self.drawSurface, (0, 255, 0, 100), self.collisionRectangle)
            self.perceptionRect = pygame.draw.polygon(self.drawSurface, (0, 0, 255, 100), self.perceptionPolygon)
            pygame.draw.rect(self.drawSurface, (0, 0, 255, 255), self.percetptionRect, 1)
        if self.isFlashing:
            pygame.draw.circle(self.drawSurface, (255, 255, 255, 255), self.pos, self.fireflyRadius)
        else:
            pygame.draw.circle(self.drawSurface, (255, 0, 0, 255), self.pos, self.fireflyRadius)

        dis.blit(self.drawSurface, (0, 0))


"""def synchronize(flies=[]):

    global INITIATEEXIT
    val = round(1/60, 2)
    states = {}
    for i in flies:
        states[i] = 0.00
    while not(INITIATEEXIT):

        s = time.time()

        for i in states:
            if i.isFlashing:
                if states[i] >= i.internalClock:
                    states[i] = 0
                    i.isFlashing = False
                else:
                    states[i] += val
            else:
                if states[i] >= i.internalClock:
                    states[i] = 0
                    i.isFlashing = True
                else:
                    states[i] += val                    

        e = time.time()
        dt = round(e - s, 2)
        if dt < val:
            time.sleep(val - dt)"""


mainDis = pygame.display.set_mode((600, 600))

tmp = Firefly(pos=(230, 180))
tmp.debug = False
fireflies = [
    Firefly(pos=(200, 200)), tmp
]

"""for i in range(80):
    fireflies.append(
        Firefly(pos=(
            random.randint(0, 560),
            random.randint(0, 560)
        ))
    )
for i in fireflies:
    t.Thread(target=i.percieve, args=(fireflies,)).start()"""
fireflies[0].computeGeometry(round(math.pi/2, 2))
t.Thread(target=fireflies[0].percieve, args=(fireflies,)).start()

lr = LinkRenderer(fireflies)

while not(INITIATEEXIT):

    for event in pygame.event.get():
        if event.type == QUIT:
            INITIATEEXIT = True
            break

    mainDis.fill((0, 0, 0))

    for i in fireflies:
        i.draw(mainDis)
    
    lr.draw(mainDis)

    pygame.display.flip()

    time.sleep(1/60)