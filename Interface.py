import Colors
import pygame
import math as mt

reservedAreaRight = (0, 0)
reservedAreaBottom = (0, 0)
reservedAreaRightStartsAt = (0, 0)
reservedAreaBottomStartsAt = (0, 0)


buttonSpeedDownRect = (0, 0, 0, 0)
buttonPauseRect = (0, 0, 0, 0)
buttonSpeedUpRect = (0, 0, 0, 0)
buttonResetRect = (0, 0, 0, 0)
buttonTickRect = (0, 0, 0, 0)

botLogStartsAt = (0, 0)

standartButtonWidth = 60
standartButtonHeight = 20


font = pygame.font.match_font('monospace', bold=True)
# font = pygame.font.match_font('monaco', bold=False)
BASICFONT = pygame.font.Font(font, 12)
SMALLFONT = pygame.font.Font(font, 11)
FontColor = Colors.Black

WINDOW_SIZE = (0, 0)

isBotGenomeDrawed = False


def __init__(windowSize):
    global reservedAreaRight, reservedAreaBottom, reservedAreaRightStartsAt, reservedAreaBottomStartsAt,\
        buttonSpeedDownRect, buttonPauseRect, buttonSpeedUpRect, buttonResetRect, buttonTickRect, \
        botLogStartsAt, \
        WINDOW_SIZE

    WINDOW_SIZE = windowSize

    reservedAreaRight = (200, windowSize[1] - 200)
    reservedAreaBottom = (windowSize[0] - 200, 200)
    reservedAreaRightStartsAt = (windowSize[0] - 200, 0)
    reservedAreaBottomStartsAt = (0, windowSize[1] - 200)

    botLogStartsAt = (reservedAreaRightStartsAt[0] - 200, windowSize[1] - 195)

    speedButtonsTop = reservedAreaBottomStartsAt[1] + 40
    buttonSpeedDownRect = (reservedAreaBottomStartsAt[0] + 5, speedButtonsTop,
                           standartButtonWidth, standartButtonHeight)
    buttonPauseRect = (reservedAreaBottomStartsAt[0] + 10 + standartButtonWidth,
                       speedButtonsTop,
                       60, 20)
    buttonSpeedUpRect = (reservedAreaBottomStartsAt[0] + 15 + standartButtonWidth * 2,
                         speedButtonsTop,
                         60, 20)
    buttonResetRect = (reservedAreaBottomStartsAt[0] + 5,
                       reservedAreaBottomStartsAt[1] + 165,
                       60, 20)
    buttonTickRect = (buttonSpeedUpRect[0] + 5 + standartButtonWidth,
                      buttonSpeedUpRect[1],
                      standartButtonWidth, standartButtonHeight)


def fillWorld(displaysurf):
    pygame.draw.rect(displaysurf, Colors.FieldColor, (0, 0, reservedAreaRightStartsAt[0], reservedAreaBottomStartsAt[1]))


def drawReservedAreaLines(displaysurf):
    global reservedAreaRight, reservedAreaBottom
    pygame.draw.line(displaysurf, Colors.Black,  # вертикальная линия
                     (WINDOW_SIZE[0] - reservedAreaRight[0], 0),
                     (WINDOW_SIZE[0] - reservedAreaRight[0], reservedAreaRight[1]))
    pygame.draw.line(displaysurf, Colors.Black,  # горизонтальная линия
                     (0, WINDOW_SIZE[1] - reservedAreaBottom[1]),
                     (reservedAreaBottom[0], WINDOW_SIZE[1] - reservedAreaBottom[1]))


def drawWorldInfo(displaysurf, tick, ticksPerSecond, ticksPerSecondCurrent, activeBots=0, organicCount=0, resetCount=0):
    textSurf = BASICFONT.render('Ход: ' + str(tick), True, FontColor)
    textRect = textSurf.get_rect()
    textRect.top = (reservedAreaBottomStartsAt[1] + 5)
    textRect.left = reservedAreaBottomStartsAt[0] + 5
    displaysurf.blit(textSurf, textRect)

    textSurf = BASICFONT.render('Ходов в секунду (тек./макс.): {1}/{0}'
                                .format(str(ticksPerSecond), str(ticksPerSecondCurrent)), True, FontColor)
    textRect = textSurf.get_rect()
    textRect.top = (reservedAreaBottomStartsAt[1] + 20)
    textRect.left = reservedAreaBottomStartsAt[0] + 5
    displaysurf.blit(textSurf, textRect)

    textSurf = BASICFONT.render('Боты: {0}'
                                .format(str(activeBots)), True, FontColor)
    textRect = textSurf.get_rect()
    textRect.top = (reservedAreaBottomStartsAt[1] + 5)
    textRect.left = reservedAreaBottomStartsAt[0] + 300
    displaysurf.blit(textSurf, textRect)

    textSurf = BASICFONT.render('Органика: {0}'
                                .format(str(organicCount)), True, FontColor)
    textRect = textSurf.get_rect()
    textRect.top = (reservedAreaBottomStartsAt[1] + 20)
    textRect.left = reservedAreaBottomStartsAt[0] + 300
    displaysurf.blit(textSurf, textRect)
    textSurf = BASICFONT.render('Перезапусков мира: {0}'
                                .format(str(resetCount)), True, FontColor)
    textRect = textSurf.get_rect()
    textRect.top = (reservedAreaBottomStartsAt[1] + 35)
    textRect.left = reservedAreaBottomStartsAt[0] + 300
    displaysurf.blit(textSurf, textRect)


