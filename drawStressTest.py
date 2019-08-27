import sys
import Colors
import pygame
import random
from pygame.locals import *

pygame.init()
RUNCLOCK = pygame.time.Clock()
DISPLAYSURF = pygame.display.set_mode((1300, 1000))

def HandleEvents():
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            terminate()

def terminate():    
    pygame.quit()
    sys.exit(0)

def drawAll():
    font = pygame.font.match_font('monospace', bold=True)
    BASICFONT = pygame.font.Font(font, 12)
    FontColor = Colors.Black
    textSurf = BASICFONT.render('FPS: ' + str(int(RUNCLOCK.get_fps())), True, FontColor)
    textRect = textSurf.get_rect()
    textRect.top = 1
    textRect.left = 1
    DISPLAYSURF.blit(textSurf, textRect)    

    for x in range(0, 30):
        for y in range(0, 24):
            randColor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            botRect = pygame.Rect(50+x*4, 10+y*4, 3, 3)
            color = Colors.BlueBot
            pygame.draw.rect(DISPLAYSURF, randColor, botRect)

while True:
    HandleEvents()
    DISPLAYSURF.fill(Colors.PanelColor)
    drawAll()
    pygame.display.update()
    RUNCLOCK.tick(60)