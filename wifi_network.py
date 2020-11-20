import json
import multiprocessing
import time

from threading import Thread
import subprocess

from diskio import FileProcess
from logs import Logs
from monitor import MonitorClass

WIFI_INTERFACE_CHECK = "sudo iw dev"
WIFI_INTERFACE_SHOW = "sudo ip link show wlan0"
WIFI_INTERFACE_SET_DOWN = "sudo ip link set wlan0 down"
WIFI_INTERFACE_SET_UP = "sudo ip link set wlan0 up"
WIFI_CONNECTION_STATE = "sudo iw wlan0 link"
KILL_ALL_WPA_SUPPLICANT = "sudo killall wpa_supplicant"

# Wifi Scan
WIFI_SSID_SCAN = "sudo iw wlan0 scan | egrep 'SSID:' | sed -e 's/\\tSSID: //' | sort"
# WIFI_SSID_SCAN = "sudo iwlist scan | egrep 'SSID:' | sed -e  's/\\tSSID: //' | sort"

# Background Running
WIFI_WPA_CONNECT = "sudo wpa_supplicant -B -i wlan0 -c wpa_supplicant.conf"


# WIFI_WPA_CONNECT = "sudo wpa_supplicant -i wlan0 -c wpa_supplicant.conf"


class WifiNT(MonitorClass):
    def __init__(self):

        super().setWifiStatus(False)
        # print("WifiNT - ", self.getWifiStatus())

        self.pool = None
        self.func_list = [
            'wifiConnection',
        ]

        # global variable to communicate other class instance
        global ap_list
        ap_list = []

        # status variable to control thread
        self.monitorStatus = False
        self.wifiConSsid = ""

        # Thread object
        self.threadMonitor = None

        # File Control object
        self.file = FileProcess()
        self.dict_info = None
        self.log = Logs(self.__class__.__name__)
        self.log.write(self.log.INFO, self.__init__.__name__, "initiated.")

    def initialize(self):
        # self.setMultiprocess()
        # Load Network Information
        #self.loadFiles()
        self.setThreadOn()
        #self.wifiConnection()

    def funcMap(self, funcName):
        if funcName == "wifiConnection":
            self.wifiConnection()

    def setMultiprocess(self):
        try:
            pool = multiprocessing.Pool(processes=2)
            pool.map(self.funcMap, self.func_list)
            # pool.map(self.count, self.func_list)
        except Exception as ex:
            print(ex)

    def restart(self):
        self.log.write(self.log.INFO, self.restart.__name__, "Called.")
        self.monitorStatus = False
        self.wifiConSsid = ""
        self.threadMonitor = None

        self.finish()
        self.initialize()

    def loadFiles(self):
        self.log.write(self.log.INFO, self.loadFiles.__name__, "Called.")
        try:
            str_data = self.file.fileRead("", "network.txt")
            json_data = json.loads(str_data)
            self.dict_info = dict(json_data)
        except Exception as ex:
            self.log.write(self.log.ERROR, self.loadFiles.__name__, "Failed to execute : {0}".format(ex))

    def setThreadOn(self):
        self.log.write(self.log.INFO, self.setThreadOn.__name__, "Called.")
        try:
            if self.threadMonitor is not None and self.threadMonitor.is_alive():
                self.finish()
        except Exception as ex:
            pass

        try:
            self.threadMonitor = Thread(target=self.monitor)
            self.threadMonitor.daemon = True
            self.monitorStatus = True
            self.threadMonitor.start()

        except Exception as ex:
            self.log.write(self.log.ERROR, self.setThreadOn.__name__, "Failed to execute : {0}".format(ex))
            # print("Failed to assign or start threadMonitor. wifiNT")

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
            # print(ex)
            return None

    def getWifiList(self):
        """
        This method will return wifi ap list as ssid id
        :return:
        """

        self.log.write(self.log.INFO, self.getWifiList.__name__, "Called.")

        # dict_output = getSubpro(WIFI_SSID_SCAN, False, timeout=2)
        dict_output = self.getSubpro(WIFI_SSID_SCAN, timeout=2)

        # convert string type
        raw_str = str(dict_output['output'])

        # split "\n" to list
        ssid_list = raw_str.split("\n")
        # remove garbage ssid such as ""
        rm_list = list()

        # find "" value ssid in ssid_list
        for idx, ssid in enumerate(ssid_list):
            if ssid == '':
                rm_list.append(ssid)

        # remove "" value
        for item in rm_list:
            ssid_list.remove(item)

        return ssid_list

    def setWpaFile(self, ssid, pw):
        """
        This method will write and create wpa_supplicant.conf in current dir
        which will be used as information of wifi connection
        :param ssid:
        :param pw:
        :return:
        """
        self.log.write(self.log.INFO, self.setWpaFile.__name__, "Called.")
        dict_output = dict()
        try:
            p1 = subprocess.Popen(["wpa_passphrase", ssid, pw], stdout=subprocess.PIPE)
            p2 = subprocess.Popen(["sudo", "tee",
                                   # "a", # add information
                                   "wpa_supplicant.conf",
                                   # ">",
                                   # "/dev/null"
                                   ],
                                  stdin=p1.stdout, stdout=subprocess.PIPE)
            p1.stdout.close()
            output, err = p2.communicate()
            dict_output['output'] = output.decode('UTF-8')
            dict_output['err'] = err
            return dict_output
        except Exception as ex:
            self.log.write(self.log.ERROR, self.setWpaFile.__name__, "Failed to execute : {0}".format(ex))
            # print(ex)
            return None

    def setWpaCon(self, timeout):
        """
        Try to connect Wifi network
        :return: output
        """
        self.log.write(self.log.INFO, self.setWpaCon.__name__, "Called.")
        try:
            dict_output = self.getSubpro(WIFI_WPA_CONNECT, timeout=timeout)
            time.sleep(timeout)
            return dict_output
        except Exception as ex:
            self.log.write(self.log.ERROR, self.setWpaCon.__name__, "Failed to execute : {0}".format(ex))
            # print(ex)
            return None

    def getConSSID(self):
        """
        Get SSID with connection state
        :return:
        """
        self.log.write(self.log.INFO, self.getConSSID.__name__, "Called.")

        try:
            dict_output = self.getSubpro(WIFI_INTERFACE_CHECK)
            str_output = str(dict_output['output'])
            ssid_index = str_output.find("ssid")
            ssid_start = str_output[ssid_index:].find(" ")
            ssid_start += ssid_index + 1
            ssid_newline = str_output[ssid_index:].find("\n")
            ssid_newline += ssid_index
            ssid = str_output[ssid_start:ssid_newline]
            if ssid != "":
                self.setWifiStatus(True)

            return ssid
        except Exception as ex:
            self.log.write(self.log.ERROR, self.getConSSID.__name__, "Failed to execute : {0}".format(ex))
            # return will be blank.
            return ""

    def isMatched(self):
        #self.loadFiles()
        try:
            if self.wifiConSsid != self.dict_info["wifi-ssid"]:
                self.log.write(self.log.NOTICE, self.isMatched.__name__,
                               "Wifi is not matched. Before[{0}], Now[{1}]".format(self.dict_info["wifi-ssid"],
                                                                                   self.wifiConSsid))
                return False
            else:
                return True
        except Exception as ex:
            self.log.write(self.log.ERROR, self.isMatched.__name__, "Failed to execute : ", ex)
            print("ex - ", ex)
            return False


    def isConnected(self, fetchedSsid):
        self.wifiConSsid = fetchedSsid
        try:
            # isConnected???
            if self.wifiConSsid == "" or self.wifiConSsid is None:
                self.log.write(self.log.NOTICE, self.isConnected.__name__, "Wifi was disconnected.")
                print("wifi module was failed to connect AP({0})".format(self.dict_info["wifi-ssid"]))
                return False

            # isMatched??
            elif self.isMatched():
                return True
            else:
                self.log.write(self.log.NOTICE, self.isConnected.__name__, "Wifi ssid was changed.")
                print("wifi module was failed to connect AP({0})".format(self.dict_info["wifi-ssid"]))
                return False

        except Exception as ex:
                self.log.write(self.log.ERROR, self.isConnected.__name__, "Failed to execute : ",ex)
                print("ex - ", ex)

    def monitor(self):
        self.log.write(self.log.INFO, self.monitor.__name__, "Called.")
        while self.monitorStatus:
            # Load File information
            self.loadFiles()

            fetchedSsid = self.getConSSID()

            # Wifi
            # curWifiStatus = self.getWifiStatus()
            #print("=================monitor====================")
            if not self.getWifiStatus():
                self.log.write(self.log.NOTICE, self.monitor.__name__, "Wifi was disconnected.")
                print("wifi module was failed to connect AP({0})".format(self.dict_info["wifi-ssid"]))
                self.wifiConnection()
                time.sleep(2)
                #continue
            # conResult = self.isConnected(fetchedSsid)
            elif not self.isConnected(fetchedSsid):
                self.setWifiStatus(False)
                self.wifiConnection()
                time.sleep(2)
                #self.restart()
                # try:
                #     self.log.write(self.log.NOTICE, self.monitor.__name__, "Wifi connection will be initialized")
                #     print("Wifi connection will be initialized")
                #     self.restart()
                # except Exception as ex:
            else:
                self.log.write(self.log.NOTICE, self.monitor.__name__,
                               "Current Wifi info Setting. Before[{0}], Now[{1}]".format(self.dict_info["wifi-ssid"],
                                                                                        self.wifiConSsid))
                time.sleep(5)

    def wifiConnection(self):
        """
        wifiConnection will execute the connection process with subprocess module
        :return:
        """
        #print("=================wifiConnection====================")
        self.log.write(self.log.INFO, self.wifiConnection.__name__, "Called.")

        # Load File information
        if self.dict_info is None:
            self.loadFiles()

        ssid = self.dict_info["wifi-ssid"]
        pw = self.dict_info["wifi-password"]

        try:
            self.log.write(self.log.INFO, self.wifiConnection.__name__, "Wifi Module was DOWN.")
            # print("----------    Down   --------------------")
            dict_output = self.getSubpro(KILL_ALL_WPA_SUPPLICANT, timeout=2)
            time.sleep(1)

            self.log.write(self.log.INFO, self.wifiConnection.__name__, "Wifi Module was UP.")
            # print("----------    Up   --------------------")
            dict_output = self.getSubpro(WIFI_INTERFACE_SET_UP, timeout=5)
            time.sleep(2)

            # print("----------    Scan   --------------------")
            # dict_output = self.getSubpro(WIFI_SSID_SCAN, timeout=2)
            # print(dict_output['output'])
            # time.sleep(2)
            #
            # print("----------    Check connection state   --------------------")
            # dict_output = self.getSubpro(WIFI_CONNECTION_STATE, timeout=2)
            # print(dict_output['output'])
            # time.sleep(2)

            self.log.write(self.log.INFO, self.wifiConnection.__name__, "wpa_supplicant.conf was created.")
            # print("----------   Set File --------------------")
            dict_output = self.setWpaFile(ssid, pw)
            self.log.write(self.log.NOTICE, self.wifiConnection.__name__, "{0}".format(dict_output['output']))
            # print(dict_output['output'])

            self.log.write(self.log.INFO, self.wifiConnection.__name__,
                           "Wifi Module tried to connect AP({0})".format(ssid))
            # print("----------   Set Connection --------------------")
            dict_output = self.setWpaCon(timeout=5)
            self.log.write(self.log.NOTICE, self.wifiConnection.__name__, "{0}".format(dict_output['output']))
            # print(dict_output['output'])
            time.sleep(5)

            self.log.write(self.log.INFO, self.wifiConnection.__name__, "Get Wifi Connection State from Wifi Module.")
            # print("-----------  Get Wifi Connection State-------------------")
            dict_output = self.getSubpro(WIFI_CONNECTION_STATE)
            self.log.write(self.log.NOTICE, self.wifiConnection.__name__, "{0}".format(dict_output['output']))
            # print(dict_output['output'])
            time.sleep(5)

            self.log.write(self.log.INFO, self.wifiConnection.__name__, "Get Connected SSID.")
            # print("-----------  Get Wifi Connection State-------------------")
            output = self.getConSSID()
            self.log.write(self.log.NOTICE, self.wifiConnection.__name__, "{0}".format(output))
            # print(output)

            if output == ssid:
                self.setWifiStatus(True)
                self.wifiConSsid = ssid
                self.log.write(self.log.INFO, self.wifiConnection.__name__, "Connection Validated.")
                print("WiFi was connected to {0}".format(self.wifiConSsid))
                return True
            else:
                return False

        except Exception as ex:
            self.log.write(self.log.ERROR, self.wifiConnection.__name__, "Failed to execute : {0}".format(ex))
            # print(ex)

            return False

    def finish(self):
        self.log.write(self.log.INFO, self.finish.__name__, "Called.")
        self.monitorStatus = False
        self.setWifiStatus(False)
        try:
            if self.threadMonitor is not None and self.threadMonitor.is_alive():
                self.threadMonitor.join()
                self.log.write(self.log.NOTICE, self.finish.__name__, "Wifi threadMonitor was successfully finished.")
                print("Wifi threadMonitor was successfully finished")

            return True

        except Exception as ex:
            self.log.write(self.log.ERROR, self.finish.__name__, "Failed to execute : {0}".format(ex))
            print("Wifi Join threads were failed - ", ex)
            return False
