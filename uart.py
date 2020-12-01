import requests
import serial, time
import datetime
import json

from threading import Thread
import threading

from api import ApiServer
from diskio import FileProcess
from logs import Logs
from message import ApiSendData

import inspect

from monitor import MonitorClass

SPEED00 = 'p'  # stop

SPEED01 = 's01'  # 100ms
SPEED02 = 's02'  # 200ms
SPEED03 = 's03'  # 300ms
SPEED04 = 's04'  # 400ms
SPEED05 = 's05'  # 500ms
SPEED06 = 's06'  # 600ms
SPEED07 = 's07'  # 700ms
SPEED08 = 's08'  # 800ms
SPEED09 = 's09'  # 900ms
SPEED10 = 's10'  # 1000ms

DEVICE_PORT = "/dev/ttyAMA1" # set device serial port


class UartRead(MonitorClass):

    def __init__(self):
        super().setUartStatus(False)
        #print("UartRead - ", self.getUartStatus())
        # status variable to control thread
        self.receiverStatus = False
        self.monitorStatus = False

        # Thread object
        self.threadReceive = None
        self.threadMonitor = None

        # Serial object
        self.ser = None

        # File Control Object
        self.file = FileProcess()
        # Api Server Object
        self.api = ApiServer()
        # Log Object
        self.log = Logs(self.__class__.__name__)
        self.log.write(self.log.INFO, self.__init__.__name__, "initiated.")

        # operation variable
        self.op_code = 'off'

        # info variable
        self.prop = {}

    def initialize(self):
        self.loadFiles()
        self.initSerial()
        self.openSerial()
        self.uartSet(SPEED00)
        self.setAllThreadOn()

    def loadFiles(self):
        self.log.write(self.log.INFO, self.loadFiles.__name__, "Called.")

        str = self.file.fileRead("", "user.txt")
        json_data = json.loads(str)
        dict_info = dict(json_data)

        str = self.file.fileRead("", "bed.txt")
        json_data = json.loads(str)
        dict_bed = dict(json_data)
        # dict data merge
        dict_bed.update(dict_info)
        self.prop = dict_bed

    def initSerial(self):
        self.log.write(self.log.INFO, self.initSerial.__name__, "Called.")
        if self.ser is not None:
            self.log.write(self.log.WARNING, self.initSerial.__name__, "Uart Serial Object was not null.")
            self.ser.close()

        self.ser = serial.Serial()
        self.ser.port = DEVICE_PORT
        self.ser.baudrate = 115200
        self.ser.bytesize = serial.EIGHTBITS  # number of bits per bytes
        self.ser.parity = serial.PARITY_NONE  # set parity check: no parity
        self.ser.stopbits = serial.STOPBITS_ONE  # number of stop bits
        # ser.timeout = None          #block read
        self.ser.timeout = 1  # non-block read
        # ser.timeout = 2              #timeout block read
        self.ser.xonxoff = False  # disable software flow control
        self.ser.rtscts = False  # disable hardware (RTS/CTS) flow control
        self.ser.dsrdtr = False  # disable hardware (DSR/DTR) flow control
        self.ser.writeTimeout = 2  # timeout for write

    def openSerial(self):
        try:
            self.log.write(self.log.INFO, self.openSerial.__name__, "Try to open port....")
            self.ser.open()

            # At this line, It was regarded as uart communication is ready
            self.setUartStatus(True)

        except Exception as ex:
            self.log.write(self.log.ERROR, self.openSerial.__name__, "Failed to execute : {0}".format(ex))
            #print("error open serial port: " + str(e))
            exit()

    def uartSet(self, level):
        self.log.write(self.log.INFO, self.uartSet.__name__, "Called.")
        if level is None:
            level = SPEED01
        try:
            if level == SPEED00:
                for i in range(3):
                    # stop data
                    op = 'p'
                    self.ser.write(op.encode())
                    time.sleep(0.2)  # give the serial port sometime to receive the data
            else:
                for i in range(3):
                    # Set operation mode and level
                    op = level
                    # send data by uart
                    self.ser.write(op.encode())
                    time.sleep(0.2)  # give the serial port sometime to receive the data


            return True

        except Exception as ex:
            self.log.write(self.log.ERROR, self.uartSet.__name__, "Failed to execute : {0}".format(ex))
            #print("Failed to execute uartSet function in UartRead")
            return False

    def setAllThreadOn(self):
        self.log.write(self.log.INFO, self.setAllThreadOn.__name__, "Called.")
        try:
            self.threadReceive = Thread(target=self.receiver)
            self.threadMonitor = Thread(target=self.monitor)
            self.threadReceive.daemon = True
            self.threadMonitor.daemon = True
            self.receiverStatus = True
            self.monitorStatus = True
            self.threadReceive.start()
            self.threadMonitor.start()

        except Exception as ex:
            self.log.write(self.log.ERROR, self.setAllThreadOn.__name__, "Failed to execute : {0}".format(ex))
            #print("Failed to assign or start threadReceive, threadMonitor.")

    def setReceiveThreadOn(self):
        self.log.write(self.log.INFO, self.setReceiveThreadOn.__name__, "Called.")
        try:
            self.initSerial()
            self.openSerial()
            self.uartSet(SPEED00)
            self.threadReceive = Thread(target=self.receiver)
            self.threadReceive.daemon = True
            self.receiverStatus = True
            self.threadReceive.start()

        except Exception as ex:
            self.log.write(self.log.ERROR, self.setReceiveThreadOn.__name__, "Failed to execute : {0}".format(ex))
            #print("Failed to assign or start threadReceive.")

    def monitor(self):
        self.log.write(self.log.INFO, self.monitor.__name__, "Called.")
        while self.monitorStatus:
            try:

                if self.threadReceive.is_alive() is False:
                    self.setUartStatus(False)
                    self.setReceiveThreadOn()
                    self.log.write(self.log.NOTICE, self.monitor.__name__, "threadReceive was terminated and "
                                                                           "re-initiated.")

                time.sleep(1)
            except Exception as ex:
                self.log.write(self.log.WARNING, self.monitor.__name__, "Failed to execute : {0}".format(ex))


    def receiver(self):
        self.log.write(self.log.INFO, self.receiver.__name__, "Called.")
        while self.receiverStatus:
            try:
                if self.ser.isOpen():
                    # if self.op_code == 'start':
                    line = self.ser.read()
                    if line != b's':
                        continue
                    line += self.ser.readline()
                    dt = datetime.datetime.now()

                    stf = dt.strftime('%Y-%m-%d %H:%M:%S')
                    self.prop['collect_time'] = stf
                    dict_data = ApiSendData(line, self.prop)

                    res = self.api.dataSend(dict_data.__dict__)
                    print(stf, res)
                    self.log.write(self.log.INFO, self.receiver.__name__, res)

                    # async thread
                    # res = requests.post(url, headers=header, data=json.dumps(dict_data))

                    # async thread
                    #self.file.data_store(dict_data)

            except Exception as ex:
                print(ex)
                break

    def timeStamp(self):
        """

        :return:
        """
        self.log.write(self.log.INFO, self.timeStamp.__name__, "Called.")
        dt = datetime.datetime.now()
        stamp = dt.strftime('%Y-%m-%d %H:%M:%S,%f')



    def closeSerial(self):
        """

        :return:
        """
        self.log.write(self.log.INFO, self.closeSerial.__name__, "Called.")
        try:
            self.ser.close()
        except Exception as ex:
            self.log.write(self.log.ERROR, self.closeSerial.__name__, "Failed to execute : {0}".format(ex))

    def finish(self):

        self.log.write(self.log.INFO, self.finish.__name__, "Called.")
        self.monitorStatus = False
        self.receiverStatus = False
        self.closeSerial()
        time.sleep(1)

        try:
            if self.threadReceive.is_alive():
                self.threadReceive.join()
                self.log.write(self.log.NOTICE, self.finish.__name__, "uart threadReceive was successfully finished.")
                #print("uart threadReceive was successfully finished")

            if self.threadMonitor.is_alive():
                self.threadMonitor.join()
                self.log.write(self.log.NOTICE, self.finish.__name__, "uart threadMonitor was successfully finished.")
                #print("uart threadMonitor was successfully finished")

            return True

        except Exception as ex:
            self.log.write(self.log.NOTICE, self.finish.__name__, "Failed to execute : {0}".format(ex))
            #print("uart Join threads were failed - ", ex)
            return False
