import time

import bluetooth
from threading import Thread
import json

from diskio import FileProcess
from logs import Logs
from message import RequestData, User, ControlUart, CloudCycleSet, WifiInfo, WifiSetting, WifiIP, WifiAPList, \
    StoredDataList

from monitor import MonitorClass

import pexpect
import subprocess

import asyncio
import itertools
from enum import Enum

import sys

class StateType(Enum):
    READY = 1 # Device on
    SET_DEFUALT_DEVICE = 2
    SET_PAIRABLE = 3
    SET_DISCOVERABLE = 4
    WAITING_REQUEST = 5
    REQUEST_PAIRING = 6
    PAIRED = 7
    UNPAIRED = 8
    CONNECTED = 9
    DISCONNECTED = 10
    SCANNING = 11
    SERVICE_RESOLVED_YES = 12
    SERVICE_RESOLVED_NO = 13
    REQUEST_PAIRED_DEVICES = 14
    REQUEST_AVAILABLE_DEVICE = 15
    DISCONNECT_DEVICE = 16
    REMOVE_DEVICE = 17

class BluetoothctlAsync:
    def __init__(self):
        self.available_devices = []
        self.paired_devices = []
        self.hearing_cmd = True
        self.reuqest_condition = None
        self.state = StateType.READY.name
        out = subprocess.check_output("rfkill unblock bluetooth", shell = True)
        self.child = pexpect.spawn("bluetoothctl", echo = False, encoding='utf-8')

    async def get_agent_output(self, command, pause=0):
        """Run a command in bluetoothctl prompt, return output as a list of lines."""
        self.child.send(command + "\n")
        await asyncio.sleep(pause)

        start_failed = await self.child.expect(["bluetooth", "agent", pexpect.EOF, pexpect.TIMEOUT], async_=True)
        result = str(self.child.before).split("\r\n")

        if start_failed == 2 or start_failed == 3:
            raise Exception("Bluetoothctl failed after running " + command)

        return result

    async def async_loading(self):
        print("Now Program Initiate. Please Wait.")
        try:
            write, flush = sys.stdout.write, sys.stdout.flush
            for char in itertools.cycle('||//--\\\\'):
                status = "{0}  loading...({1})".format(char, self.state)
                write(status)
                flush()
                write('\x08' * len(status))

                await asyncio.sleep(0.05)

                write(' ' * len(status) + '\x08' * len(status))

        except Exception as ex:
            print(ex)

    async def hearing(self):
        #await self.set_agent_on()
        try:
            while True:
                # Set to monitor in cmd line
                #self.child.logfile_read = sys.stdout
                pattern = [
                    "Agent registered", #0
                    "Agent is already registered", #1
                    "Default agent request successful", #2
                    "Request confirmation", #3
                    "Authorize service", #4
                    "Paired: yes",  #5
                    "Paired: no",  #6
                    "Connected: yes", #7
                    "Connected: no", #8
                    "ServicesResolved: yes", #9
                    "ServicesResolved: no", #10
                    "Device has been removed", #11
                    #"[NEW]", #12
                    #"[DEL]", #13
                    #"[CHG]", #14
                    pexpect.TIMEOUT,#12
                    pexpect.EOF,#13
                ]
                res = await self.child.expect(pattern, timeout=2, async_=True)
                #print(res)
                if res == 0 or res == 1:
                    # await asyncio.sleep(1)
                    self.state = StateType.READY.name
                    await self.get_agent_output("agent on", 1)

                    # await asyncio.sleep(1)
                    self.state = StateType.SET_DEFUALT_DEVICE.name
                    await self.get_agent_output("default-agent", 1)

                elif res == 2:
                    await self.get_agent_output("discoverable on", 1)

                    self.state = StateType.REQUEST_PAIRED_DEVICES.name
                    self.paired_devices = await self.get_paired_devices()
                    if len(self.paired_devices) > 0:
                        self.state = StateType.WAITING_REQUEST.name
                        #print(self.paired_devices)

                elif res == 3:
                    self.state = StateType.REQUEST_PAIRING.name
                    await self.get_agent_output("yes",1)
                elif res == 4:
                    await self.get_agent_output("no")
                elif res == 5:
                    self.state = StateType.PAIRED.name
                elif res == 6:
                    self.state = StateType.UNPAIRED.name
                elif res == 7:
                    self.state = StateType.CONNECTED.name
                elif res == 8:
                    self.state = StateType.DISCONNECTED.name
                elif res == 9:
                    self.state = StateType.SERVICE_RESOLVED_YES.name
                elif res == 10:
                    self.state = StateType.SERVICE_RESOLVED_NO.name
                elif res == 11:
                    pass
                elif res == 12:
                    self.state = StateType.WAITING_REQUEST.name
                    if self.reuqest_condition == StateType.REQUEST_PAIRED_DEVICES.name:
                        self.state = StateType.REQUEST_PAIRED_DEVICES.name
                        self.paired_devices = await self.get_paired_devices()
                    elif self.reuqest_condition == StateType.REQUEST_AVAILABLE_DEVICE.name:
                        self.state = StateType.REQUEST_AVAILABLE_DEVICE.name
                        self.available_devices = await self.get_available_devices()

                    self.reuqest_condition=None
                elif res == 13:
                    pass

        except Exception as ex:
            print(ex)
            pass

    def parse_device_info(self, info_string):
        """Parse a string corresponding to a device."""
        device = {}
        block_list = ["[\x1b[0;", "removed"]
        string_valid = not any(keyword in info_string for keyword in block_list)

        if string_valid:
            try:
                device_position = info_string.index("Device")
            except ValueError:
                pass
            else:
                if device_position > -1:
                    attribute_list = info_string[device_position:].split(" ", 2)
                    device = {
                        "mac_address": attribute_list[1],
                        "name": attribute_list[2]
                    }

        return device

    async def start_scan(self, cmd):
        """Start bluetooth scanning process."""
        try:
            out = await self.get_agent_output("scan " + cmd, 1)
        except Exception as ex:
            print(ex)

    async def set_agent_on(self):
        try:
            out = await self.get_agent_output("agent on", 1)
        except Exception as ex:
            print(ex)
            pass

    async def set_default_agent(self):
        try:
            out = await self.get_agent_output("default-agent", 1)
        except Exception as ex:
            print(ex)

    async def set_discoverable(self):
        """Make device discoverable."""
        try:
            out = await self.get_agent_output("discoverable on")
        except Exception as ex:
            print(ex)

    async def get_available_devices(self):
        """Return a list of tuples of paired and discoverable devices."""
        try:
            out = self.get_output("devices")
        except Exception as ex:
            print(ex)
            return None
        else:
            available_devices = []
            for line in out:
                device = self.parse_device_info(line)
                if device:
                    available_devices.append(device)

            return available_devices

    async def get_paired_devices(self):
        """Return a list of tuples of paired devices."""
        try:
            out = await self.get_agent_output("paired-devices")
        except Exception as e:
            print(e)
            return None
        else:
            paired_devices = []
            for line in out:
                device = self.parse_device_info(line)
                if device:
                    paired_devices.append(device)

            return paired_devices

    async def get_discoverable_devices(self):
        """Filter paired devices out of available."""
        try:
            available = await self.get_available_devices()
            paired = await self.get_paired_devices()

            return [d for d in available if d not in paired]
        except Exception as e:
            print(e)
            return None

    async def get_device_info(self, mac_address):
        """Get device info by mac address."""
        try:
            out = await self.get_output("info " + mac_address)
        except Exception as e:
            print(e)
            return None
        else:
            return out

    async def pair(self, mac_address):
        """Try to pair with a device by mac address."""
        try:
            out = await self.get_output("pair " + mac_address, 4)

        except Exception as e:
            print(e)
            return None
        else:
            res = await self.child.expect(["Request confirmation", pexpect.EOF], timeout=3, async_=True)
            out = self.get_output("yes", 3)
            #print("Yes!")
        finally:
            res = self.child.expect(["Failed to pair", "Pairing successful", pexpect.EOF], timeout=3, async_=True)
            #print("Successfully connected...")
            if res == 1:
                return True

    async def remove(self, mac_address):
        """Remove paired device by mac address, return success of the operation."""
        try:
            out = await self.get_output("remove " + mac_address, 3)
        except Exception as e:
            print(e)
            return None
        else:
            res = await self.child.expect(["not available", "Device has been removed", pexpect.EOF], timeout=3, async_=True)
            success = True if res == 1 else False
            return success

    async def connect(self, mac_address):
        """Try to connect to a device by mac address."""
        try:
            out = await self.get_output("connect " + mac_address, 2)
        except Exception as e:
            print(e)
            return None
        else:
            res = self.child.expect(["Failed to connect", "Connection successful", pexpect.EOF], timeout=3, async_=True)
            success = True if res == 1 else False
            return success

    async def disconnect(self, mac_address):
        """Try to disconnect to a device by mac address."""
        try:
            out = await self.get_output("disconnect " + mac_address, 2)
        except Exception as e:
            print(e)
            return None
        else:
            res = await self.child.expect(["Failed to disconnect", "Successful disconnected", pexpect.EOF], timeout=3, async_=True)
            success = True if res == 1 else False
            return success

