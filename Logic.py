import Config
import Helpers

gameWorld = None
gameState = None
nextBotIndex = 0
startTime = 0

tickIndex = 0
ticksPerSecondCurrent = 0

activeBots = []
botsToAdd = []
botsToRemove = []
organicInWorld = []
organicToRemove = []
selectedBot = None

DEFAULT_START_BOT_QUANTITY = 0

worldInfo = {
    "tick": tickIndex,
    "ticksPerSecond": Config.MAX_TICKS_PER_SECOND,
    "ticksPerSecondCurrent": ticksPerSecondCurrent,
    "activeBots": 0,
    "organicQuantity": 0,
    "resetCount": 0
}

mousePos = (0, 0)


def Initialize():
    from datetime import datetime
    import World
    global startTime, gameWorld, gameState, DEFAULT_START_BOT_QUANTITY
    startTime = str(datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
    gameWorld = World.World()
    gameState = World.WorldState.Running
    DEFAULT_START_BOT_QUANTITY = int((gameWorld.worldSizeInCells[0] + gameWorld.worldSizeInCells[1]))
    pass


def newBot(botPosition, botParent=None):
    import Bot
    global nextBotIndex
    newbornBot = Bot.Bot(botPosition, nextBotIndex, botParent)
    nextBotIndex += 1
    gameWorld.createBot(newbornBot)
    botsToAdd.append(newbornBot)
    return newbornBot


def newOrgan(organPosition, botHead, newGenome):
    import Bot
    newbornOrgan = Bot.Organ(organPosition, botHead, newGenome)
    gameWorld.createBot(newbornOrgan)
    return newbornOrgan


def removeBot(bot):
    import Organic
    global selectedBot
    organic = Organic.Organic(bot.position, (bot.health + bot.energy))
    gameWorld.createOrganic(organic)
    organicInWorld.append(organic)
    activeBots.remove(bot)
    if bot == selectedBot:
        selectedBot = None


def attackBot(defenderCoord, force):
    import Bot
    defender = gameWorld.worldMatrix[defenderCoord[0]][defenderCoord[1]]
    if isinstance(defender, Bot.Bot):
        return defender.getDamage(force)
    else:
        return 0


def compareGenome(bot1, bot2):
    if bot1.genomeSize == bot2.genomeSize:
        genomeDifference = 0
        for i in range(0, bot1.genomeSize-1):
            if bot1.genome[i] != bot2.genome[i]:
                genomeDifference += 1
                if genomeDifference > Config.MAX_GENOME_DIFFERENCE:
                    return False
        return True
    else:
        return False


def placeOrganic(organicPosition, food=64):
    import Organic
    organic = Organic.Organic(organicPosition, food)
    gameWorld.createOrganic(organic)
    organicInWorld.append(organic)


def removeOrganic(organic):
    # organicCoord = (Helpers.loopValue(organicCoord[0], 0, gameWorld.worldSizeInCells[0]-1), organicCoord[1])
    gameWorld.removeOrganic(organic)
    try:
        #if organic is not None:
        organicInWorld.remove(organic)
    except ValueError:
        print("strange error")
    except AttributeError:
        print("strange error")
    return organic.food


def fillWorldWithBots(botCount: int, parent: object = None):
    import random
    import World
    for i in range(0, int(botCount/2)):
        xCoord = random.randint(0, gameWorld.worldSizeInCells[0] - 1)
        yCoord = random.randint(0, gameWorld.worldSizeInCells[1] - 1)
        targetCell = gameWorld.whatIsOnTile((xCoord, yCoord))
        if targetCell == World.WorldObject.Empty:
            if i % 4 == 0:
                newBot((xCoord, yCoord), parent)
            else:
                newBot((xCoord, yCoord), None)
                
                
def fillWorldWithOrganic(orgCount=int(DEFAULT_START_BOT_QUANTITY)):
    import random
    import World
    for i in range(0, orgCount):
        xCoord = random.randint(0, gameWorld.worldSizeInCells[0] - 1)
        yCoord = random.randint(0, gameWorld.worldSizeInCells[1] - 1)
        targetCell = gameWorld.whatIsOnTile((xCoord, yCoord))
        if targetCell == World.WorldObject.Empty:
            placeOrganic((xCoord, yCoord))
            
            
def updateNumbers():
    global worldInfo

    worldInfo["tick"] = tickIndex
    worldInfo["ticksPerSecond"] = int(Config.MAX_TICKS_PER_SECOND)
    worldInfo["ticksPerSecondCurrent"] = ticksPerSecondCurrent
    worldInfo["activeBots"] = len(activeBots)
    worldInfo["organicQuantity"] = len(organicInWorld)


def tick():
    global tickIndex
    tickIndex += 1

    if Config.RESPAWN_ORGANIC is True and tickIndex % Config.RESPAWN_ORGANIC_COUNTDOWN is 0:
        fillWorldWithOrganic(DEFAULT_START_BOT_QUANTITY)

    for bot in activeBots:
        bot.tick(tickIndex)
        if bot.health <= 0:
            if Config.GOD_MODE is False:
                botsToRemove.append(bot)

    for bot in botsToAdd:
        activeBots.append(bot)
    botsToAdd.clear()

    for botToRemove in botsToRemove:
        removeBot(botToRemove)
    botsToRemove.clear()

    if Config.ENABLE_ORGANIC_DISSAPEAR is True:
        for org in organicInWorld:
            org.timeLeft -= 1
            if org.timeLeft <= 0:
                organicToRemove.append(org)

    for organic in organicToRemove:
        removeOrganic(organic)
    organicToRemove.clear()

    updateNumbers()


# region Events

def handleLeftClick():
    import Bot
    import Interface
    global selectedBot
    clickedCell = gameWorld.cellByPixel(mousePos)
    if clickedCell is not None:
        if isinstance(gameWorld.worldMatrix[clickedCell[0]][clickedCell[1]], Bot.Bot):
            if isinstance(selectedBot, Bot.Bot):
                selectedBot.isSelected = False
            selectedBot = gameWorld.worldMatrix[clickedCell[0]][clickedCell[1]]
            selectedBot.isSelected = True
        else:
            if isinstance(selectedBot, Bot.Bot):
                selectedBot.isSelected = False
            selectedBot = None
    elif Helpers.isCoordsInRect(mousePos, Interface.buttonSpeedDownRect) is True:
        gameSpeedDown()
    elif Helpers.isCoordsInRect(mousePos, Interface.buttonSpeedUpRect) is True:
        gameSpeedUp()
    elif Helpers.isCoordsInRect(mousePos, Interface.buttonPauseRect) is True:
        switchGameState()
    elif Helpers.isCoordsInRect(mousePos, Interface.buttonResetRect) is True:
        reset()
    elif Helpers.isCoordsInRect(mousePos, Interface.buttonTickRect) is True:
        tick()


def gameSpeedUp():
    Config.MAX_TICKS_PER_SECOND = Config.MAX_TICKS_PER_SECOND * 2


def gameSpeedDown():
    Config.MAX_TICKS_PER_SECOND = Config.MAX_TICKS_PER_SECOND / 2
    if Config.MAX_TICKS_PER_SECOND < 1:
        Config.MAX_TICKS_PER_SECOND = 1


def switchGameState():
    import World
    global gameState
    if gameState == World.WorldState.Running:
        gameState = World.WorldState.Paused
    elif gameState == World.WorldState.Paused:
        gameState = World.WorldState.Running


def reset():
    global tickIndex
    worldInfo["resetCount"] += 1
    activeBots.clear()
    for org in organicInWorld:
        gameWorld.removeOrganic(org)
    organicInWorld.clear()
    gameWorld.recreateWorld()
    tickIndex = 0
    fillWorldWithBots(DEFAULT_START_BOT_QUANTITY)
# endregion