def drawBotLog(displaysurf, bot):
    logSurf = SMALLFONT.render("Лог действия бота:", True, FontColor)
    logRect = logSurf.get_rect()
    logRect.top = botLogStartsAt[1]
    logRect.left = botLogStartsAt[0] + 5
    displaysurf.blit(logSurf, logRect)
    pygame.draw.line(displaysurf, FontColor,
                     (botLogStartsAt[0] + 5, botLogStartsAt[1]+12),
                     (botLogStartsAt[0] + 200, botLogStartsAt[1]+12))
    for i in range(0, len(bot.botLog)):
        logSurf = SMALLFONT.render(bot.botLog[i], True, FontColor)
        logRect = logSurf.get_rect()
        logRect.top = botLogStartsAt[1] + 15 + 15*i
        logRect.left = botLogStartsAt[0] + 5
        displaysurf.blit(logSurf, logRect)


def drawBotInfo(displaysurf, bot):
    #if not isBotGenomeDrawed:
    drawBotGenome(displaysurf, bot)
    drawBotStats(displaysurf, bot)
    drawBotLog(displaysurf, bot)
    pass


def drawBotGenome(displaysurf, bot):
    global reservedAreaRightStartsAt, reservedAreaBottomStartsAt, isBotGenomeDrawed
    genomeDrawStartX = reservedAreaRightStartsAt[0] + 11
    genomeDrawStartY = 55

    # разделяем строку генома на 8 колонок для лучшего отображения
    botGenomeColumnsCount = 8

    # кол-во рядов для 8 колонок
    botGenomeRowCount = mt.trunc(len(bot.genome) / botGenomeColumnsCount)
    if (len(bot.genome) / botGenomeColumnsCount - botGenomeRowCount) > 0:
        botGenomeRowCount += 1

    # создаём из всего этого список со списками
    botGenomeMatrix = [bot.genome[i:i + botGenomeColumnsCount] for i in
                       range(0, len(bot.genome), botGenomeColumnsCount)]

    # для каждой строки
    for i in range(0, botGenomeRowCount):
        row = botGenomeMatrix[i]
        # для каждого символа в строке, рисуем этот символ
        for n in range(0, len(row)):
            s = str(row[n])
            textSurf = BASICFONT.render(s, True, FontColor)
            textRect = textSurf.get_rect()
            textRect.center = (genomeDrawStartX + 25 + (18 * n), genomeDrawStartY + 10 + (18 * i))

            # рисуем квадрат сетки вокруг символа
            gridRect = pygame.Rect(0, 0, 18, 18)
            gridRect.center = textRect.center

            # рисуем жёлтое выделение вокруг текущего указателя генома
            if bot.commandPointer % botGenomeColumnsCount == n and \
               mt.trunc(bot.commandPointer / botGenomeColumnsCount) == i:
                pygame.draw.rect(displaysurf, Colors.Yellow, gridRect, 1)
            else:
                pygame.draw.rect(displaysurf, Colors.Silver, gridRect, 1)

            displaysurf.blit(textSurf, textRect)


def drawBotStats(displaysurf, bot):
    index = ('Номер: ' + str(bot.index))
    indexSurf = BASICFONT.render(index, True, Colors.Black)
    indexRect = indexSurf.get_rect()
    indexRect.top = 5
    indexRect.left = reservedAreaRightStartsAt[0] + 5
    displaysurf.blit(indexSurf, indexRect)
    
    health = ('Здоровье: ' + str(bot.health))
    healthSurf = BASICFONT.render(health, True, FontColor)
    healthRect = healthSurf.get_rect()
    healthRect.top = 20
    healthRect.left = reservedAreaRightStartsAt[0] + 5
    displaysurf.blit(healthSurf, healthRect)

    energy = ('Энергия: ' + str(bot.energy))
    energySurf = BASICFONT.render(energy, True, FontColor)
    energyRect = energySurf.get_rect()
    energyRect.top = 35
    energyRect.left = reservedAreaRightStartsAt[0] + 5
    displaysurf.blit(energySurf, energyRect)

    color = ('' + str(bot.color))
    energySurf = BASICFONT.render(color, True, FontColor)
    energyRect = energySurf.get_rect()
    energyRect.top = 35
    energyRect.left = reservedAreaRightStartsAt[0] + 100
    displaysurf.blit(energySurf, energyRect)


