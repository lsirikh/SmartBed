import requests
import serial, time
import datetime

import threading


from diskio import FileProcess
from procdata import *




prop = {}
prop['duid'] = '8800000000000'
prop['name'] = 'sensorway'
prop['sex'] = 'm'
prop['age'] = '30'
prop['height'] = '176'
prop['weight'] = '78'




class UartRead(threading.Thread):
    threadStatus = False
    file = None
    op_code = None
    ser = None

    def init(self):
        #self.ser = Serial("/dev/ttyAMA1", 115200)  # Open port with baud rate

        self.file = FileProcess()
        self.initSerial()
        self.openSerial()
        self.op_code = 'stop'
        self.uartSet()


    def setAllThreadOn(self):
        self.threadStatus = True


    def initSerial(self):
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


    def uartSet(self):
        if self.op_code == 'start':
            # send data by uart
            op = 's'
            self.ser.write(op.encode())
            time.sleep(0.5)  # give the serial port sometime to receive the data
        elif self.op_code == 'stop':
            # stop data
            op = 'p'
            self.ser.write(op.encode())
            time.sleep(0.5)  # give the serial port sometime to receive the data


    def run(self):
        #self.init()
        count=0
        while self.threadStatus:
            try:
                if self.ser.isOpen():
                    #if self.op_code == 'start':
                    line = self.ser.read()
                    if line != b's':
                        continue
                    line += self.ser.readline()
                    dt = datetime.datetime.now()

                    stf = dt.strftime('%Y-%m-%d %H:%M:%S')
                    prop['collect_time'] = stf
                    dict_data = build_data(line, prop)
                    #print(type(dict_data))
                    #print(dict_data)
                    count = count + 1
                    url = 'http://182.173.185.246:3001/api/Bed/Sensor/SendData/Start'
                    header = {'Content-Type': 'application/json; charset=utf-8'}

                    # async thread
                    res = requests.post(url, headers=header, data=json.dumps(dict_data))

                    # async thread
                    self.file.data_store(dict_data)

                    #set delay

                    print(res)

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
        timestamp = timestamp.timestamp()*1000

    def finish(self):
        self.threadStatus = False
        time.sleep(0.5)