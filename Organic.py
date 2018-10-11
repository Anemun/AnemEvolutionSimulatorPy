import Colors
import pygame
import Logic
import Config
import Helpers


class Organic(object):

    def __init__(self, position, food):
        self.position = position
        self.color = Colors.OrganicColor
        self.food = food
        self.timeLeft = Config.ORGANIC_MAX_TIME

    def draw(self, displaysurface):
        pos = Logic.gameWorld.pixelPosFromCell(self.position)
        size = (Config.DRAW_CELL_SIZE[0] - 1, Config.DRAW_CELL_SIZE[1] - 1)
        pos = (pos[0] + 1, pos[1] + 1)  # adjusting bot placement in the cell
        botRect = pygame.Rect((pos[0], pos[1], size[0], size[1]))
        pygame.draw.rect(displaysurface, self.color, botRect)
