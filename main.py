import operator
import time
import signal
import sys
import pygame
from display import Display
from serialport import SerialPort
from util import Util
from button import Button

def loadTestData():
    t=[]
    t.append('GLG,120.6200,AM,0,0,14 ZOB Ultra Hi,ZOB Ultra Hi,HOLL-V,1,0,NONE,NONE')
    t.append('GLG,120.6250,AM,0,0,14 ZOB Ultra Hi,ZOB Ultra Hi,HOLL-V,1,0,NONE,NONE')
    t.append('GLG,120.6300,AM,0,0,14 ZOB Ultra Hi,ZOB Ultra Hi,HOLL-V,0,1,NONE,NONE')
    t.append('GLG,127.9000,AM,0,0,13 ZOB VHF,ZOB VHF,Carlton Low,1,0,NONE,NONE')
    t.append('GLG,127.9050,AM,0,0,13 ZOB VHF,ZOB VHF,Carlton Low,0,1,NONE,NONE')
    t.append('GLG,125.8800,AM,0,0,13 ZOB VHF,ZOB VHF,Brecksville Hi,1,0,NONE,NONE')
    t.append('GLG,125.8750,AM,0,0,13 ZOB VHF,ZOB VHF,Brecksville Hi,0,1,NONE,NONE')
    t.append('GLG,133.5250,AM,0,0,13 ZOB VHF,ZOB VHF,Wayne Super Hi,1,0,NONE,NONE')
    t.append('GLG,133.5150,AM,0,0,13 ZOB VHF,ZOB VHF,Wayne Super Hi,1,0,NONE,NONE')
    t.append('GLG,133.5050,AM,0,0,13 ZOB VHF,ZOB VHF,Wayne Super Hi,0,1,NONE,NONE')
    t.append('GLG,127.8000,AM,0,0,13 ZOB VHF,ZOB VHF,Carlton Low,1,0,NONE,NONE')
    t.append('GLG,127.7000,AM,0,0,13 ZOB VHF,ZOB VHF,Carlton Low,0,1,NONE,NONE')
    t.append('GLG,119.2750,AM,0,0,13 ZOB VHF,ZOB VHF,Ravenna Hi,1,0,NONE,NONE')
    t.append('GLG,119.3750,AM,0,0,13 ZOB VHF,ZOB VHF,Ravenna Hi,0,1,NONE,NONE')
    t.append('GLG,125.1150,AM,0,0,13 ZOB VHF,ZOB VHF,Brecksville Hi,0,1,NONE,NONE')
    t.append('GLG,133.1250,AM,0,0,13 ZOB VHF,ZOB VHF,Wayne Super Hi,1,0,NONE,NONE')
    t.append('GLG,133.1350,AM,0,0,13 ZOB VHF,ZOB VHF,Wayne Super Hi,1,0,NONE,NONE')
    t.append('GLG,133.1450,AM,0,0,13 ZOB VHF,ZOB VHF,Wayne Super Hi,0,1,NONE,NONE')
    t.append('GLG,127.1500,AM,0,0,13 ZOB VHF,ZOB VHF,Carlton Low,1,0,NONE,NONE')
    t.append('GLG,127.1600,AM,0,0,13 ZOB VHF,ZOB VHF,Carlton Low,0,1,NONE,NONE')
    t.append('GLG,119.1750,AM,0,0,13 ZOB VHF,ZOB VHF,Ravenna Hi,1,0,NONE,NONE')
    t.append('GLG,119.1850,AM,0,0,13 ZOB VHF,ZOB VHF,Ravenna Hi,0,1,NONE,NONE')

    hl=[]
    for i in t:
        h = loadHitData(i)
        hl = updateHitList(hl, h)
    
    return hl

def getSquelchFlag(rawData):
    d = rawData.split(',')
    if (len(d) != 13):  # ensure there's 13 elements.  powering off/on can return GLG with not enough elements
        return False
    elif (d[8] == "0"):
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
    global dsp
    global hits
    global curPage

    if curPage - 1 > 0:
        curPage -= 1
        dsp.displayHitList(hits, curPage)

def pageDownBtn():
    global dsp
    global hits
    global curPage

    numPages = dsp.getNumPages(hits)
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
hits=loadTestData()
dsp.displayHitList(hits, curPage)

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
                print(hit)
                hits = updateHitList(hits, loadHitData(hit))
                dsp.displayHitList(hits, curPage)

            if (gotHit and not sqFlag):
                gotHit = False

    if (pageDownBtn.isDisabled and dsp.getNumPages(hits) > 1):      # enable pgdown if > 1 page
        pageDownBtn.drawButton(Button.State.ON)

    if (pageDownBtn.isOn and curPage == dsp.getNumPages(hits)):     # disable pgdown if at end of pages
        pageDownBtn.drawButton(Button.State.DISABLED)

    if (pageUpBtn.isDisabled and curPage > 1):                      # enable pgup if > 1 page
        pageUpBtn.drawButton(Button.State.ON)

    if (pageDownBtn.isOn and curPage == 1):                         # disable pgup if at 1st page
        pageUpBtn.drawButton(Button.State.DISABLED)


    for event in pygame.event.get():
        if (event.type == pygame.FINGERUP or event.type == pygame.MOUSEBUTTONUP):
            for btn in buttonList:                
                if (btn.isSelected() and (not (btn.isDisabled() or btn.isHidden()))):
                    if (btn.getType() == Button.Type.STICKY):
                        btn.toggleButton()

                    if (btn.getType() == Button.Type.MOMENTARY):
                        btn.pushButton()

    dsp.refreshDisplay()

