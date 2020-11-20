import os
from datetime import datetime
import json
import csv

from logs import Logs


class FileProcess:

    def __init__(self):
        self.log = Logs(self.__class__.__name__)
        self.log.write(self.log.INFO, self.__init__.__name__, "initiated.")

    def fileRead(self, subDir, filename):
        self.log.write(self.log.INFO, self.fileRead.__name__, "Called.")
        try:
            if self.isFileExist(subDir, filename):
                f = open(filename, 'r', encoding='UTF-8')
                line = f.read()
                f.close()
                return line
            else:
                return None
        except Exception as ex:
            self.log.write(self.log.ERROR, self.fileRead.__name__, "Failed to excute : {0}".format(ex))
            return None

    # def networkFileRead(self):
    #     subDir = ""
    #     filename = "network.txt"
    #     if self.checkFiles(subDir, filename):
    #         f = open(filename, 'r')
    #         line = f.read()
    #         f.close()
    #         return line
    #     else:
    #         return None
    #
    # def userFileRead(self):
    #     subDir = ""
    #     if self.checkFiles(subDir,"user.txt"):
    #         f = open("user.txt", 'r')
    #         line = f.read()
    #         f.close()
    #         return line
    #
    # def infoFileRead(self):
    #     subDir = ""
    #     if self.checkFiles(subDir,"info"):
    #         f = open("info.txt", 'r')
    #         line = f.read()
    #         f.close()
    #         return line
    #
    # def bedFileRead(self):
    #     subDir = ""
    #     if self.checkFiles(subDir,"bed"):
    #         f = open("bed.txt", 'r')
    #         line = f.read()
    #         f.close()
    #         return line

    def fileWrite(self, subDir, filename, dict_data):
        self.log.write(self.log.INFO, self.fileWrite.__name__, "Called.")
        try:
            if self.isFileExist(subDir, filename):
                f = open(filename, 'w', encoding='UTF-8')
                json.dump(dict_data, f, indent=4, ensure_ascii=False)
                f.close()

            return True
        except Exception as ex:
            self.log.write(self.log.ERROR, self.fileWrite.__name__, "Failed to excute : {0}".format(ex))
            #print("Failed to execute fileWrite!!!!")
            return False

    def checkDir(self, subDir):
        """
        Directory check whether ./data directory exists or not
        :return: boolean
        """
        self.log.write(self.log.INFO, self.checkDir.__name__, "Called.")
        try:
            dir = os.getcwd()
            if not (os.path.isdir(dir + subDir)):
                os.makedirs(os.path.join(dir + subDir))

            return True

        except OSError as ex:
            self.log.write(self.log.ERROR, self.checkDir.__name__, "Failed to excute : {0}".format(ex))
            #print("Failed to create directory!!!!!")
            return False

    def getFilePath(self, subDir, filename):
        self.log.write(self.log.INFO, self.getFilePath.__name__, "Called.")
        try:
            dir = os.getcwd()
            filepath = os.path.join(dir + subDir +"/{0}".format(filename))
            return filepath

        except Exception as ex:
            self.log.write(self.log.ERROR, self.getFilePath.__name__, "Failed to excute : {0}".format(ex))
            #print("Failed to execute getFilePath!!!!")
            return None

    def getDirFiles(self, subDir):
        result = self.checkDir(subDir)
        try:
            if result:
                myPath = os.getcwd() + subDir
                file_list = [f for f in os.listdir(myPath) if os.path.isfile(os.path.join(myPath, f))]
                return file_list
        except Exception as ex:
            self.log.write(self.log.ERROR, self.getFilePath.__name__, "Failed to excute : {0}".format(ex))
            #print("Failed to execute getDirFiles!!!!")
            return None

    def isFileExist(self, subDir, filename):
        self.log.write(self.log.INFO, self.isFileExist.__name__, "Called.")
        try:
            filepath = self.getFilePath(subDir, filename)

            if (subDir == "") and (os.path.isfile(filepath)):
                return True

            elif (subDir == "") and (not os.path.isfile(filepath)):
                f = open(filepath, "w", encoding='UTF-8')
                data = ""
                if filename == "user.txt":
                    # data = {'duid': '0000000000000', 'name': 'default',
                    #         'sex': 'm', 'age': 0, 'height': 0, 'weight': 0}
                    data = {'name': 'default', 'sex': 'm', 'age': 0,
                            'height': 0, 'weight': 0}
                elif filename == "info.txt":
                    data = {'collection_period': 1, 'store_time': 24,
                            'max_file': 10, 'numbering': 0}
                elif filename == "bed.txt":
                    data = {'duid': "0000000000000"}
                elif filename == "network.txt":
                    data = {"bluetooth": "",
                            "wifi-ssid": "",
                            "wifi-password": "",
                            "time_server-ip": "",
                            "time_server-port": 0,
                            "cloud_server-ip": "",
                            "cloud_server-port": 0,
                            "cloud_server-urls": ""
                            }
                elif filename == "reqeust.txt":
                    data = {"target": 0,
                            "range_start": "2020-01-01 00:00:00",
                            "range_stop": "2020-01-01 23:59:59",
                            "bed_num": "0000000000000"
                            }
                json.dump(data, f, indent=4)
                f.close()
                return True

            # subDir == /data
            elif (subDir != "") and (not os.path.isfile(filepath)):
                return False
            elif (subDir != "") and (os.path.isfile(filepath)):
                return True

        except Exception as ex:
            self.log.write(self.log.ERROR, self.isFileExist.__name__, "Failed to excute : {0}".format(ex))
            #print("Failed to execute checkFiles!!!!")
            return False

    # def isDataExist(self, file):
    #     try:
    #         if self.checkDir():
    #             dir = os.getcwd()
    #             dir += "/data/"
    #             filepath = os.path.join(dir + str(file))
    #             if os.path.isfile(filepath):
    #                 return True
    #             else:
    #                 return False
    #
    #     except Exception as ex:
    #         print("Failed to execute isDataExist!!!!")
    #         return False

    def getTimeStamp(self):
        self.log.write(self.log.INFO, self.getTimeStamp.__name__, "Called.")
        dt = datetime.now()
        stf = dt.strftime('%Y%m%d_%Hh')
        return stf

    def checkDataFile(self):
        self.log.write(self.log.INFO, self.checkDataFile.__name__, "Called.")
        stf = self.getTimeStamp()
        # checkData info Dictionary
        dict_data = {}
        dict_data["filepath"] = None
        dict_data["isNew"] = False

        # subDir variable
        subDir = "/data"

        # set filename
        filename = "data{0}.txt".format(stf)

        try:
            # default setting info
            filepath = self.getFilePath(subDir, filename)
            dict_data["filepath"] = filepath

            if not self.isFileExist(subDir, filename):
                # if not os.path.isfile(filepath):
                fid = open(filepath, "w")
                fid.close()
                dict_data["isNew"] = True

        except Exception as ex:
            self.log.write(self.log.ERROR, self.checkDataFile.__name__, "Failed to excute : {0}".format(ex))
            #print("Failed to execute checkDataFile!!!!")

        return dict_data

    def data_store(self, dict_arg):
        self.log.write(self.log.INFO, self.data_store.__name__, "Called.")
        # get dictionary type data of file status
        r_dict = self.checkDataFile()
        filepath = r_dict["filepath"]
        isNew = r_dict["isNew"]

        if filepath != None:
            try:

                with open(filepath, 'a+', newline='', encoding='UTF-8') as f:
                    # Create a csv.writer object
                    csv_writer = csv.writer(f)
                    # Newly create file needs keys
                    if isNew:
                        csv_writer.writerow(dict_arg.keys())

                    # Add contents of list as last row in the file
                    csv_writer.writerow(dict_arg.values())
                    f.close()

            except Exception as ex:
                self.log.write(self.log.ERROR, self.data_store.__name__, "Failed to excute : {0}".format(ex))
                #print("Failed to store sensor data!!!")

    def data_load(self, filename):

        self.log.write(self.log.INFO, self.data_load.__name__, "Called.")
        subDir = "/data"
        if self.isFileExist(subDir, filename):
            filepath = self.getFilePath(subDir, filename)
            dict_data = []
            try:
                with open(filepath, mode='r', encoding='UTF-8') as f:
                    fieldnames = ['collect_time', 'duid', 'name', 'sex',
                                  'age', 'height', 'weight', 'accelerationx',
                                  'accelerationy', 'accelerationz', 'temperature',
                                  'humidity', 'lightsensor', 'pad_value']
                    data = csv.DictReader(f)

                    for row in data:
                        dict_data.append(dict(row))

                    return dict_data

            except Exception as ex:
                self.log.write(self.log.ERROR, self.data_load.__name__, "Failed to excute : {0}".format(ex))
                return False