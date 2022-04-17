import serial

class SerialPort():
        
    def __init__(self, portName):
        self.__serPort = serial.Serial(port=portName, baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0.1)
        self.isScanning = "GLG,,,,,,,,,,,,"

    def pollScanner(self):
        self.__serPort.write(b'GLG\r')

    def getScannerResponse(self):
        resp = self.__serPort.readline().decode('utf-8')
        

s = SerialPort("/dev/ttyS0")

while True:
    s.pollScanner()
    print(s.getScannerResponse())
