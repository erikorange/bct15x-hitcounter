import pygame
import enum

class Button():

    class State(enum.Enum): 
        ON = 1
        OFF = 2
        DISABLED = 3
        HIDDEN = 4

    class Type(enum.Enum):
        MOMENTARY = 1
        STICKY = 2

    class Style(enum.Enum):
        TEXT = 0
        PAUSE = 1
        UP_ARROW = 2
        DOWN_ARROW = 3
        CLOCK = 4

    def __init__(self, screen, pos, size, style, font, btnColor, textColor, text, onCallback, offCallback, initialState, buttonType):
        self.__screen = screen
        self.__posX = pos[0]
        self.__posY = pos[1]
        self.__sizeX = size[0]
        self.__sizeY = size[1]
        self.__style = style
        self.__font = font
        self.__btnColorOff = pygame.Color(btnColor)
        self.__textColorOff = pygame.Color(textColor)
        if (buttonType == Button.Type.STICKY):
            self.__btnColorOn = pygame.Color(btnColor).correct_gamma(0.55)
            self.__textColorOn = pygame.Color(textColor).correct_gamma(0.55)
        else:
            self.__btnColorOn = pygame.Color(btnColor)
            self.__textColorOn = pygame.Color(textColor)

        self.__btnColorDisabled = pygame.Color((55,55,55))
        self.__textColorOff = pygame.Color(textColor)
        self.__textColorOn = pygame.Color(textColor).correct_gamma(0.25)
        self.__btnColorHidden = pygame.Color((0,0,0))
        self.__text = text
        self.__onCallback = onCallback
        self.__offCallback = offCallback
        self.__type = buttonType
        self.drawButton(initialState)

    def drawButton(self, state):
        if (state == self.State.ON):
            self.__state = self.State.ON
            self.__renderButton(self.__btnColorOn, self.__textColorOn)
        
        if (state == self.State.OFF):
            self.__state = self.State.OFF
            self.__renderButton(self.__btnColorOff, self.__textColorOff)

        if (state == self.State.DISABLED):
            self.__state = self.State.DISABLED
            self.__renderButton(self.__btnColorDisabled, self.__textColorOff)

        if (state == self.State.HIDDEN):
            self.__state = self.State.HIDDEN
            self.__renderButton(self.__btnColorHidden, self.__btnColorHidden)

    def __renderButton(self, bgColor, txtColor):
        self.__buttonRect = pygame.draw.rect(self.__screen, bgColor, (self.__posX, self.__posY, self.__sizeX, self.__sizeY), border_radius=10)
        centerX = self.__buttonRect.centerx
        centerY = self.__buttonRect.centery

        if (self.__style == self.Style.TEXT):
            txt = self.__font.render(self.__text, 1, txtColor)
            txtRect = txt.get_rect(center=(centerX, centerY))
            self.__screen.blit(txt, txtRect)

        elif (self.__style == self.Style.PAUSE):
            pWidth = 6
            pHeight = 20
            ctrOffset = 6

            lp = pygame.Rect(0,0,pWidth,pHeight)
            lp.center = (centerX - ctrOffset, centerY)
            pygame.draw.rect(self.__screen, txtColor, lp)

            rp = pygame.Rect(0,0,pWidth,pHeight)
            rp.center = (centerX + ctrOffset, centerY)
            pygame.draw.rect(self.__screen, txtColor, rp)

        elif (self.__style == self.Style.DOWN_ARROW):
            ctrOffset = 9
            pygame.draw.polygon(self.__screen, txtColor, [(centerX, centerY+ctrOffset), (centerX-ctrOffset, centerY-ctrOffset), (centerX+ctrOffset, centerY-ctrOffset),(centerX, centerY+ctrOffset)])

        elif (self.__style == self.Style.UP_ARROW):
            ctrOffset = 9
            pygame.draw.polygon(self.__screen, txtColor, [(centerX, centerY-ctrOffset), (centerX-ctrOffset, centerY+ctrOffset), (centerX+ctrOffset, centerY+ctrOffset),(centerX, centerY-ctrOffset)])     

        elif (self.__style == self.Style.CLOCK):
            ctrOffset = 14
    
            pygame.draw.circle(self.__screen, txtColor, (centerX, centerY), ctrOffset, width=2)
            
            mh = pygame.Rect(0, 0, 2, 8)
            mh.midbottom = (centerX, centerY)
            pygame.draw.rect(self.__screen, txtColor, mh)

            hh = pygame.Rect(0, 0, 7, 2)
            hh.midleft = (centerX, centerY)
            pygame.draw.rect(self.__screen, txtColor, hh)

        else:
            return

    def toggleButton(self):
        if (self.__state == self.State.OFF):
            self.drawButton(self.State.ON)
            self.__onCallback()
        else:
            self.drawButton(self.State.OFF)
            self.__offCallback()

    def pushButton(self):
        self.__onCallback()

    def isDisabled(self):
        if (self.__state == self.State.DISABLED):
            return True
        else:
            return False

    def isHidden(self):
        if (self.__state == self.State.HIDDEN):
            return True
        else:
            return False

    def isOn(self):
       if (self.__state == self.State.ON):
           return True
       else:
           return False
        
    def isSelected(self):
        return self.__buttonRect.collidepoint(pygame.mouse.get_pos())

    def getType(self):
        return self.__type

    def getState(self):
        return self.__state
