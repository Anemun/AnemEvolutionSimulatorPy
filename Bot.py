import Colors
import pygame
import math as mt
import World
import Helpers
import Logic
import Config
import random as rn
from pygame import *


class Bot(object):
    DRAW_BOT_SIZE = (Config.DRAW_CELL_SIZE[0] - 1, Config.DRAW_CELL_SIZE[1] - 1)
    MAX_LIFETIME = 1000
    ABSOLUTE_COMMAND_CAP = 10
    MAX_LOG_RECORDS = 10

    def __init__(self, position, index, parent=None, isOrgan=False):
        self.position = position
        self.lifetime = 0

        self._commandPointer = 0

        self.botLog = []
        self.tickIndex = 0

        self.executeNextCommand = False
        self.tickCommandCount = 0

        self.faceDirection = rn.randint(0, 7)  # 0 is up, 2 is right, 4 is down, 6 is left (for total 8 directions)
        self.isSelected = False

        self._color = Colors.InititalBotColor

        self.commandList = {
            0: self.command_Stay,
            1: self.command_Look,
            5: self.command_TurnRelative,
            10: self.command_Move,
            # 15: self.command_Multiply,
            16: self.command_CheckIfRelative,
            17: self.command_CheckHealth,
            18: self.command_CheckEnergy,
            19: self.command_GiveEnergy,
            20: self.command_Heal,
            25: self.command_Photosyntesis,
            30: self.command_Eat,
            35: self.command_GrowOrgan
        }

        if isOrgan: # TODO: а это работает??
            pass
        else:
            self.index = index
            self.genomeSize = 64
            self.organGenomeSize = 8
            self.mutateChance = 4  # чем больше значение, тем меньше шанс (1/x)
            self.maxHealth = self.genomeSize
            self.maxEnergy = self.genomeSize * 2
            self.genome = []
            self.organs = []
            self.movePoints = 0
            if parent is not None:
                self.createChildBot(parent)
            else:
                self._health = self.genomeSize
                self._energy = int(self.genomeSize / 2)
                self.writeToLog("A bot has born! (no parents)")
                #self.makePredefinedBots()
                self.genome = [rn.randint(0, self.genomeSize - 1) for i in range(self.genomeSize)]

    def createChildBot(self, parent):
        self.writeToLog("A bot has born! (parent: {0})".format(parent.index))
        self.genome = parent.genome[:]
        self.health = int(parent.health / 2)
        self.energy = int(parent.energy / 2)
        if rn.randint(1, self.mutateChance) == self.mutateChance:
            mutatePointer = rn.randint(0, self.genomeSize - 1)
            mutateValue = rn.randint(0, self.genomeSize - 1)
            self.genome[mutatePointer] = mutateValue


    @property
    def commandPointer(self):
        return self._commandPointer

    @commandPointer.setter
    def commandPointer(self, value):
        self._commandPointer = self.getLoopedValue(self.genomeSize, value)

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, value):
        if value < 0:
            self._health = 0
        elif value > self.maxHealth:
            self._health = self.maxHealth
        else:
            self._health = value

    @property
    def energy(self):
        return self._energy

    @energy.setter
    def energy(self, value):
        if value < 0:
            self._energy = 0
        else:
            self._energy = value
        if self._energy > self.maxEnergy:
            self.command_Multiply()

    @staticmethod
    def getLoopedValue(size, value):
        if size <= 0:
            return 0
        if value >= size:
            return value % size
        else:
            return value
            # while value >= size:
            #     value = value - size
            # else:
            #     return value

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = (Helpers.clampValue(value[0], 0, 255),
                       Helpers.clampValue(value[1], 0, 255),
                       Helpers.clampValue(value[2], 0, 255))


