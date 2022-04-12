import os
from datetime import datetime
import platform

class Util:

    @staticmethod
    def isWindows():
        if (platform.system() == 'Windows'):
            return True
        else:
            return False

    @staticmethod
    def shutdownSystem():
        sd = os.popen('sudo shutdown -h now').readline()
        return
        
    @staticmethod
    def setCurrentDir(dirpath):
        os.chdir(dirpath)
