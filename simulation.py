"""
File simulation.py
Author: Trevor Stalnaker

A small program for simulated simple cellular automata
"""

import pygame, random
import numpy as np
import matplotlib.pyplot as plt

SCREEN_SIZE = (1000,600) #Desired Screen Size (Not actual screen size)
STEP_TIME = .25
GRID_SIZE = (500,500)
LIVE_COLOR = (120,0,0)#(0,160,0)
DEAD_COLOR = (255,255,255)
BACKGROUND_COLOR = (160,160,160)
BORDERS = False
POPULATE = False
STROBE = False

COLORS = [DEAD_COLOR, LIVE_COLOR]

## Replicators:
#      -B1357/S1357 (from Wikipedia)
#      -B147/S4
#      -B12345/S467
#      -B146/S147
# Game of Life: B3/S23
# Life without Death: B3/S012345678
# Interesting Rule: B2/S35 -- glider [[0,1,0],[1,0,0],[1,0,0],[0,0,1]]
# Interesting Rule 2: B73648/S3810246
# Ripples: B123467/S
# Replicator without Death: B1/S1234567
# B1278/S234567
RULE = "B16482/S8512"

class Game():

    def __init__(self, gridSize, rule):

        pygame.init()
        pygame.display.set_caption("Automata Simulator")

        if POPULATE:
            a = np.random.choice(2, size=gridSize[0]*gridSize[1], p=[.95, .05])
            array = a.reshape(gridSize)
        else:
            array = np.zeros(gridSize)
        
            
        self._m = len(array) # number of rows
        self._n = len(array[0]) # number of columns

        x = SCREEN_SIZE[0] // self._m
        y = SCREEN_SIZE[1] // self._n
        self._tileDims = (x,y)
        self._actualScreenSize = (self._tileDims[0] * self._m,
                            self._tileDims[1] * self._n)
        
        self._screen = pygame.display.set_mode(self._actualScreenSize)

        self._g = Grid(self._actualScreenSize, self._tileDims, BACKGROUND_COLOR)
        self._image = None
        
        self._gameClock = pygame.time.Clock()
        self._timer = STEP_TIME
        self._stepTime = STEP_TIME
        
        self._RUNNING = True
        self._pause = False
        self._dragging = False

        self._rules = parseRule(rule)
        
        self._array = array
        self.makeInitialCheckList()
        self.makeDisplay()

    def draw(self):
        self._screen.blit(self._display, (0,0))
        if BORDERS:
            self._g.draw(self._screen)
        
        pygame.display.flip()
                
    def handleEvents(self):
        for event in pygame.event.get(): 
            if (event.type == pygame.QUIT):
                self._RUNNING = False

            # Pause the world
            if event.type == pygame.KEYDOWN and\
               event.key == pygame.K_p:
                if self._pause:
                    self.makeInitialCheckList()
                    self.makeDisplay()
                self._pause = not self._pause

            if event.type == pygame.KEYDOWN and\
               event.key == pygame.K_e:
                self.exportImage()


            # Clear the world
            if event.type == pygame.KEYDOWN and\
               event.key == pygame.K_c:
                for row in range(len(self._array)):
                    for column in range(len(self._array[0])):
                        self._array[row][column] = 0
                self.makeDisplay()

            # Repopulate the world
            if event.type == pygame.KEYDOWN and\
               event.key == pygame.K_n:
                a = np.random.choice(2, size=self._m*self._n, p=[.9, .1])
                self._array = a.reshape((self._m, self._n))
                self.makeDisplay()

            # Manage Mouse Dragging
            if self._pause:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self._dragging = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self._dragging = False
            else:
                self._dragging = False

            # Draw / Erase on the Screen
            if self._dragging:
                x, y = pygame.mouse.get_pos()
                column = x // self._tileDims[0]
                row = y // self._tileDims[1]
                # Check if Control Key is down
                state = pygame.key.get_mods() & pygame.KMOD_CTRL == 0
                self._array[column][row] = state
                self._image.set_at((column, row), COLORS[state])
                self.scaleDisplay()

    def makeDisplay(self):
        self.createGrid()
        self.scaleDisplay()

    def scaleDisplay(self):
        self._display = pygame.transform.scale(self._image, self._actualScreenSize)

    def createGrid(self):
        copy = []#self._array.copy()
        for row in range(len(self._array)):
            temp = []
            for column in range(len(self._array[0])):
                i = self._array[row][column]
                if i:
                    temp.append(LIVE_COLOR)
                else:
                    temp.append(DEAD_COLOR)
            copy.append(temp)
        s = np.asarray(copy)
        s = pygame.surfarray.make_surface(s)
        self._image = s

    def makeInitialCheckList(self):
        self._checkList = {}
        for row in range(len(self._array)):
            for column in range(len(self._array[row])):
                neighbors = self.getNeighbors((row, column))
                state = self._array[row][column]
                if state==1:
                    for n in neighbors:
                        if n in self._checkList:
                            self._checkList[n] += 1
                        else:
                            self._checkList[n] = 1

    def getNeighbors(self, pos):
        row, column = pos
        nextColumn = (column+1)%self._n
        prevColumn = (column-1)%self._n
        nextRow = (row+1)%self._m
        prevRow = (row-1)%self._m

        rows = [prevRow, row, nextRow]
        columns = [prevColumn, column, nextColumn]

        neighbors = []
        for r in rows:
            for c in columns:
                if r!=row or c!=column:
                    neighbors.append((r,c))
        return neighbors
                    
    def getLivingNeighborCount(self, neighbors):
        alive = 0
        for r, c in neighbors:
            alive += self._array[r][c]
        return alive

    def updateGrid(self):
        self._newCheckList = {}
        self._tempArray = np.zeros(self._array.shape)
        self._image.fill(COLORS[0])
        for coords, count in self._checkList.items():
            if count in self._rules[1] or count in self._rules[0]:
                row, column = coords
                state = self._array[row][column]
                # Survive
                if state==1 and count in self._rules[1]:
                    self.makeAlive(row, column)
                # Birth (come to life)
                elif state==0 and count in self._rules[0]:
                    self.makeAlive(row, column)
        self._array = self._tempArray
        self.scaleDisplay()
        self._checkList = self._newCheckList

    def makeAlive(self, row, column):
        self._tempArray[row][column] = 1
        self._image.set_at((row, column), COLORS[1])
        neighbors = self.getNeighbors((row, column))
        for n in neighbors:
            if n in self._newCheckList:
                self._newCheckList[n] += 1
            else:
                self._newCheckList[n] = 1

    def update(self):
        ticks = self._gameClock.get_time() /1000
        if STROBE:
            COLORS[0] = self.getRandomColor()
            COLORS[1] = self.getRandomColor()
        if not self._pause:
            if self._timer <= 0:
                self.updateGrid()
                self._timer = self._stepTime
            else:
                self._timer -= ticks

    def getRandomColor(self):
        def getColor():
            return random.randint(0,255)
        return (getColor(), getColor(), getColor())

    def runGameLoop(self):
        while self.isRunning():
            self._gameClock.tick()
            self.draw()
            self.handleEvents()
            self.update()
        pygame.quit()

    def isRunning(self):
        return self._RUNNING

    def exportImage(self):
        array = pygame.surfarray.array3d(self._display)
        array = array.swapaxes(0,1)
        plt.imsave("image.png", array)