# region --- Commands ---

    def command_Stay(self):             # command 0
        self.writeToLog("Wait...")
        self.commandPointer += 1
        self.executeNextCommand = False

    def command_Look(self):             # command 1
        nextByte = self.getNextGenomeByte()     # смотрим, какой байт следующий в геноме

        # вычисляем значение относительного поворота
        lookValue = nextByte % 8
        # вычисляем направление в зависимости от того, куда повёрнут бот
        directionToLook = self.getLoopedValue(8, self.faceDirection + lookValue)

        # смотрим, что там находится
        coord = self.getAdjCoordByDirection(directionToLook)
        nearbyObject = Logic.gameWorld.whatIsOnTile(coord)
        if nearbyObject == World.WorldObject.Empty:
            self.writeToLog("Look to {0}({1}), saw nothing".format(directionToLook, coord))
            self.commandPointer += self.genome[self.getLoopedValue(self.genomeSize, self.commandPointer + 2)]
            self.executeNextCommand = True
        elif nearbyObject == World.WorldObject.Organic:
            self.writeToLog("Look to {0}({1}), saw Organic".format(directionToLook, coord))
            self.commandPointer += self.genome[self.getLoopedValue(self.genomeSize, self.commandPointer + 3)]
            self.executeNextCommand = True
        elif nearbyObject == World.WorldObject.Wall:
            self.writeToLog("Look to {0}({1}), saw Wall".format(directionToLook, coord))
            self.commandPointer += self.genome[self.getLoopedValue(self.genomeSize, self.commandPointer + 4)]
            self.executeNextCommand = True
        elif nearbyObject == World.WorldObject.Bot:
            anotherBot = Logic.gameWorld.getObjectFromTile(coord)
            if Logic.compareGenome(self, anotherBot) is True:
                self.writeToLog("Look to {0}({1}), saw Bot-relative".format(directionToLook, coord))
                self.commandPointer += self.genome[self.getLoopedValue(self.genomeSize, self.commandPointer + 5)]
                self.executeNextCommand = True
            else:
                self.writeToLog("Look to {0}({1}), saw Bot-stranger".format(directionToLook, coord))
                self.commandPointer += self.genome[self.getLoopedValue(self.genomeSize, self.commandPointer + 6)]
                self.executeNextCommand = True

    def command_TurnRelative(self):         # command 5
        nextByte = self.getNextGenomeByte()  # смотрим, какой байт следующий в геноме

        # вычисляем значение относительного поворота
        lookValue = nextByte % 8
        # вычисляем направление в зависимости от того, куда повёрнут бот
        directionToTurn = self.getLoopedValue(8, self.faceDirection + lookValue)
        self.faceDirection = directionToTurn

        # смотрим, что там находится
        coord = self.getAdjCoordByDirection(directionToTurn)
        nearbyObject = Logic.gameWorld.whatIsOnTile(coord)
        if nearbyObject == World.WorldObject.Empty:
            self.writeToLog("Turn to {0}({1}), saw nothing".format(directionToTurn, coord))
            self.commandPointer += self.genome[self.getLoopedValue(self.genomeSize, self.commandPointer + 2)]
            self.executeNextCommand = True
        elif nearbyObject == World.WorldObject.Organic:
            self.writeToLog("Turn to {0}({1}), saw Organic".format(directionToTurn, coord))
            self.commandPointer += self.genome[self.getLoopedValue(self.genomeSize, self.commandPointer + 3)]
            self.executeNextCommand = True
        elif nearbyObject == World.WorldObject.Wall:
            self.writeToLog("Turn to {0}({1}), saw Wall".format(directionToTurn, coord))
            self.commandPointer += self.genome[self.getLoopedValue(self.genomeSize, self.commandPointer + 4)]
            self.executeNextCommand = True
        elif nearbyObject == World.WorldObject.Bot:
            anotherBot = Logic.gameWorld.getObjectFromTile(coord)
            if Logic.compareGenome(self, anotherBot) is True:
                self.writeToLog("Turn to {0}({1}), saw Bot-relative".format(directionToTurn, coord))
                self.commandPointer += self.genome[self.getLoopedValue(self.genomeSize, self.commandPointer + 5)]
                self.executeNextCommand = True
            else:
                self.writeToLog("Turn to {0}({1}), saw Bot-stranger".format(directionToTurn, coord))
                self.commandPointer += self.genome[self.getLoopedValue(self.genomeSize, self.commandPointer + 6)]
                self.executeNextCommand = True

    def command_Move(self):
        if self.movePoints >= 1:      # command 10
            self.movePoints -= 1
            nearbyObject = Logic.gameWorld.whatIsOnTile(self.getAdjCoordByDirection(self.faceDirection))
            if nearbyObject == World.WorldObject.Empty:
                self.writeToLog("Moving to {0}".format(self.getAdjCoordByDirection(self.faceDirection)))
                #Logic.gameWorld.moveBot(self, self.getAdjCoordByDirection(self.faceDirection))
                # TODO: всё переделать нахер
                oldPosition = self.move(self, self.getAdjCoordByDirection(self.faceDirection))

                # TODO: движение органов!
                for i in range(len(self.organs)):
                    oldPosition = self.move(self.organs[i], oldPosition)

            else:
                self.writeToLog("Can't move to {0}, there is {1} there".format(
                                self.getAdjCoordByDirection(self.faceDirection), 
                                nearbyObject))
                pass

            self.commandPointer += 1
            if self.movePoints >= 1:
                self.executeNextCommand = True

        else:
            self.commandPointer += 1
            self.executeNextCommand = False

    def command_Multiply(self):             # command 15
        multiplyIsDone = False
        for direction in range(1, 8):
            coord = self.getAdjCoordByDirection(self.getLoopedValue(8, self.faceDirection+direction))
            coord = (Helpers.loopValue(coord[0], 0, Logic.gameWorld.worldSizeInCells[0] - 1), coord[1])
            nearbyObject = Logic.gameWorld.whatIsOnTile(coord)
            if nearbyObject == World.WorldObject.Empty:
                self.writeToLog("Making child bot at {0}".format(coord))
                Logic.newBot(coord, botParent=self)
                self.commandPointer += 1
                multiplyIsDone = True
                self.executeNextCommand = False
                self.health = int(self.health / 2.25)
                self.energy = int(self.energy / 2.25)
                break
        if multiplyIsDone is False:
            self.writeToLog("Tryed to make a child bot but there's no room!")
            if Config.DIE_IF_NO_ROOM is True:
                self.health = 0
            else:
                self.commandPointer += 2
                self.executeNextCommand = False

    def command_CheckIfRelative(self):      # command 16
        nextByte = self.getNextGenomeByte()  # смотрим, какой байт следующий в геноме

        # вычисляем значение относительного поворота
        lookValue = nextByte % 8
        # вычисляем направление в зависимости от того, куда повёрнут бот
        directionToCheck = self.getLoopedValue(8, self.faceDirection + lookValue)

        # смотрим, что там находится
        coord = self.getAdjCoordByDirection(directionToCheck)
        coord = (Helpers.loopValue(coord[0], 0, Logic.gameWorld.worldSizeInCells[0]-1), coord[1])
        nearbyObject = Logic.gameWorld.whatIsOnTile(coord)
        if nearbyObject == World.WorldObject.Bot:
            anotherBot = Logic.gameWorld.getObjectFromTile(coord)
            if Logic.compareGenome(self, anotherBot) is True:
                self.writeToLog("There is a relative at {0}!".format(coord))
                self.commandPointer += self.genome[self.getLoopedValue(self.genomeSize, self.commandPointer + 2)]
                self.executeNextCommand = True
            else:
                self.writeToLog("There is a stranger at {0}!".format(coord))
                self.commandPointer += self.genome[self.getLoopedValue(self.genomeSize, self.commandPointer + 3)]
                self.executeNextCommand = True

    def command_CheckHealth(self):      # command 17
        nextByte = self.getNextGenomeByte()
        if self.health <= nextByte:
            self.writeToLog("Cheking health, it's less than {0}".format(nextByte))
            self.commandPointer += self.genome[self.getLoopedValue(self.genomeSize, self.commandPointer + 2)]
            self.executeNextCommand = True
        else:
            self.writeToLog("Cheking health, it's more than {0}".format(nextByte))
            self.commandPointer += self.genome[self.getLoopedValue(self.genomeSize, self.commandPointer + 3)]
            self.executeNextCommand = True

    def command_CheckEnergy(self):      # command 18
        nextByte = self.getNextGenomeByte()
        if self.energy <= nextByte:
            self.writeToLog("Cheking energy, it's less than {0}".format(nextByte))
            self.commandPointer += self.genome[self.getLoopedValue(self.genomeSize, self.commandPointer + 1)]
            self.executeNextCommand = True
        else:
            self.writeToLog("Cheking energy, it's more than {0}".format(nextByte))
            self.commandPointer += self.genome[self.getLoopedValue(self.genomeSize, self.commandPointer + 2)]
            self.executeNextCommand = True

    def command_GiveEnergy(self):       # command 19 TODO: переделать/продумать
        # вычисляем значение относительного поворота
        nextByte = self.getNextGenomeByte()  # смотрим, какой байт следующий в геноме
        lookValue = nextByte % 8
        # вычисляем направление в зависимости от того, куда повёрнут бот
        directionToCheck = self.getLoopedValue(8, self.faceDirection + lookValue)

        # смотрим, что там находится
        coord = self.getAdjCoordByDirection(directionToCheck)
        coord = (Helpers.loopValue(coord[0], 0, Logic.gameWorld.worldSizeInCells[0]-1), coord[1])
        nearbyObject = Logic.gameWorld.whatIsOnTile(coord)
        if nearbyObject == World.WorldObject.Bot:
            anotherBot = Logic.gameWorld.getObjectFromTile(coord)
            energyToTransfer = self.getNextGenomeByte(self.commandPointer+1)
            self.energy -= energyToTransfer
            anotherBot.energy += energyToTransfer
            self.writeToLog("Giving {0} energy to bot#{1}".format(nextByte, anotherBot.index))
            self.commandPointer += self.genome[self.getLoopedValue(self.genomeSize, self.commandPointer + 2)]
            self.executeNextCommand = False
        else:
            self.writeToLog("Tried to give energy but there is nobody to receive")
            self.commandPointer += self.genome[self.getLoopedValue(self.genomeSize, self.commandPointer + 3)]
            self.executeNextCommand = False

    def command_Heal(self):             # command 20
        amountToHeal = int(self.energy/2)
        if amountToHeal > self.genomeSize - self.health:
            amountToHeal = self.genomeSize - self.health
        self.health += amountToHeal
        self.energy -= amountToHeal
        self.writeToLog("Healing for {0}".format(amountToHeal))
        self.commandPointer += 1
        self.executeNextCommand = False

    def command_Photosyntesis(self):    # command 25
        self.writeToLog("Photosyntesis!")
        self.energy += Config.PHOTOSYNTESIS_VALUE
        self.commandPointer += 1
        self.executeNextCommand = False
        self.adjustColor("Green")

    def command_Eat(self):              # command 30
        eatCoord = self.getAdjCoordByDirection(self.faceDirection)
        eatCoord = (Helpers.loopValue(eatCoord[0], 0, Logic.gameWorld.worldSizeInCells[0]-1), eatCoord[1])
        if Logic.gameWorld.whatIsOnTile(eatCoord) == World.WorldObject.Bot:
            attackForce = int(self.getNextGenomeByte() / 2)
            totalFood = Logic.attackBot(eatCoord, attackForce)    # атакуем то, что впереди
            foodToHealth = int(totalFood * Config.FOOD_TO_HEALTH)
            self.health += foodToHealth
            foodToEnergy = int(totalFood * Config.FOOD_TO_ENERGY)
            self.energy += foodToEnergy
            self.writeToLog(
                "Eat bot at {0}! Gained H/E: {1}/{2}"
                .format(eatCoord, foodToHealth, foodToEnergy))
            self.commandPointer += 2
            self.executeNextCommand = False
            self.adjustColor("Red")
        elif Logic.gameWorld.whatIsOnTile(eatCoord) == World.WorldObject.Organic:
            totalFood = Logic.removeOrganic(Logic.gameWorld.getObjectFromTile(eatCoord))
            foodToHealth = int(totalFood * Config.ORGANIC_TO_HEALTH)
            self.health += foodToHealth
            foodToEnergy = int(totalFood * Config.ORGANIC_TO_ENERGY)
            self.energy += foodToEnergy
            self.writeToLog(
                "Eat organic at {0}! Gained H/E: {1}/{2}"
                .format(eatCoord, foodToHealth, foodToEnergy))
            self.commandPointer += 3
            self.adjustColor("Red")
        else:
            self.writeToLog("Nothing to be eated!")
            self.commandPointer += 1
            self.executeNextCommand = False

    def command_GrowOrgan(self):    # command 35
        organGrowIsDone = False

        organGenome = [0] * self.organGenomeSize
        for i in range(self.organGenomeSize):
            organGenome[i] = self.genome[self.getLoopedValue(self.genomeSize, self.commandPointer+1+i)]

        for direction in range(1, 7):
            coord = self.getAdjCoordByDirection(self.getLoopedValue(8, self.faceDirection + direction))
            coord = (Helpers.loopValue(coord[0], 0, Logic.gameWorld.worldSizeInCells[0] - 1), coord[1])
            nearbyObject = Logic.gameWorld.whatIsOnTile(coord)
            if nearbyObject == World.WorldObject.Empty:
                self.writeToLog("Making organ at {0}".format(coord))
                self.organs.append(Logic.newOrgan(coord, self, organGenome))
                self.commandPointer += 1
                organGrowIsDone = True
                self.executeNextCommand = False
                self.health = int(self.health / 2.25)
                self.energy = int(self.energy / 2.25)
                break
        if organGrowIsDone is False:
            self.writeToLog("Tryed to grow organ but there's no room!")
            if Config.DIE_IF_NO_ROOM is True:
                self.health = 0
            else:
                self.commandPointer += 2
                self.executeNextCommand = False

    # endregion

    def adjustColor(self, newColor):
        if newColor == "Red":
            if self.color[0] < 128:
                self.color = (self.color[0] + 2, self.color[1] - 1, self.color[2] - 1)
            else:
                self.color = (self.color[0] + 1, self.color[1] - 1, self.color[2] - 1)
        if newColor == "Green":
            if self.color[1] < 128:
                self.color = (self.color[0] - 1, self.color[1] + 2, self.color[2] - 1)
            else:
                self.color = (self.color[0] - 1, self.color[1] + 1, self.color[2] - 1)
        if newColor == "Blue":
            if self.color[2] < 128:
                self.color = (self.color[0] - 1, self.color[1] - 1, self.color[2] + 2)
            else:
                self.color = (self.color[0] - 1, self.color[1] - 1, self.color[2] + 1)

    def makePredefinedBots(self):
        self.genome = [10] * self.genomeSize
        self.genome[1] = 10
        self.genome[2] = 10
        self.genome[3] = 35
        self.genome[4] = 35
        self.faceDirection = 0
        if self.index == 0:
            pass
        elif self.index == 1:
            pass



    # пишем в лог
    def writeToLog(self, message: str):
        if len(self.botLog) > Bot.MAX_LOG_RECORDS:
            del self.botLog[0]
        self.botLog.append('{0}: {1}'.format(self.tickIndex, message))

    def getAdjCoordByDirection(self, direction):
        coord = (None, None)
        direction = self.getLoopedValue(8, direction)  # last check just in case
        if direction == 0:
            coord = (self.position[0], self.position[1] - 1)
        elif direction == 1:
            coord = (self.position[0] + 1, self.position[1] - 1)
        elif direction == 2:
            coord = (self.position[0] + 1, self.position[1])
        elif direction == 3:
            coord = (self.position[0] + 1, self.position[1] + 1)
        elif direction == 4:
            coord = (self.position[0], self.position[1] + 1)
        elif direction == 5:
            coord = (self.position[0] - 1, self.position[1] + 1)
        elif direction == 6:
            coord = (self.position[0] - 1, self.position[1])
        elif direction == 7:
            coord = (self.position[0] - 1, self.position[1] - 1)

        # if coord[0] < 0:
        #     coord = (0, coord[1])
        # if coord[1] < 0:
        #     coord = (coord[0], 0)
        # if coord[0] > World.World.WORLD_SIZE_IN_CELLS[0]:
        #     coord = (World.World.WORLD_SIZE_IN_CELLS[0], coord[1])
        # if coord[1] > World.World.WORLD_SIZE_IN_CELLS[1]:
        #     coord = (coord[0], World.World.WORLD_SIZE_IN_CELLS[1])

        return coord

    def draw(self, displaysurface):
        pos = World.World.pixelPosFromCell(self.position)
        pos = (pos[0] + 1, pos[1] + 1)  # adjusting bot placement in the cell
        botRect = pygame.Rect((pos[0], pos[1], Bot.DRAW_BOT_SIZE[0], Bot.DRAW_BOT_SIZE[1]))
        pygame.draw.rect(displaysurface, self.color, botRect)

        # # стрелка направления
        # if self.faceDirection == 0:
        #     pygame.draw.line(displaysurface, Colors.White, botRect.center, botRect.midtop, 2)
        # elif self.faceDirection == 1:
        #     pygame.draw.line(displaysurface, Colors.White, botRect.center, botRect.topright, 2)
        # elif self.faceDirection == 2:
        #     pygame.draw.line(displaysurface, Colors.White, botRect.center, botRect.midright, 2)
        # elif self.faceDirection == 3:
        #     pygame.draw.line(displaysurface, Colors.White, botRect.center, botRect.bottomright, 2)
        # elif self.faceDirection == 4:
        #     pygame.draw.line(displaysurface, Colors.White, botRect.center, botRect.midbottom, 2)
        # elif self.faceDirection == 5:
        #     pygame.draw.line(displaysurface, Colors.White, botRect.center, botRect.bottomleft, 2)
        # elif self.faceDirection == 6:
        #     pygame.draw.line(displaysurface, Colors.White, botRect.center, botRect.midleft, 2)
        # elif self.faceDirection == 7:
        #     pygame.draw.line(displaysurface, Colors.White, botRect.center, botRect.topleft, 2)

        # выделение бота
        if self.isSelected:
            pygame.draw.rect(displaysurface, Colors.Yellow, botRect, 3)

        if len(self.organs) > 0:
            for i in range(len(self.organs)):
                self.organs[i].draw(displaysurface)
                if i is 0:
                    self.drawLineBetweenBots(displaysurface, self, self.organs[i])
                else:
                    self.drawLineBetweenBots(displaysurface, self.organs[i-1], self.organs[i])
            headCenterRect = pygame.Rect(
                int(botRect.left+1+Bot.DRAW_BOT_SIZE[0]/3),
                int(botRect.top+1+Bot.DRAW_BOT_SIZE[1]/3),
                int(Bot.DRAW_BOT_SIZE[0]/3.5),
                int(Bot.DRAW_BOT_SIZE[1]/3.5))
            headCenterRect.center = botRect.center
            pygame.draw.rect(displaysurface, Colors.Red, headCenterRect, 1)
                    
    def drawLineBetweenBots(self, displaysurface, botA, botB):
        if mt.fabs(botA.position[0] - botB.position[0]) > 2 or \
           mt.fabs(botA.position[1] - botB.position[1]) > 2:
            return

        posBotA = World.World.pixelPosFromCell(botA.position)
        posBotA = (posBotA[0] + 1, posBotA[1] + 1)
        rectBotA = pygame.Rect((posBotA[0], posBotA[1], Bot.DRAW_BOT_SIZE[0], Bot.DRAW_BOT_SIZE[1]))

        posBotB = World.World.pixelPosFromCell(botB.position)
        posBotB = (posBotB[0] + 1, posBotB[1] + 1)
        rectBotB = pygame.Rect((posBotB[0], posBotB[1], Bot.DRAW_BOT_SIZE[0], Bot.DRAW_BOT_SIZE[1]))

        pygame.draw.line(displaysurface, Colors.White, rectBotB.center, rectBotA.center, 1)

    def getNextGenomeByte(self, currentIndex: int = None) -> int:
        if currentIndex is None:
            currentIndex = self.commandPointer
        newIndex = self.getLoopedValue(self.genomeSize, currentIndex + 1)
        return self.genome[newIndex]

    def executeCommand(self):
        self.tickCommandCount += 1
        command = self.genome[self.commandPointer]
        if command in self.commandList.keys():
            self.commandList[command]()
        else:
            self.commandPointer += command
            self.executeNextCommand = True

    def tick(self, tickIndex):
        self.movePoints = 1

        if len(self.organs) > 0:
            for i in range(0, len(self.organs)-1):
                self.organs[i].tick(tickIndex)

        self.tickIndex = tickIndex
        self.executeNextCommand = True
        self.health -= 1
        while self.executeNextCommand is True and self.tickCommandCount < Bot.ABSOLUTE_COMMAND_CAP:
            self.executeCommand()
        self.tickCommandCount = 0
        self.lifetime += 1
        if Config.DIE_OF_AGE is True:
            if self.lifetime >= self.MAX_LIFETIME:
                self.health = 0

    # когда кто-то пытается съесть бота
    def getDamage(self, damage):
        myForce = int(self.health / 2)  # сила бота равна половине его хп
        if damage > myForce:  # если сила атакующего выше, то
            self.writeToLog("Get attacked, lose {0}hp".format(myForce))
            self.health -= myForce
            return myForce  # отдаём половину хп
        else:
            dmg = int(myForce / 4)
            self.writeToLog("Defended, lose {0}hp".format(dmg))
            self.health -= dmg
            return dmg  # иначе отдаём одну 16-ю хп

    def move(self, bot, newPosition):
        oldPosition = bot.position
        self.writeToLog("Moving to {0}".format(newPosition))
        Logic.gameWorld.moveBot(bot, newPosition)
        return oldPosition


