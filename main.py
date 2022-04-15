import operator
import time
import signal
import sys
from display import Display
from serialport import SerialPort
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
    Util.setCurrentDir('/home/pi/')
    serialPortName="/dev/ttyS0"
else:
    serialPortName="COM4"

dsp = Display(winFlag)
dsp.setupDisplay()
dsp.drawDataLEDs()
dsp.refreshDisplay()

sp = SerialPort(serialPortName)

hits=[]
gotHit = False

while True:
    sp.pollScanner()
    rawHit = sp.getScannerResponse()
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

    dsp.refreshDisplay()

