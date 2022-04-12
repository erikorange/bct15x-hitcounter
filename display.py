import os
import pygame
from pygame.locals import *
import datetime
from util import Util


class Display():
        
    def __init__(self, winFlag):
        self.__winFlag = winFlag

        self.__screenWidth = 800
        self.__screenHeight = 480
        
        self.__dataFlipLEDs = False
        self.__dataLED1x = 10
        self.__dataLED2x = 23
        self.__dataLEDy = 10

        self.__initDisplay()
        self.__initFonts()
        self.__initColors()
    
    def __initDisplay(self):
        pygame.init()

        if (self.__winFlag):
            self.__lcd = pygame.display.set_mode((self.__screenWidth, self.__screenHeight))
        else:
            pygame.mouse.set_visible(False)
            flags = pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE
            self.__lcd = pygame.display.set_mode((self.__screenWidth, self.__screenHeight), flags)

    @property
    def lcd(self):
        return self.__lcd

    def __initFonts(self):
        if (self.__winFlag):
            sansFont = "microsoftsansserif"
            monoFont = "couriernew"
        else:
            sansFont = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
            monoFont = "/usr/share/fonts/truetype/freefont/FreeMono.ttf"

        self.__recentFont       = self.__defineFont(self.__winFlag, sansFont, 20) # civ and mil recents
        self.btnFont            = self.__defineFont(self.__winFlag, sansFont, 30) # buttons
        self.btnRadarFont       = self.__defineFont(self.__winFlag, monoFont, 50) # radar +/- buttons

    def __defineFont(self, winflag, fontFamily, size):
        if (self.__winFlag):
            return pygame.font.SysFont(fontFamily, size)
        else:
            return pygame.font.Font(fontFamily, size)

    def __initColors(self):
        self.__black        = (0,0,0)
        self.__red          = (255,0,0)
        self.__medRed       = (128,0,0)
        self.__yellow       = (255,255,0)
        self.__green        = (0,255,0)
        self.__medGreen     = (0,128,0)
        self.__easyWhite    = (200,200,200)
        self.__white        = (255,255,255)
        
    def drawDataLEDs(self):
        pygame.draw.circle(self.__lcd, self.__medRed, (self.__dataLED1x,self.__dataLEDy), 5, 0)
        pygame.draw.circle(self.__lcd, self.__medRed, (self.__dataLED2x,self.__dataLEDy), 5, 0)

    def flipDataLEDs(self):
        if (self.__dataFlipLEDs):
            LED1 = self.__medGreen
            LED2 = self.__medRed
        else:
            LED1 = self.__medRed
            LED2 = self.__medGreen

        pygame.draw.circle(self.__lcd, LED1, (self.__dataLED1x,self.__dataLEDy), 5, 0)
        pygame.draw.circle(self.__lcd, LED2, (self.__dataLED2x,self.__dataLEDy), 5, 0)
        
        self.__dataFlipLEDs = not self.__dataFlipLEDs
        return

    def clearDisplayArea(self):
        pygame.draw.rect(self.__lcd, self.__black, (0,0,self.__screenWidth,427))

    def setupDisplay(self):
        self.__lcd.fill(self.__black)
        pygame.display.update()
        pygame.event.clear()

    def displayHitList(self, hitList):
        xpos = 0
        ypos = 20
        self.clearDisplayArea()

        for i in hitList:
            theHit = f'{i["timestamp"].split(" ")[1]} {str(i["count"])} {i["freq"][0:7]} {i["channel"]}'
            txt = self.__recentFont.render(theHit, 1, self.__white, self.__black)
            self.__lcd.blit(txt, (xpos, ypos))
            ypos += 32

    def refreshDisplay(self):
        pygame.display.update()
