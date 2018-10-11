import sys
import pygame
import Config
import World
import Logic
import Colors
import os
import datetime
import cProfile

from pygame.locals import *

# region ProfileCode
profile = cProfile.Profile()
# profile.enable()
# endregion
pygame.init()
logic = Logic
logic.Initialize()
pygame.display.set_caption("Жизнь ботов (старт {0})".format(logic.startTime))
RUNCLOCK = pygame.time.Clock()
DISPLAYSURF = pygame.display.set_mode(Config.WINDOW_SIZE)

screenCaptureFolderIndex = 1
todayDate = ""

import Interface
Interface.__init__(Config.WINDOW_SIZE)


def InitScreenshotCapture():
    global screenCaptureFolderIndex, todayDate
    todayDate = str(datetime.date.today().strftime('%Y-%m-%d'))
    while os.path.exists("{0}/{1}_{2}".format(Config.screenshotDefaultFolder, todayDate, screenCaptureFolderIndex)):
        screenCaptureFolderIndex += 1
    os.makedirs("{0}/{1}_{2}".format(Config.screenshotDefaultFolder, todayDate, screenCaptureFolderIndex))


if Config.captureScreenshots is True:
    InitScreenshotCapture()


def makeScreenshot():
    if Config.captureScreenshots is True:
        if logic.tickIndex % Config.screenshotDelay == 0:
            pygame.image.save(DISPLAYSURF, "{0}/{1}_{2}/{3}.jpg".format(
                                Config.screenshotDefaultFolder,
                                todayDate,
                                screenCaptureFolderIndex,
                                int(logic.tickIndex/Config.screenshotDelay)))


def tick():
    logic.ticksPerSecondCurrent = int(RUNCLOCK.get_fps())
    logic.tick()
    makeScreenshot()


logic.fillWorldWithOrganic(logic.DEFAULT_START_BOT_QUANTITY)
logic.fillWorldWithBots(logic.DEFAULT_START_BOT_QUANTITY)


def HandleEvents():
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            terminate()
        elif event.type == MOUSEMOTION:
            logic.mousePos = event.pos
        elif event.type == MOUSEBUTTONUP:
            logic.mousePos = event.pos
            if event.button == 1:
                logic.handleLeftClick()       # mouseButton = "Left"
            elif event.button == 2:                
                pass                    # mouseButton = "Middle"
            elif event.button == 3:                
                pass                    # mouseButton = "Right"
        elif event.type == KEYUP:
            if event.key == K_SPACE:
                logic.switchGameState()
            if event.key == K_UP:
                logic.gameSpeedUp()
            if event.key == K_DOWN:
                logic.gameSpeedDown()
            if event.key == K_x:
                logic.reset()

# region Events


def terminate():
    # profile.disable()
    # profile.print_stats(sort="time")
    pygame.quit()
    os._exit(0)
    #sys.exit(0)

# endregion

# main loop
while True:
    HandleEvents()
    DISPLAYSURF.fill(Colors.PanelColor)
    Interface.drawInterface(DISPLAYSURF, logic.selectedBot, logic.worldInfo)
    logic.gameWorld.drawWorldGrid(DISPLAYSURF)
    for bot in logic.activeBots:
       bot.draw(DISPLAYSURF)
    for organic in logic.organicInWorld:
       organic.draw(DISPLAYSURF)
    if logic.gameState == World.WorldState.Running:
        tick()
        if logic.tickIndex % 100 == 0:
            print(("Bots: {0}, Organic: {1}, tps: {2}, tick: {3}")
                  .format(len(logic.activeBots), len(logic.organicInWorld), logic.ticksPerSecondCurrent, logic.tickIndex))
    pygame.display.update()
    RUNCLOCK.tick(Config.MAX_TICKS_PER_SECOND)
