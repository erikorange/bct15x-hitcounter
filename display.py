import os
import pygame
from pygame.locals import *
import datetime
from util import Util


class Display():
        
    def __init__(self, winFlag):
        self.__winFlag = winFlag

        self.__screenWidth = 700
        self.__screenHeight = 480
        self.__hitListHeight = 425
        self.__pageSize = 10            # max number of hits displayed per page
        
        self.__dataFlipLEDs = False
        self.__dataLED1x = self.__screenWidth - 10
        self.__dataLED2x = self.__screenWidth - 23
        self.__dataLEDy = self.__screenHeight - 28
        self.__dataLEDsize = 5
  
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

        self.__hitFont          = self.__defineFont(self.__winFlag, sansFont, 33) # hit text
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
        self.__green        = (0,255,0)
        self.__blue         = (0,0,255)
        self.__cyan         = (0,255,255)
        self.__white        = (255,255,255)
        
    def drawDataLEDs(self):
        pygame.draw.circle(self.__lcd, self.__red, (self.__dataLED1x,self.__dataLEDy), self.__dataLEDsize, 0)
        pygame.draw.circle(self.__lcd, self.__red, (self.__dataLED2x,self.__dataLEDy), self.__dataLEDsize, 0)

    def flipDataLEDs(self):
        if (self.__dataFlipLEDs):
            LED1 = self.__green
            LED2 = self.__red
        else:
            LED1 = self.__red
            LED2 = self.__green

        pygame.draw.circle(self.__lcd, LED1, (self.__dataLED1x,self.__dataLEDy), self.__dataLEDsize, 0)
        pygame.draw.circle(self.__lcd, LED2, (self.__dataLED2x,self.__dataLEDy), self.__dataLEDsize, 0)
        
        self.__dataFlipLEDs = not self.__dataFlipLEDs
        return

    def clearDisplayArea(self):
        pygame.draw.rect(self.__lcd, self.__black, (0,0,self.__screenWidth,self.__hitListHeight))

    def setupDisplay(self):
        self.__lcd.fill(self.__black)
        pygame.draw.line(self.__lcd, self.__blue, (0,self.__hitListHeight+2), (self.__screenWidth,self.__hitListHeight+2), width=1)
        pygame.display.update()
        pygame.event.clear()
    
    def getNumPages(self, hits):
        numHits = len(hits)
        if numHits == 0:
            return 1
        
        numPages = int(numHits/self.__pageSize)
        if numHits%self.__pageSize == 0:
            return numPages
        else:
            return numPages + 1

    def __calcRange(self, hits, curPage):
        numPages = self.getNumPages(hits)

        lowerBound = curPage*self.__pageSize - self.__pageSize
        if curPage < numPages:
          upperBound = curPage*self.__pageSize
        else:
          upperBound = len(hits)

        return (lowerBound, upperBound)


    def displayHitList(self, hitList, curPage):
        ypos = 0
        self.clearDisplayArea()
        (lowerBound, upperBound) = self.__calcRange(hitList, curPage)
        print(f"l:{lowerBound} u:{upperBound}")

        for i in range(lowerBound, upperBound):
            ts = hitList[i]["timestamp"].split(" ")[1]
            count = str(hitList[i]["count"])
            freq = hitList[i]["freq"][0:7]
            channel = hitList[i]["channel"]

            data = [{"text":ts,"anchor":"left","xpos":0,"color":self.__cyan},
                    {"text":count,"anchor":"right","xpos":210,"color":self.__white},
                    {"text":freq,"anchor":"left","xpos":240,"color":self.__green},
                    {"text":channel,"anchor":"left","xpos":380,"color":self.__green}]

            for l in data:
                txt = self.__hitFont.render(l["text"], 1, l["color"])
                txtRect = txt.get_rect()
                if l["anchor"] == "left":
                    txtRect.left = l["xpos"]
                else:
                    txtRect.right = l["xpos"]
                txtRect.y = ypos
                self.__lcd.blit(txt, txtRect)

            ypos += 42

    def refreshDisplay(self):
        pygame.display.update()
