import serial
import operator
import time


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


hits=[]
nullHit = "GLG,,,,,,,,,,,,"
gotHit = False

ser = serial.Serial(port='COM4', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0.1)

while True:
    ser.write(b'GLG\r')
    rawHit = ser.readline().decode('utf-8')
    hit = ''.join(rawHit.splitlines())

    if (hit != nullHit):
        d = hit.split(',')
        sqFlag = getSquelchFlag(hit)

        if (not gotHit and sqFlag):
            gotHit = True
            hitData = loadHitData(hit)
            hits = updateHitList(hits, hitData)
            for i in hits:
                print(f'{i["timestamp"]} {str(i["count"])} {i["freq"]} {i["channel"]}')
            print("")
        
        if (gotHit and not sqFlag):
            gotHit = False


