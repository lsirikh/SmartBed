import requests
import serial, time
import datetime
import json

from threading import Thread
import threading

from api import ApiServer
from diskio import FileProcess
from message import ApiSendData

# prop = {}
# prop['duid'] = '8800000000000'
# prop['name'] = 'sensorway'
# prop['sex'] = 'm'
# prop['age'] = '30'
# prop['height'] = '176'
# prop['weight'] = '78'

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


class UartRead():

    def __init__(self):
        # status variable to control thread
        self.receiverStatus = False
        self.monitorStatus = False

        # Thread object
        self.threadReceive = None
        self.threadMonitor = None

        # Serial object
        self.ser = None

        # File Control object
        self.file = FileProcess()
        # Api Server Object
        self.api = ApiServer()

        # operation variable
        self.op_code = 'off'

        # info variable
        self.prop = {}

        self.loadFiles()
        self.initSerial()
        self.openSerial()
        self.uartSet(SPEED00)
        self.setAllThreadOn()

    def loadFiles(self):
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
        if self.ser is not None:
            self.ser.close()

        self.ser = serial.Serial()
        # ser.port = "/dev/ttyUSB0"
        # ser.port = "/dev/ttyS2"
        self.ser.port = "/dev/ttyAMA1"
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
            self.ser.open()
        except Exception as e:
            print("error open serial port: " + str(e))
            exit()

    def uartSet(self, level):
        if level is None:
            level = SPEED01
        try:
            if level == SPEED00:
                for i in range(3):
                    # stop data
                    op = 'p'
                    r = self.ser.write(op.encode())
                    time.sleep(0.2)  # give the serial port sometime to receive the data
            else:
                for i in range(3):
                    # Set operation mode and level
                    op = level
                    # send data by uart
                    self.ser.write(op.encode())
                    time.sleep(0.2)  # give the serial port sometime to receive the data


            # if self.op_code == 'on':
            #     for i in range(3):
            #         # Set operation mode and level
            #         op = level
            #         # send data by uart
            #         self.ser.write(op.encode())
            #         time.sleep(0.2)  # give the serial port sometime to receive the data
            #
            # elif self.op_code == 'off':
            #     for i in range(3):
            #         # stop data
            #         op = 'p'
            #         r = self.ser.write(op.encode())
            #         time.sleep(0.2)  # give the serial port sometime to receive the data
            return True

        except Exception as ex:
            print("Failed to execute uartSet function in UartRead")
            return False

    def setAllThreadOn(self):
        try:
            self.threadReceive = Thread(target=self.receiver)
            self.threadMonitor = Thread(target=self.monitor)
            self.receiverStatus = True
            self.monitorStatus = True
            self.threadReceive.start()
            self.threadMonitor.start()

        except Exception as ex:
            print("Failed to assign or start threadReceive, threadMonitor.")

    def setReceiveThreadOn(self):
        try:
            self.initSerial()
            self.openSerial()
            self.uartSet(SPEED00)
            self.threadReceive = Thread(target=self.receiver)
            self.receiverStatus = True
            self.threadReceive.start()

        except Exception as ex:
            print("Failed to assign or start threadReceive.")

    def monitor(self):

        while self.monitorStatus:
            if self.threadReceive.is_alive() is False:
                print("threadReceive was terminated.")
                print("threadReceive will re-initiate.")
                self.setReceiveThreadOn()

            time.sleep(1)

    def receiver(self):
        # self.init()
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
                    #dict_data = build_data(line, self.prop)
                    dict_data = ApiSendData(line, self.prop)

                    res = self.api.dataSend(dict_data.__dict__)
                    print(res)
                    # url = 'http://182.173.185.246:3001/api/Bed/Sensor/SendData/Start'
                    # header = {'Content-Type': 'application/json; charset=utf-8'}
                    #
                    # # async thread
                    # res = requests.post(url, headers=header, data=json.dumps(dict_data))

                    # async thread
                    #self.file.data_store(dict_data)

                    # set delay
                    # print(res)

                    # time.sleep(0.08)

            except Exception as ex:
                print(ex)
                break

    def timestamp(self):
        """

        :return:
        """
        dt = datetime.datetime.now()
        stamp = dt.strftime('%Y-%m-%d %H:%M:%S,%f')
        timestamp = datetime.datetime.strptime(stamp, '%Y-%m-%d %H:%M:%S,%f')
        timestamp = timestamp.timestamp() * 1000

    def closeSerial(self):
        """

        :return:
        """
        self.ser.close()

    def finish(self):
        self.monitorStatus = False
        self.receiverStatus = False
        self.closeSerial()
        time.sleep(1)

        try:
            if self.threadReceive.is_alive():
                self.threadReceive.join()
                print("uart threadReceive was successfully finished")

            if self.threadMonitor.is_alive():
                self.threadMonitor.join()
                print("uart threadMonitor was successfully finished")

            return True

        except Exception as ex:
            print("uart Join threads were failed - ", ex)
            return False