class Organ(Bot):
    # TODO: взаимодействие с миром
    # TODO: максимальное здоровье/энергия
    def __init__(self, position, parent, genome):
        super().__init__(position, parent.index)

        self.headBot = parent
        self.index = self.headBot.index
        self.genome = genome
        self.genomeSize = len(self.genome)

    @property
    def health(self):
        return self.headBot.health

    @health.setter
    def health(self, value):
        self.headBot.health = value

    @property
    def energy(self):
        return self.headBot.energy

    @energy.setter
    def energy(self, value):
        self.headBot.energy = value

    def command_Move(self):         # command 5     Move will add to the head's move points
        self.writeToLog("Giving one more move to Head")
        self.headBot.movePoints += 1
        self.commandPointer += 1
        self.executeNextCommand = False

    def command_Multiply(self):     # command 15    Will do nothing since organs can't multiply
        self.commandPointer += 15
        self.executeNextCommand = True

    def command_GrowOrgan(self):    # command 35    Will do nothing since organs can't grow organs
        self.commandPointer += 35
        self.executeNextCommand = True

    def tick(self, tickIndex):
        self.health += 2
        self.energy += 1

        self.tickIndex = tickIndex
        self.executeNextCommand = True
        self.health -= 0.75
        while self.executeNextCommand is True and self.tickCommandCount < Bot.ABSOLUTE_COMMAND_CAP:
            self.executeCommand()
        self.tickCommandCount = 0
        self.lifetime += 1
        if Config.DIE_OF_AGE is True:
            if self.lifetime >= self.MAX_LIFETIME:
                self.health = 0

    def draw(self, displaysurface):
        pos = World.World.pixelPosFromCell(self.position)
        pos = (pos[0] + 1, pos[1] + 1)  # adjusting bot placement in the cell
        botRect = pygame.Rect((pos[0], pos[1], Bot.DRAW_BOT_SIZE[0], Bot.DRAW_BOT_SIZE[1]))
        pygame.draw.rect(displaysurface, self.color, botRect)

        # posHead = World.World.pixelPosFromCell(self.headBot.position)
        # posHead = (posHead[0] + 1, posHead[1] + 1)
        # botRectHead = pygame.Rect((posHead[0], posHead[1], Bot.DRAW_BOT_SIZE[0], Bot.DRAW_BOT_SIZE[1]))
        # pygame.draw.line(displaysurface, Colors.White, botRect.center, botRectHead.center, 1)

        if self.isSelected:
            pygame.draw.rect(displaysurface, Colors.Yellow, botRect, 3)

