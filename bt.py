import time

import bluetooth
from threading import Thread
import threading
import json

from diskio import FileProcess
from message import RequestData, User, ControlUart, CloudCycleSet


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
class BTReceive():
    """

    """
    def __init__(self):
        self.receiverStatus = False
        self.monitorStatus = False

        self.threadReceive = None
        self.threadMonitor = None

        self.server_sock = None
        self.client_sock = None
        self.address = None
        self.port = None

        self.op_code = None
        self.op_level = None
        self.msg = None

        self.pair()
        self.setAllThreadOn()

    # def init(self):
    #     self.pair()
    #     self.setAllThreadOn()

    def pair(self):
        file = FileProcess()
        str = file.fileRead("", "network.txt")
        json_data = json.loads(str)
        # print(json_data["bluetooth"])
        # print(json_data["wifi-ssid"])
        # print(json_data["wifi-password"])
        # print(json_data["time_server-ip"])
        # print(json_data["time_server-port"])
        # print(json_data["cloud_server-ip"])
        # print(json_data["cloud_server-port"])
        # print(json_data["cloud_server-urls"])

        self.address = json_data['bluetooth']
        self.port = 1

        # str = file.custom_file_read()
        # json_data = json.loads(str)
        # print(json_data["name"])
        # print(json_data["sex"])
        # print(json_data["age"])
        # print(json_data["height"])
        # print(json_data["weight"])
        #
        # str = file.info_file_read()
        # json_data = json.loads(str)
        # print(json_data)

    def connection(self):
        if self.server_sock is None:
            #self.pair()
            self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            print("Server socket was created")

            self.server_sock.bind(("", self.port))
            self.server_sock.listen(1)

        if self.client_sock is None:
            print("Try to connect to " + str(self.address))
            self.client_sock, self.address = self.server_sock.accept()
            print("Accepted : ", self.address)

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
            self.threadReceive = Thread(target=self.receiver)
            self.receiverStatus = True
            self.threadReceive.start()

        except Exception as ex:
            print("Failed to assign or start threadReceive.")

    def monitor(self):

        while self.monitorStatus:
            # print(self.threadReceive.is_alive())
            if self.threadReceive.is_alive() is False:
                print("threadReceive was terminated.")
                print("threadReceive will re-initiate.")
                self.setReceiveThreadOn()

            time.sleep(1)

    def receiver(self):
        self.connection()
        try:
            while self.receiverStatus:
                # Waiting for data from Android until received
                # unlimited wait
                # self.connection()
                data = self.client_sock.recv(1024)
                data = data.decode('utf-8')
                data = str(data).replace("\n", "")
                data = data.replace("\r", "")
                print("received [%s]" % data)

                # self.control()

                self.msgConvert(data)

                time.sleep(1)

        except Exception as ex:
            # Thread will be dead with Exception
            self.closeSock()
            print("Bluetooth was disconnected or aborted- ", ex)

    def msgConvert(self, data):
        """
        This method will convert str msg to json type
        to discriminate what it means
        :arg: data - bt data
        :return:
        """
        try:
            json_str = json.loads(data)
            dict_data = dict(json_str)
            typeMessage = dict_data["TypeMessage"]
            if typeMessage == 1:
                self.msg = RequestData(dict_data)
                print(self.msg)
            elif typeMessage == 2:
                self.msg = User(dict_data)
                print(self.msg)
            elif typeMessage == 3:
                pass
            elif typeMessage == 4:
                pass
            elif typeMessage == 5:
                option_sel = dict_data["CloudServer_Option"]["Option_Sel"]
                #print(cloudServer_option)
                if option_sel == 0:
                    pass
                elif option_sel == 1:
                    pass
                elif option_sel == 2:
                    pass
                elif option_sel == 3:
                    self.msg = CloudCycleSet(dict_data)
                    # self.op_level = self.msg.converter()
                    # self.op_code = "on"


            elif typeMessage == 6:
                pass
            elif typeMessage == 7:
                pass
            elif typeMessage == 8:
                self.msg = ControlUart(dict_data)
                #print(controlUart)
                # if controlUart.operation():
                #     self.op_code = "on"
                #     #self.op_level = "s01"
                # else:
                #     self.op_code = "off"


        except Exception as ex:
            print("Failed to convert data to dict format ", ex)



    def sendMessageTo(self, str):
        # sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        # sock.connect((self.address, self.port))
        self.client_sock.send(str)
        # sock.close()

    def closeSock(self):
        """

        :return:
        """
        self.receiverStatus = False
        self.client_sock.close()
        self.server_sock.close()
        self.server_sock = None
        self.client_sock = None

    def finish(self):
        self.monitorStatus = False
        self.receiverStatus = False
        self.closeSock()
        time.sleep(1)

        try:
            if self.threadReceive.is_alive():
                self.threadReceive.join()
                print("bt threadReceive was successfully finished")

            if self.threadMonitor.is_alive():
                self.threadMonitor.join()
                print("bt threadMonitor was successfully finished")

            return True

        except Exception as ex:
            print("bt Join threads were failed - ", ex)
            return False
