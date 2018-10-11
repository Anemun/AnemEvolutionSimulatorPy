import sys
import pygame
import Colors
import Config
from Helpers import *
from enum import Enum, unique
from pygame.locals import *


class WorldObject(Enum):
    Self = -1,
    Empty = 0,
    Bot = 1,
    Organic = 2,
    Wall = 3


class WorldState(Enum):
    Paused = 0,
    Running = 1


class World(object):
    # worldSizeInCells = (0, 0)    # определяется при инициализации
    UNICELL_SIZE = Config.DRAW_CELL_SIZE[0]

    def __init__(self):
        self.worldSizeInCells = Config.WORLD_SIZE
        self.GRID_SIZE = ((self.worldSizeInCells[0] + 1) * Config.DRAW_CELL_SIZE[0],
                          (self.worldSizeInCells[1] + 1) * Config.DRAW_CELL_SIZE[1])
        self.worldMatrix = [[None] * self.worldSizeInCells[1] for i in range(self.worldSizeInCells[0])]
        print("World generated {0}:{1}".format(len(self.worldMatrix), len(self.worldMatrix[0])))

    def recreateWorld(self):
        self.worldMatrix.clear()
        self.worldMatrix = [[None] * self.worldSizeInCells[1] for i in range(self.worldSizeInCells[0])]

    def createBot(self, bot):
        bot.position = (loopValue(bot.position[0], 0, self.worldSizeInCells[0]-1), bot.position[1])
        self.worldMatrix[bot.position[0]][bot.position[1]] = bot

    def createOrganic(self, organic):
        self.worldMatrix[organic.position[0]][organic.position[1]] = organic

    def removeOrganic(self, organic):
        #position = (loopValue(organic.position[0], 0, self.worldSizeInCells[0]-1), position[1])
        #organic = self.worldMatrix[position[0]][position[1]]
        self.worldMatrix[organic.position[0]][organic.position[1]] = None

    def moveBot(self, bot, newPosition):
        newPos = (loopValue(newPosition[0], 0, self.worldSizeInCells[0]-1), newPosition[1])
        self.worldMatrix[bot.position[0]][bot.position[1]] = None
        self.worldMatrix[newPos[0]][newPos[1]] = bot
        bot.position = newPos

    def whatIsOnTile(self, tilePos):
        import Bot
        import Organic
        tilePosition = (loopValue(tilePos[0], 0, self.worldSizeInCells[0]-1), tilePos[1])
        #if tilePosition[0] < 0 or tilePosition[0] >= self.worldSizeInCells[0]:
        #   tilePosition[0] =
        if tilePosition[1] < 0 or \
           tilePosition[1] >= self.worldSizeInCells[1]:
            return WorldObject.Wall
            # try:
            # print("Looking to {0}:{1}".format(tilePosition[0], tilePosition[1]))
        if self.worldMatrix[tilePosition[0]][tilePosition[1]] is None:
            return WorldObject.Empty
        elif isinstance(self.worldMatrix[tilePosition[0]][tilePosition[1]], Bot.Bot):
            return WorldObject.Bot
        elif isinstance(self.worldMatrix[tilePosition[0]][tilePosition[1]], Organic.Organic):
            return WorldObject.Organic
            # except:
            #    print("exeption!")

    def getObjectFromTile(self, tilePos):
        tilePosition = (loopValue(tilePos[0], 0, self.worldSizeInCells[0] - 1), tilePos[1])
        return self.worldMatrix[tilePosition[0]][tilePosition[1]]

    def drawWorldGrid(self, displaysurf):
        for x in range(Config.DRAW_CELL_SIZE[0], self.GRID_SIZE[0] + Config.DRAW_CELL_SIZE[0], Config.DRAW_CELL_SIZE[0]):
            pygame.draw.line(displaysurf, Colors.Silver, (x, Config.DRAW_CELL_SIZE[0]), (x, self.GRID_SIZE[1]))
        for y in range(Config.DRAW_CELL_SIZE[1], self.GRID_SIZE[1] + Config.DRAW_CELL_SIZE[1], Config.DRAW_CELL_SIZE[1]):
            pygame.draw.line(displaysurf, Colors.Silver, (Config.DRAW_CELL_SIZE[1], y), (self.GRID_SIZE[0], y))

    @staticmethod
    def pixelPosFromCell(cellpos):
        return (Config.DRAW_CELL_SIZE[0] + (cellpos[0] * Config.DRAW_CELL_SIZE[0]),
                Config.DRAW_CELL_SIZE[1] + (cellpos[1] * Config.DRAW_CELL_SIZE[1]))

    def cellByPixel(self, pixelCoord):
        import math
        cellIndex = (math.trunc(pixelCoord[0] / World.UNICELL_SIZE) - 1,
                     math.trunc(pixelCoord[1] / World.UNICELL_SIZE) - 1)
        try:
            self.worldMatrix[cellIndex[0]][cellIndex[1]]
        except IndexError:
            return None
        return cellIndex
