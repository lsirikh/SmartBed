import itertools
import subprocess
import sys
import multiprocessing

from bt import Bluetooth

from uart import *
from wifi_network import WifiNT
from monitor import MonitorClass


class SmartBed:

    def __init__(self):

        # MonitorClass init
        self.monitor = MonitorClass()

        #multiprocess
        self.func_list = [
            'initBT',
            'initUart',
            'initWifi',
            'loadExp',
            'loading'
        ]
        self.pool = None

        #FileProcess class was created
        self.statusFile = None
        #self.uartThread = None
        self.file = FileProcess()

        #UartData class was created
        self.statusUart = None
        self.threadUart = None
        self.mProcessUart = False
        self.uart = None

        #Logs class was created
        self.logStatus = None
        #self.uartThread = None
        self.log = Logs(self.__class__.__name__)

        #BTReceive class was created
        self.statusBT = None
        self.threadBT = None
        self.mProcessBT = False
        self.bt = None

        #WifiNT class was created
        self.statusWifi = None
        self.threadWifi = None
        self.mProcessWifi = False
        self.wifi = None

        # loadingExp function
        self.statusLoadingExp = None
        self.threadLoadingExp = None

        # workflow
        self.statusWorkflow = None
        self.threadWorkflow = None


        # statusIndex
        self.statusIdex = 0


    # def funcMap(self, funcName):
    #     if funcName == "initWifi":
    #         self.mProcessWifi=self.initWifi()
    #     elif funcName == "initBT":
    #         self.mProcessBT=self.initBT()
    #     elif funcName == "initUart":
    #         self.mProcessUart=self.initUart()
    #     elif funcName == "loadExp":
    #         self.loadExp()
    #     elif funcName == "loading":
    #         self.loading()

    def initWifi(self):
        self.log.write(self.log.INFO, self.initWifi.__name__, "Called.")
        try:
            self.wifi = WifiNT()
            self.wifi.initialize()
        except Exception as ex:
            self.log.write(self.log.ERROR, self.initWifi.__name__, "Failed to execute : {0}".format(ex))

    def initBT(self):
        self.log.write(self.log.INFO, self.initBT.__name__, "Called.")
        try:
            self.bt = Bluetooth()
            self.bt.initialize()
        except Exception as ex:
            self.log.write(self.log.ERROR, self.initBT.__name__, "Failed to execute : {0}".format(ex))

    def initUart(self):
        self.log.write(self.log.INFO, self.initUart.__name__, "Called.")
        try:
            self.uart = UartRead()
            self.uart.initialize()
        except Exception as ex:
            self.log.write(self.log.ERROR, self.initUart.__name__, "Failed to execute : {0}".format(ex))

    # def setMultiprocess(self):
    #     try:
    #         self.pool = multiprocessing.Pool(processes=2)
    #         self.pool.map(self.funcMap, self.func_list)
    #         #pool.map(self.count, self.func_list)
    #     except Exception as ex:
    #         print(ex)

    def setAllThreadOn(self):
        self.log.write(self.log.INFO, self.setAllThreadOn.__name__, "Called.")
        try:
            #Set thread environment
            self.threadUart = Thread(target=self.initUart)
            self.threadUart.daemon = False
            self.statusUart = True

            self.threadBT = Thread(target=self.initBT)
            self.threadBT.daemon = False
            self.statusBT = True

            self.threadWifi = Thread(target=self.initWifi)
            self.threadWifi.daemon = False
            self.statusWifi = True

            self.threadWorkflow = Thread(target=self.workFlow)
            self.threadWifi.daemon = False
            self.statusWorkflow = True

            self.threadLoadingExp = Thread(target=self.loadExp)
            self.threadLoadingExp.daemon = False
            self.statusLoadingExp = True

            #Start threads
            self.threadBT.start()
            self.threadUart.start()
            self.threadWifi.start()
            self.threadLoadingExp.start()

        except Exception as ex:
            print(ex)
            self.log.write(self.log.ERROR, self.setAllThreadOn.__name__, "Failed to execute : {0}".format(ex))

    def close(self):

        #uartWrite.finish()
        if self.bt.finish() and self.uart.finish():
            print("all threads were finished.")
            sys.exit()

    def mutex(self):
        filename = sys.argv[0].split('/')[-1].split('.')[0]
        print(self.getSubpro("ps aux | grep {0}".format(filename), 3)['output'])
        print(self.getSubpro("ps aux | grep "+filename+" |awk '{print $2}'" , 3)['output'])

    def getSubpro(self, command, timeout=None):
        """
        This method is the prime role in this class.
        Wifi Connection modules are not suitable for this project
        This subprocess method was used to send command data to bash cmd line
        to execute wifi connection order.
        :param timeout:
        :param command:
        :return:
        """
        self.log.write(self.log.INFO, self.getSubpro.__name__, "Called.")
        dict_output = dict()
        try:
            obj = subprocess.Popen(command,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   shell=True
                                   )

            output, err = obj.communicate()
            obj.wait(timeout)

            dict_output['output'] = output.decode('UTF-8')
            dict_output['err'] = err
            return dict_output

        except Exception as ex:
            self.log.write(self.log.ERROR, self.getSubpro.__name__, "Failed to execute : {0}".format(ex))
            #print(ex)
            return None

    def workFlow(self):
        # Main thread
        while self.statusWorkflow:
            try:
                # local variable will be initialized
                typeMessage = None

                # Check msg is None or not
                if self.bt.msg is not None:
                    typeMessage = self.bt.msg.typeMessage

                result = False

                # Each action will be taken
                if typeMessage == 1:
                    obj = self.bt.msg
                    load_str = self.file.fileRead("","bed.txt")
                    json_data = json.loads(load_str)
                    #print("json_data : ",json_data)
                    #print("obj : ",obj)
                    inter_result = obj.checkBedNum(json_data['duid'])
                    #print("inter result : ", inter_result)
                    if inter_result:
                        dict_data = obj.setRequest()

                        # inter_result will be used
                        # uart to api send re-init function need!!!!!
                        # -------------------------------------
                        result = True

                        result = self.file.fileWrite("", "request.txt", dict_data)
                        self.bt.sendMessageTo(str(obj.response(result)))

                elif typeMessage == 2:
                    obj = self.bt.msg
                    result = self.file.fileWrite("", "user.txt", obj.getData())
                    self.bt.sendMessageTo(str(obj.response(result)))
                    self.uart.loadFiles()
                    # if getConSSID() == "":
                    #     print("disconnected")
                elif typeMessage == 3:
                    pass
                elif typeMessage == 4:
                    obj = self.bt.msg
                    # wifi get ssid
                    if obj.option_sel == 0:
                        load_str = self.file.fileRead("","network.txt")
                        json_data = json.loads(load_str)
                        data = obj.response(json_data['wifi-ssid'])
                        self.bt.sendMessageTo(str(data))
                    # wifi ssid and pw setting
                    elif obj.option_sel == 1:
                        load_str = self.file.fileRead("","network.txt")
                        json_data = json.loads(load_str)
                        dict_data = dict(json_data)
                        proc_data = obj.setWifi(dict_data)
                        result=self.file.fileWrite("", "network.txt", proc_data)
                        data = obj.response(result)

                        # wifi network re-init function need!!!!!
                        # -------------------------------------

                        self.bt.sendMessageTo(str(data))

                        # wifi ssid and pw setting
                    elif obj.option_sel == 2:
                        pass

                    elif obj.option_sel == 3:
                        ap_list=self.wifi.getWifiList()
                        #print(ap_list)
                        result=obj.request()
                        if result:
                            data = obj.response(ap_list)

                        self.bt.sendMessageTo(str(data))

                elif typeMessage == 5:

                    obj = self.bt.msg
                    result = self.uart.uartSet(obj.converter())
                    self.bt.sendMessageTo(str(obj.response(result)))
                elif typeMessage == 6:
                    obj = self.bt.msg

                    if obj.option_sel == 0:
                        data_list = self.file.getDirFiles("/data")
                        result = obj.request()
                        if result:
                            data = obj.response(data_list)

                    self.bt.sendMessageTo(str(data))
                elif typeMessage == 7:
                    pass
                elif typeMessage == 8:
                    # uart receive on/off
                    obj = self.bt.msg
                    if obj.operation():
                        result = self.uart.uartSet(SPEED01)
                    else:
                        result = self.uart.uartSet(SPEED00)
                    self.bt.sendMessageTo(str(obj.response(result)))

                self.bt.msg = None
                #self.uart.op_code = ''

                time.sleep(0.1)
            except Exception as ex:
                #print(ex)
                pass




    def loadExp(self):
        print("Now Program Initiate. Please Wait.")
        self.statusIdex = 0
        flagWifi = False
        flagUart = False
        flagBluetooth = False
        flagComplete = False

        write, flush = sys.stdout.write, sys.stdout.flush
        for char in itertools.cycle('|/-\\'):
            if self.statusIdex < 10:
                try:
                    status = "{0}  loading...({1})        ".format(char, self.bt.bl.state)
                except AttributeError as ex:
                    status = "{0}  loading...({1})        ".format(char, "PREPARING")
                write(status)
                flush()
                write('\x08' * len(status))


            try:
                # print("SmartBed(bt_receiver) : ", self.bt_receiver.getBTStatus())
                # print("SmartBed(uart) : ", self.uart.getUartStatus())
                # print("SmartBed(wifi) : ", self.wifi.getWifiStatus())
                # print("confirmed index : ", self.statusIdex)
                if self.bt.getBTStatus() and not flagBluetooth:
                    flagBluetooth = True
                    print("Now Bluetooth Module is ready!")
                    self.statusIdex += 1

            except Exception as ex:
                #print("SmartBed ex : ",ex)
                pass

            try:
                if self.uart.getUartStatus() and not flagUart:
                    flagUart = True
                    print("Now Uart Module is ready!")
                    self.statusIdex += 1
            except Exception as ex:
                #print("uart ex : ",ex)
                pass


            try:
                if self.wifi.getWifiStatus() and not flagWifi:
                    flagWifi = True
                    print("Now Wifi Module is ready!")
                    self.statusIdex += 1
            except Exception as ex:
                #print("wifi ex : ",ex)
                pass

            try:
                if self.statusIdex == 3 and not flagComplete:
                    flagComplete = True
                    print("Loading was completed.")
                    #self.threadLoadingExp.join(2)

                    #break
            except Exception as ex:
                print("complete ex : ",ex)

            time.sleep(0.1)

        write(' ' * len(status) + '\x08' * len(status))


if __name__ == '__main__':

    smartBed = SmartBed()
    smartBed.setAllThreadOn()
    #smartBed.setMultiprocess()
    #smartBed.loading()
    # smartBed.pool.close()
    # smartBed.pool.join()
    #smartBed.mutex()
    #print("SmartBed was Activated.")
    smartBed.workFlow()

