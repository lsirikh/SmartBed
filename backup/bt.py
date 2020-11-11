import time

import bluetooth
import threading
import json

from diskio import FileProcess


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

class BTReceive(threading.Thread):
    """

    """
    threadStatus = False

    server_sock = None
    client_sock = None
    address = None
    port = None

    op_code = None

    def pair(self):
        file = FileProcess()
        str = file.networkFileRead()
        json_data = json.loads(str)

        self.address = json_data['bluetooth']
        self.port = 1

    def setThreadOn(self):
        self.threadStatus = True

    def init(self):
        """

        """

        if self.server_sock is None:
            self.pair()
            self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

            self.server_sock.bind(("", self.port))
            self.server_sock.listen(1)
            print("test1")

        if self.client_sock is None:
            print("Try to connect to " + str(self.address))
            self.client_sock, self.address = self.server_sock.accept()
            print("Accepted : ", self.address)

    def run(self):

        try:
            while self.threadStatus:
                # Waiting for data from Android until received
                # unlimited wait
                self.init()

                data = self.client_sock.recv(1024)
                data = data.decode('utf-8')
                data = str(data).replace("\n", "")
                data = data.replace("\r", "")
                print("received [%s]" % data)
                if data == 'start' or data == 'end':
                    self.op_code = data
                    self.sendMessageTo("Success!!")
                elif data == 'break':
                    self.op_code = data
                    self.sendMessageTo("Finish!!")

                #self.control()
                self.msgConvert(data)

        except Exception as ex:
            print("Bluetooth thread was finished : ", ex)
            self.closeSock()
            pass


    def msgConvert(self, data):
        """
        This method will convert str msg to json type
        to discriminate what it means
        :arg: data - bt data
        :return:
        """

        pass

    def sendMessageTo(self, str):
        #sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        #sock.connect((self.address, self.port))
        self.client_sock.send(str)
        #sock.close()

    def closeSock(self):
        """

        :return:
        """
        self.client_sock.close()
        self.server_sock.close()
        self.server_sock = None
        self.client_sock = None

    def finish(self):
        self.closeSock()
        self.threadStatus = False
        time.sleep(0.5)





