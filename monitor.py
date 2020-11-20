

class MonitorClass:
    btStatus=""
    wifiStatus=""
    uartStatus=""

    # def __init__(self):
    #
    #     self.btStatus = False
    #     self.wifiStatus = False
    #     self.uartStatus = False

    def setWifiStatus(self, flag):
        if flag:
            self.wifiStatus = True
        else:
            self.wifiStatus = False

    def getWifiStatus(self):
        return self.wifiStatus

    def setBTStatus(self, flag):
        if flag:
            self.btStatus = True
        else:
            self.btStatus = False

    def getBTStatus(self):
        return self.btStatus

    def setUartStatus(self, flag):
        if flag:
            self.uartStatus = True
        else:
            self.uartStatus = False

    def getUartStatus(self):
        return self.uartStatus

