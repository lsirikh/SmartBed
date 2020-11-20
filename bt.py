import time

import bluetooth
from threading import Thread
import json

from diskio import FileProcess
from logs import Logs
from message import RequestData, User, ControlUart, CloudCycleSet, WifiInfo, WifiSetting, WifiIP, WifiAPList, \
    StoredDataList

from monitor import MonitorClass


class BTSetup:
    server_sock = None
    client_sock = None
    address = None

    def __init__(self):
        """

        """
        if self.server_sock is None:
            self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

            port = 1
            self.server_sock.bind(("", port))
            self.server_sock.listen(1)

        if self.client_sock is None:
            self.client_sock, self.address = self.server_sock.accept()
            print("Accepted connection from " + str(self.address))

    def lookUpNearbyBluetoothDevices(self):
        """

        :return:
        """
        nearby_devices = bluetooth.discover_devices()
        for bdaddr in nearby_devices:

            print(str(bluetooth.lookup_name(bdaddr)) + " [" + str(bdaddr) + "]")
            if bluetooth.lookup_name(bdaddr) == "Galaxy Note8":
                return bdaddr

    def closeSock(self):
        """

        :return:
        """

        self.client_sock.close()
        self.server_sock.close()


# class BTReceive(threading.Thread):
class BTReceive(MonitorClass):
#class BTReceive():
    def __init__(self):

        super().setBTStatus(False)
        #print("BTReceive - ", self.getBTStatus())
        # self.mClass = MonitorClass()
        # self.mClass.setBTStatus(False)

        self.receiverStatus = False
        self.monitorStatus = False

        self.threadReceive = None
        self.threadMonitor = None

        self.server_sock = None
        self.client_sock = None
        self.address = None
        self.port = None

        self.msg = None

        # Log Object
        self.log = Logs(self.__class__.__name__)
        self.log.write(self.log.INFO, self.__init__.__name__, "initiated.")

        self.file = FileProcess()

    def initialize(self):
        self.setBTStatus(True)
        self.pair()
        self.setAllThreadOn()


    def pair(self):
        self.log.write(self.log.INFO, self.pair.__name__, "Called.")
        str_data = self.file.fileRead("", "network.txt")
        json_data = json.loads(str_data)

        self.log.write(self.log.INFO, self.pair.__name__, "Loaded - BT ADDRESS : {0}".format(json_data['bluetooth']))
        self.address = json_data['bluetooth']
        self.port = 1

    def connection(self):
        self.log.write(self.log.INFO, self.connection.__name__, "Called.")
        try:
            if self.server_sock is not None:
                self.server_sock.close()

            self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.log.write(self.log.NOTICE, self.connection.__name__, "Server socket was created")
            print("Server socket was created")

            self.server_sock.bind(("", self.port))
            self.server_sock.listen(1)
            self.server_sock.settimeout(3)
        except Exception as ex:
            self.log.write(self.log.ERROR, self.connection.__name__, "Failed to execute : {0}".format(ex))
            print("Failed to open or bind server socket", ex)

        try:
            if self.client_sock is not None:
                self.client_sock.close()

            print("Try to connect to " + str(self.address))
            self.log.write(self.log.NOTICE, self.connection.__name__, "Try to connect to {0}".format(str(self.address)))

            self.client_sock, self.address = self.server_sock.accept()
            print("Accepted : ", self.address)
        except Exception as ex:
            self.log.write(self.log.ERROR, self.connection.__name__, "Failed to execute : {0}".format(ex))
            print("Failed to open or bind client_sock", ex)

    def setAllThreadOn(self):
        self.log.write(self.log.INFO, self.setAllThreadOn.__name__, "Called.")
        try:
            # Temporally Set Ready Baseline at this point
            self.setBTStatus(True)

            self.threadReceive = Thread(target=self.receiver)
            self.threadMonitor = Thread(target=self.monitor)
            self.threadReceive.daemon = False
            self.threadMonitor.daemon = False
            self.receiverStatus = True
            self.monitorStatus = True


            self.threadReceive.start()
            self.threadMonitor.start()

        except Exception as ex:
            self.log.write(self.log.ERROR, self.setAllThreadOn.__name__, "Failed to execute : {0}".format(ex))
            print("Failed to assign or start threadReceive, threadMonitor.")

    def bluetoothReConnect(self):
        self.log.write(self.log.INFO, self.bluetoothReConnect.__name__, "Called.")
        try:
            result = self.closeSock()
            if result:
                print("Bluetooth sockets were successfully closed.")
            self.connection()

        except Exception as ex:
            self.log.write(self.log.ERROR, self.bluetoothReConnect.__name__, "Failed to execute : {0}".format(ex))
            print("Failed to re-initiate Bluetooth sockets for reconnection. ", ex)

    def setReceiveThreadOn(self):
        self.log.write(self.log.INFO, self.setReceiveThreadOn.__name__, "Called.")
        try:
            self.threadReceive = Thread(target=self.receiver)
            self.threadReceive.daemon = False
            self.receiverStatus = True
            self.setBTStatus(True)
            self.threadReceive.start()

        except Exception as ex:
            self.log.write(self.log.ERROR, self.setReceiveThreadOn.__name__, "Failed to execute : {0}".format(ex))
            print("Failed to assign or start threadReceive.")

    def monitor(self):
        self.log.write(self.log.INFO, self.monitor.__name__, "Called.")
        count =0
        while self.monitorStatus:
            # print(self.threadReceive.is_alive())
            if count > 10:
                if self.threadReceive.is_alive() is True:
                    self.threadReceive.join()
                    print("bt thread was stopped.")

            if self.threadReceive.is_alive() is False:
                self.setBTStatus(False)
                self.log.write(self.log.NOTICE, self.monitor.__name__, "threadReceive was terminated and will re-initiate.")
                print("threadReceive was terminated.")
                print("threadReceive will re-initiate.")
                self.setReceiveThreadOn()

            time.sleep(1)

    def receiver(self):
        self.log.write(self.log.INFO, self.receiver.__name__, "Called.")
        #super().setWifiStatus(True)
        self.connection()
        try:
            while self.receiverStatus:
                # Waiting for data from Android until received
                # unlimited wait
                data = self.client_sock.recv(1024)
                data = data.decode('utf-8')
                data = str(data).replace("\n", "")
                data = data.replace("\r", "")
                print("received [%s]" % data)

                self.msgConvert(data)

                time.sleep(1)

        except Exception as ex:
            # Thread will be dead with Exception
            self.closeSock()
            self.log.write(self.log.ERROR, self.receiver.__name__, "Failed to execute : {0}".format(ex))
            print("Bluetooth was disconnected or aborted- ", ex)

    def msgConvert(self, data):
        """
        This method will convert str msg to json type
        to discriminate what it means
        :arg: data - bt data
        :return:
        """
        self.log.write(self.log.INFO, self.msgConvert.__name__, "Called.")
        try:
            json_str = json.loads(data)
            dict_data = dict(json_str)
            typeMessage = dict_data["TypeMessage"]
            if typeMessage == 1:
                self.msg = RequestData(dict_data)
                # print(self.msg)
            elif typeMessage == 2:
                self.msg = User(dict_data)
            elif typeMessage == 3:
                pass
            elif typeMessage == 4:
                option_sel = dict_data["Wifi_Option"]["Option_Sel"]
                if option_sel == 0:
                    self.msg = WifiInfo(dict_data)
                    # print(self.msg )
                elif option_sel == 1:
                    self.msg = WifiSetting(dict_data)
                elif option_sel == 2:
                    self.msg = WifiIP(dict_data)
                elif option_sel == 3:
                    self.msg = WifiAPList(dict_data)

            elif typeMessage == 5:
                option_sel = dict_data["CloudServer_Option"]["Option_Sel"]
                # print(cloudServer_option)
                if option_sel == 0:
                    pass
                elif option_sel == 1:
                    self.msg = CloudCycleSet(dict_data)
                elif option_sel == 2:
                    pass
                elif option_sel == 3:
                    self.msg = CloudCycleSet(dict_data)

            elif typeMessage == 6:
                option_sel = dict_data["StoredFiles_Option"]["Option_Sel"]
                if option_sel == 0:
                    self.msg=StoredDataList(dict_data)
            elif typeMessage == 7:
                pass
            elif typeMessage == 8:
                self.msg = ControlUart(dict_data)


        except Exception as ex:
            self.log.write(self.log.ERROR, self.msgConvert.__name__, "Failed to execute : {0}".format(ex))
            print("Failed to convert data to dict format ", ex)

    def sendMessageTo(self, str):
        """

        :param str:
        :return:
        """
        self.log.write(self.log.INFO, self.sendMessageTo.__name__, "Called.")
        try:
            self.client_sock.send(str)
        except Exception as ex:
            self.log.write(self.log.ERROR, self.sendMessageTo.__name__, "Failed to execute : {0}".format(ex))
            print("Failed to send a message to BT module.")

    def closeSock(self):
        """

        :return:
        """
        self.log.write(self.log.INFO, self.closeSock.__name__, "Called.")
        try:
            self.client_sock.close()
            self.server_sock.close()
            self.server_sock = None
            self.client_sock = None

            return True
        except Exception as ex:
            self.log.write(self.log.ERROR, self.closeSock.__name__, "Failed to execute : {0}".format(ex))
            print("Failed to close bluetooth sockets. ", ex)
            return False

    def finish(self):
        self.log.write(self.log.INFO, self.finish.__name__, "Called.")
        self.monitorStatus = False
        self.receiverStatus = False
        result = self.closeSock()

        self.setBTStatus(False)
        if result:
            self.log.write(self.log.NOTICE, self.finish.__name__, "Bluetooth sockets were successfully closed.")
            print("Bluetooth sockets were successfully closed.")
        time.sleep(1)

        try:
            if self.threadReceive.is_alive():
                self.threadReceive.join()
                self.log.write(self.log.NOTICE, self.finish.__name__, "Bluetooth threadReceive was successfully finished")
                print("Bluetooth threadReceive was successfully finished")

            if self.threadMonitor.is_alive():
                self.threadMonitor.join()
                self.log.write(self.log.NOTICE, self.finish.__name__, "Bluetooth threadMonitor was successfully finished")
                print("Bluetooth threadMonitor was successfully finished")

            return True

        except Exception as ex:
            self.log.write(self.log.ERROR, self.finish.__name__, "Failed to execute : {0}".format(ex))
            print("bt Join threads were failed - ", ex)
            return False
