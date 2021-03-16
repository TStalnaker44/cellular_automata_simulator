"""
File simulation.py
Author: Trevor Stalnaker

A small program for simulated simple cellular automata
"""

import pygame, random
import numpy as np

SCREEN_SIZE = (1200,800) #Desired Screen Size (Not actual screen size)
STEP_TIME = .25
GRID_SIZE = (300,200)
LIVE_COLOR = (0,160,0)
DEAD_COLOR = (255,255,255)
BACKGROUND_COLOR = (160,160,160)
BORDERS = False
POPULATE = True

COLORS = [DEAD_COLOR, LIVE_COLOR]

## Replicators:
#      -B1357/S1357 (from Wikipedia)
#      -B147/S4
#      -B12345/S467
# Game of Life: B3/S23
# Life without Death: B3/S012345678
# Interesting Rule: B2/S35 -- glider [[0,1,0],[1,0,0],[1,0,0],[0,0,1]]
RULE = "B12345/S467"

class Game():

    def __init__(self, gridSize, rule):

        pygame.init()
        pygame.display.set_caption("Conway's Game of Life")

        if POPULATE:
            a = np.random.choice(2, size=gridSize[0]*gridSize[1], p=[.9, .1])
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
                state = pygame.key.get_mods()% pygame.KMOD_CTRL == 0
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
        self._checkList = []
        for row in range(len(self._array)):
            for column in range(len(self._array[row])):
                neighbors = self.getNeighbors((row, column))
                state = self._array[row][column]
                if state==1:
                    self._checkList.append((row, column))
                    self._checkList.extend(neighbors)
        self._checkList = set(self._checkList)
                

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
        self._newCheckList = []
        tempArray = np.zeros(self._array.shape)
        self._image.fill(COLORS[0])
        for row, column in self._checkList:
                neighbors = self.getNeighbors((row, column))
                num = self.getLivingNeighborCount(neighbors)
                state = self._array[row][column]
                # Survive
                if state==1 and num in self._rules[1]:
                    tempArray[row][column] = 1
                    self._image.set_at((row, column), COLORS[1])
                    self._newCheckList.append((row, column))
                    self._newCheckList.extend(neighbors)
                # Birth (come to life)
                elif state==0 and num in self._rules[0]:
                    tempArray[row][column] = 1
                    self._image.set_at((row, column), COLORS[1])
                    self._newCheckList.append((row, column))
                    self._newCheckList.extend(neighbors)
        self._array = tempArray
        self.scaleDisplay()
        self._checkList = set(self._newCheckList)

    def update(self):
        ticks = self._gameClock.get_time() / 1000
        if not self._pause:
            if self._timer <= 0:
                self.updateGrid()
                self._timer = self._stepTime
            else:
                self._timer -= ticks

    def runGameLoop(self):
        while self.isRunning():
            self._gameClock.tick()
            self.draw()
            self.handleEvents()
            self.update()
        pygame.quit()

    def isRunning(self):
        return self._RUNNING

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
