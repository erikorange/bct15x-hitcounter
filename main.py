import operator
import time
import signal
import sys
import pygame
from display import Display
from serialport import SerialPort
from util import Util
from button import Button

# if pagenum > 1 then enable pageup btn
# 
#
# pagedownBtn:
# numPages = int(len(hits)/10)+1
# If pageNum + 1 <= numPages
#     pageNum += 1

# 1 page = 0-9
# 2 page = 10 - 19
# 3 page = 20 - 24

# lowerBound = pageNum*10 - 10
# if pageNum < numPages
#   upperBound = pageNum*10 - 1
# else
#   upperBound = len(hits) - 1



def getSquelchFlag(rawData):
    d = rawData.split(',')
    if (d[8] == "0"):
        return False
    else:
        return True

def loadHitData(rawData):
    p = {}
    d = rawData.split(',')
    p['freq'] = d[1]
    p['bank'] = d[5]
    p['channel'] = d[7]
    t = time.localtime()
    p['timestamp_raw'] = t
    p['timestamp'] = time.strftime('%m-%d-%Y %H:%M:%S', t)
    return(p)

def updateHitList(dict, entry):
    idx = 0
    found = False

    while (idx < len(dict) and not found):
        item = dict[idx]
        if (item["freq"] == entry["freq"] and \
            item["bank"] == entry["bank"] and \
            item["channel"] == entry["channel"]):
            found = True
        else:
            idx += 1

    if (found):             # we located a duplicate entry, so just increment the count and update timestamp
        dict[idx]["count"] += 1
        t = time.localtime()
        dict[idx]["timestamp_raw"] = t
        dict[idx]["timestamp"] = time.strftime('%m-%d-%Y %H:%M:%S', t)
    else:                   # this is a new unique entry, so append
        entry['count'] = 1
        dict.append(entry)
    
    dict = sorted(dict, key=operator.itemgetter('timestamp_raw'), reverse=True)
    return dict

def shutdownEvent(signal, frame):
    sys.exit(0)

def holdBtnOn():
    global isHolding
    isHolding = True

def holdBtnOff():
    global isHolding
    isHolding = False
    
def pageUpBtn():
    print("page up")

def pageDownBtn():
    global hits
    global curPage

    numPages = int(len(hits)/10)+1
    if curPage + 1 <= numPages:
        curPage += 1
    
    dsp.displayHitList(hits, curPage)

def clrBtn():
    global hits, curPage, pageDownBtn, pageUpBtn, dsp
    hits = []
    dsp.clearDisplayArea()
    curPage = 1
    pageDownBtn.drawButton(Button.State.DISABLED)
    pageUpBtn.drawButton(Button.State.DISABLED)

def exitSystem():
    sys.exit(0)

winFlag = Util.isWindows()
if (not winFlag):
    signal.signal(signal.SIGTERM, shutdownEvent)
    signal.signal(signal.SIGINT, shutdownEvent)
    signal.signal(signal.SIGTSTP, shutdownEvent)
    Util.setCurrentDir('/home/pi/')
    serialPortName="/dev/ttyS0"
else:
    serialPortName="COM4"

dsp = Display(winFlag)
dsp.setupDisplay()
dsp.drawDataLEDs()
dsp.refreshDisplay()

medRed = (225,0,0)
medPurple = (80,0,80)
medBlue = (0,0,225)
green = (0,110,0)
gray = (128,128,128)
darkGreen=(0,128,0)
dataColor=(40,40,0)
white=(255,255,255)

# button variables
isHolding = False

btnY = 434
buttonList = []
holdBtn = Button(dsp.lcd, 5, btnY, 100, 40, dsp.btnFont, medPurple, gray, "HOLD", holdBtnOn, holdBtnOff, Button.State.OFF, Button.Type.STICKY)
buttonList.append(holdBtn)
pageDownBtn = Button(dsp.lcd, 115, btnY, 100, 40, dsp.btnFont, darkGreen, white, "DOWN", pageDownBtn, None, Button.State.DISABLED, Button.Type.MOMENTARY)
buttonList.append(pageDownBtn)
pageUpBtn = Button(dsp.lcd, 225, btnY, 100, 40, dsp.btnFont, darkGreen, white, "UP", pageUpBtn, None, Button.State.DISABLED, Button.Type.MOMENTARY)
buttonList.append(pageUpBtn)
clrBtn = Button(dsp.lcd, 335, btnY, 120, 40, dsp.btnFont, medBlue, white, "CLEAR", clrBtn, None, Button.State.ON, Button.Type.MOMENTARY)
buttonList.append(clrBtn)
exitBtn = Button(dsp.lcd, 565, btnY, 100, 40, dsp.btnFont, medRed, gray, "EXIT", exitSystem, None, Button.State.ON, Button.Type.MOMENTARY)
buttonList.append(exitBtn)

curPage = 1

sp = SerialPort(serialPortName)

hits=[]
gotHit = False

while True:
    sp.pollScanner()
    rawHit = sp.getScannerResponse()

    if (not isHolding) and sp.isValidResponse(rawHit):
        dsp.flipDataLEDs()
        hit = ''.join(rawHit.splitlines())
        if (hit != sp.isScanning):
            d = hit.split(',')
            sqFlag = getSquelchFlag(hit)

            if (not gotHit and sqFlag):
                gotHit = True
                print("got a hit")
                print(hit)
                hits = updateHitList(hits, loadHitData(hit))
                dsp.displayHitList(hits, curPage)

            if (gotHit and not sqFlag):
                gotHit = False

    if (len(hits) > 10 and pageDownBtn.isDisabled):
        pageDownBtn.drawButton(Button.State.ON)

    for event in pygame.event.get():
        if (event.type == pygame.FINGERUP or event.type == pygame.MOUSEBUTTONUP):
            for btn in buttonList:                
                if (btn.isSelected() and (not (btn.isDisabled() or btn.isHidden()))):
                    if (btn.getType() == Button.Type.STICKY):
                        btn.toggleButton()

                    if (btn.getType() == Button.Type.MOMENTARY):
                        btn.pushButton()

    dsp.refreshDisplay()