# region --- Buttons ---
def drawSpeedButtons(displaysurf):
    # --- button SpeedDown ---
    pygame.draw.rect(displaysurf, Colors.Gray, buttonSpeedDownRect)
    pyButtonSpeedDownRect = pygame.draw.rect(displaysurf, FontColor, buttonSpeedDownRect, 1)
    textSurf = BASICFONT.render('Speed-', True, FontColor)
    textRect = textSurf.get_rect()
    textRect.center = pyButtonSpeedDownRect.center
    displaysurf.blit(textSurf, textRect)
    # button SpeedDown hotkey
    textSurf = BASICFONT.render('[ArrDown]', True, FontColor)
    textRect = textSurf.get_rect()
    textRect.center = pyButtonSpeedDownRect.center
    textRect.top = pyButtonSpeedDownRect.bottom
    displaysurf.blit(textSurf, textRect)

    # --- button Pause ---
    pygame.draw.rect(displaysurf, Colors.Gray, buttonPauseRect)
    pyButtonPauseRect = pygame.draw.rect(displaysurf, FontColor, buttonPauseRect, 1)
    textSurf = BASICFONT.render('Pause', True, FontColor)
    textRect = textSurf.get_rect()
    textRect.center = pyButtonPauseRect.center
    displaysurf.blit(textSurf, textRect)
    # button Pause hotkey
    textSurf = BASICFONT.render('[Space]', True, FontColor)
    textRect = textSurf.get_rect()
    textRect.center = pyButtonPauseRect.center
    textRect.top = pyButtonPauseRect.bottom
    displaysurf.blit(textSurf, textRect)

    # --- button SpeedUp ---
    pygame.draw.rect(displaysurf, Colors.Gray, buttonSpeedUpRect)
    pyButtonSpeedUpRect = pygame.draw.rect(displaysurf, FontColor, buttonSpeedUpRect, 1)
    textSurf = BASICFONT.render('Speed+', True, FontColor)
    textRect = textSurf.get_rect()
    textRect.center = pyButtonSpeedUpRect.center
    displaysurf.blit(textSurf, textRect)
    # button SpeedUp hotkey
    textSurf = BASICFONT.render('[ArrUp]', True, FontColor)
    textRect = textSurf.get_rect()
    textRect.center = pyButtonSpeedUpRect.center
    textRect.top = pyButtonSpeedUpRect.bottom
    displaysurf.blit(textSurf, textRect)

    # --- button Tick ---
    pygame.draw.rect(displaysurf, Colors.Gray, buttonTickRect)
    pyButtonTickRect = pygame.draw.rect(displaysurf, FontColor, buttonTickRect, 1)
    textSurf = BASICFONT.render('Tick', True, FontColor)
    textRect = textSurf.get_rect()
    textRect.center = pyButtonTickRect.center
    displaysurf.blit(textSurf, textRect)


def drawResetButton(displaysurf):
    # --- button Reset ---
    pygame.draw.rect(displaysurf, Colors.Gray, buttonResetRect)
    pyButtonResetRect = pygame.draw.rect(displaysurf, FontColor, buttonResetRect, 1)
    textSurf = BASICFONT.render('Reset', True, FontColor)
    textRect = textSurf.get_rect()
    textRect.center = pyButtonResetRect.center
    displaysurf.blit(textSurf, textRect)
    # button SpeedUp hotkey
    textSurf = BASICFONT.render('[X]', True, FontColor)
    textRect = textSurf.get_rect()
    textRect.center = pyButtonResetRect.center
    textRect.top = pyButtonResetRect.bottom
    displaysurf.blit(textSurf, textRect)


def drawControlButtons(displaysurf):
    drawSpeedButtons(displaysurf)
    drawResetButton(displaysurf)

# endregion


def drawInterface(displaysurf, selectedBot, worldData):
    fillWorld(displaysurf)
    drawReservedAreaLines(displaysurf)
    drawControlButtons(displaysurf)
    drawWorldInfo(displaysurf,
                  worldData["tick"], worldData["ticksPerSecond"], worldData["ticksPerSecondCurrent"],
                  worldData["activeBots"], worldData["organicQuantity"],
                  worldData["resetCount"])
    if selectedBot is not None:
        drawBotInfo(displaysurf, selectedBot)