class Grid():
    """Models the pixel grid display of rows and columns"""

    def __init__(self, screenDims, tileDims, color):
        surf = pygame.Surface(screenDims, pygame.SRCALPHA)
        verticalLines = screenDims[0]//tileDims[0]
        for i in range(verticalLines):
            x = i * tileDims[0]
            pygame.draw.line(surf, color, (x,0), (x,screenDims[1]), 1)
        horizontalLines = screenDims[1]//tileDims[1]
        for j in range(horizontalLines):
            y = j * tileDims[1]
            pygame.draw.line(surf, color, (0,y), (screenDims[0],y), 1)
            
        self._image = surf

    def draw(self, screen):
        screen.blit(self._image, (0,0))

def parseRule(rule):
    b, s = rule.split("/")
    b = [int(x) for x in b[1:]]
    s = [int(x) for x in s[1:]]
    return b, s

def getRandomRule():
    birthProb = .3
    survivalProb = .3
    b = [str(x) for x in range(1, 8) if random.random() <= birthProb]
    s = [str(x) for x in range(1, 8) if random.random() <= survivalProb]
    return "B%s/S%s" % ("".join(b), "".join(s))
        
if __name__ == "__main__":
    if RULE.upper() == "RANDOM":
        RULE = getRandomRule()
        print("Rule:", RULE)
    g = Game(GRID_SIZE, RULE)
    g.runGameLoop()
