import serial
import operator
import time
import signal
import sys
from display import Display
from util import Util


def getSquelchFlag(rawData):
    d = rawData.split(',')
    if (d[8] == "0"):
        return False
    else:
        return True

def loadHitData(rawData):
    p = {}
    d = rawData.split(',')
    p['count'] = 0
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


winFlag = Util.isWindows()
if (not winFlag):
    signal.signal(signal.SIGTERM, shutdownEvent)
    signal.signal(signal.SIGINT, shutdownEvent)
    signal.signal(signal.SIGTSTP, shutdownEvent)
    Util.setCurrentDir('/home/pi/adsb-remote')

dsp = Display(winFlag)
dsp.setupDisplay()
dsp.drawDataLEDs()
dsp.refreshDisplay()

hits=[]
nullHit = "GLG,,,,,,,,,,,,"
gotHit = False

ser = serial.Serial(port='COM4', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0.1)

while True:
    ser.write(b'GLG\r')
    rawHit = ser.readline().decode('utf-8')

    dsp.flipDataLEDs()

    hit = ''.join(rawHit.splitlines())

    if (hit != nullHit):
        d = hit.split(',')
        sqFlag = getSquelchFlag(hit)

        if (not gotHit and sqFlag):
            gotHit = True
            hitData = loadHitData(hit)
            hits = updateHitList(hits, hitData)
            dsp.displayHitList(hits)
        
        if (gotHit and not sqFlag):
            gotHit = False

    dsp.refreshDisplay()