# class BTReceive(threading.Thread):
class Bluetooth(MonitorClass):
#class BTReceive():
    def __init__(self):
        super().setBTStatus(False)

        self.receiverStatus = False
        self.monitorStatus = False
        self.hearingStatus = False

        self.threadReceive = None
        self.threadMonitor = None
        self.threadHearing = None

        self.server_sock = None
        self.client_sock = None
        self.address = None
        self.port = None

        self.msg = None

        self.paired_list = None

        # Log Object
        self.log = Logs(self.__class__.__name__)
        self.log.write(self.log.INFO, self.__init__.__name__, "initiated.")

        # BluetoothCtl Object
        self.bl = BluetoothctlAsync()

        # FileProcess Object
        self.file = FileProcess()

        # Task
        self.tasks = [
            self.bl.hearing(),
            #bl.async_loading()
        ]



    def initialize(self):
        self.setBTStatus(True)

        self.pair()
        self.setAllThreadOn()

    def load_hearing(self):
        self.bl.hearing_cmd = True
        asyncio.run(asyncio.wait(self.tasks))

    def halt_hearing(self):
        self.bl.hearing_cmd = False


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
            #print("Server socket was created")

            self.server_sock.bind(("", self.port))
            self.server_sock.listen(1)
            self.server_sock.settimeout(3)
        except Exception as ex:
            self.log.write(self.log.ERROR, self.connection.__name__, "Failed to execute : {0}".format(ex))
            #print("Failed to open or bind server socket", ex)

        try:
            if self.client_sock is not None:
                self.client_sock.close()

            #print("Try to connect to " + str(self.address))
            self.log.write(self.log.NOTICE, self.connection.__name__, "Try to connect to {0}".format(str(self.address)))

            self.client_sock, self.address = self.server_sock.accept()
            #print("Accepted : ", self.address)
        except Exception as ex:
            self.log.write(self.log.ERROR, self.connection.__name__, "Failed to execute : {0}".format(ex))
            #print("Failed to open or bind client_sock", ex)

    def setAllThreadOn(self):
        self.log.write(self.log.INFO, self.setAllThreadOn.__name__, "Called.")
        try:
            # Temporally Set Ready Baseline at this point
            self.setBTStatus(True)

            self.threadReceive = Thread(target=self.receiver)
            self.threadMonitor = Thread(target=self.monitor)
            self.threadBlCtl = Thread(target=self.load_hearing)
            self.threadReceive.daemon = False
            self.threadMonitor.daemon = False
            self.threadBlCtl.daemon = False
            self.receiverStatus = True
            self.monitorStatus = True
            self.hearingStatus = True

            self.threadReceive.start()
            self.threadMonitor.start()
            self.threadBlCtl.start()

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
        while self.monitorStatus:
            # print(self.threadReceive.is_alive())

            if self.threadReceive.is_alive() is False:
                self.setBTStatus(False)
                self.log.write(self.log.NOTICE, self.monitor.__name__, "threadReceive was terminated and will re-initiate.")
                #print("threadReceive was terminated.")
                #print("threadReceive will re-initiate.")
                self.setReceiveThreadOn()
            else :
                time.sleep(1)

    def receiver(self):
        self.log.write(self.log.INFO, self.receiver.__name__, "Called.")
        self.connection()
        try:
            while self.receiverStatus:
                # Waiting for data from Android until received
                # unlimited wait
                data = self.client_sock.recv(1024)
                data = data.decode('utf-8')
                data = str(data).replace("\n", "")
                data = data.replace("\r", "")
                self.log.write(self.log.NOTICE, self.receiver.__name__, "received : {0}".format(data))
                print("received [%s]" % data)

                self.msgConvert(data)

                time.sleep(1)

        except Exception as ex:
            # Thread will be dead with Exception
            self.closeSock()
            self.log.write(self.log.ERROR, self.receiver.__name__, "Failed to execute : {0}".format(ex))
            #print("Bluetooth was disconnected or aborted- ", ex)

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

            if self.client_sock is not None:
                self.client_sock.close()
            self.client_sock = None

            if self.server_sock is not None:
                self.server_sock.close()
            self.server_sock = None

            return True
        except Exception as ex:
            self.log.write(self.log.ERROR, self.closeSock.__name__, "Failed to execute : {0}".format(ex))
            print("Failed to close bluetooth sockets. ", ex)
            return False

    def finish(self):
        self.log.write(self.log.INFO, self.finish.__name__, "Called.")
        self.monitorStatus = False
        self.receiverStatus = False
        self.bl.hearing_cmd = False
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
