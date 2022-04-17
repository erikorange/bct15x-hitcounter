import operator
import time
import signal
import sys
import pygame
from display import Display
from serialport import SerialPort
from util import Util
from button import Button


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
    isHolding = True

def holdBtnOff():
    isHolding = False


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

medRed = (80,0,0)
medPurple = (80,0,80)
medBlue = (0,0,80)
green = (0,110,0)
gray = (128,128,128)
darkGreen=(0,32,0)
dataColor=(40,40,0)
white=(255,255,255)

isHolding = False

btnY = 440
buttonList = []
holdBtn = Button(dsp.lcd, 5, btnY, 100, 40, dsp.btnFont, medPurple, gray, "HOLD", holdBtnOn, holdBtnOff, Button.State.OFF, Button.Type.STICKY)
buttonList.append(holdBtn)


#milBtn = Button(dsp.lcd, 115, 438, 100, 40, dsp.btnFont, darkGreen, gray, "MIL", milBtnOn, milBtnOff, Button.State.OFF, Button.Type.STICKY)
#buttonList.append(milBtn)
#infoBtn = Button(dsp.lcd, 225, 438, 100, 40, dsp.btnFont, medBlue, gray, "INFO", infoOn, infoOff, Button.State.OFF, Button.Type.STICKY)
#buttonList.append(infoBtn)
#bigBtn = Button(dsp.lcd, 335, 438, 100, 40, dsp.btnFont, dataColor, gray, "BIG", bigOn, bigOff, Button.State.OFF, Button.Type.STICKY)
#buttonList.append(bigBtn)
#exitBtn = Button(dsp.lcd, 695, 438, 100, 40, dsp.btnFont, medRed, gray, "EXIT", exitSystem, None, Button.State.OFF, Button.Type.MOMENTARY)
#buttonList.append(exitBtn)
##offBtn = Button(dsp.lcd, 695, 429, 100, 50, dsp.btnFont, medRed, gray, "OFF", powerOff, None, Button.State.OFF, Button.Type.MOMENTARY)
##buttonList.append(offBtn)
#plusBtn = Button(dsp.lcd, 545, 438, 40, 40, dsp.btnRadarFont, darkGreen, white, "+", zoomBtnOut, None, Button.State.HIDDEN, Button.Type.MOMENTARY)
#buttonList.append(plusBtn)
#minusBtn = Button(dsp.lcd, 605, 438, 40, 40, dsp.btnRadarFont, darkGreen, white, "-", zoomBtnIn, None, Button.State.HIDDEN, Button.Type.MOMENTARY)
#buttonList.append(minusBtn)
##historyBtn = Button(dsp.lcd, 5, 40, 100, 50, dsp.btnFont, green, white, "LIST", historyOn, None, Button.State.HIDDEN, Button.Type.MOMENTARY)
##buttonList.append(historyBtn)




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
                hitData = loadHitData(hit)
                hits = updateHitList(hits, hitData)
                dsp.displayHitList(hits)

            if (gotHit and not sqFlag):
                gotHit = False

    for event in pygame.event.get():
        if (event.type == pygame.FINGERUP or event.type == pygame.MOUSEBUTTONUP):
            for btn in buttonList:                
                if (btn.isSelected() and (not (btn.isDisabled() or btn.isHidden()))):
                    if (btn.getType() == Button.Type.STICKY):
                        btn.toggleButton()

                    if (btn.getType() == Button.Type.MOMENTARY):
                        btn.pushButton()

    dsp.refreshDisplay()

