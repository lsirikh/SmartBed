import os
from datetime import datetime
import json
import csv


class FileProcess:

    def fileRead(self, subDir, filename):
        if self.isFileExist(subDir, filename):
            f = open(filename, 'r')
            line = f.read()
            f.close()
            return line
        else:
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
        try:
            if self.isFileExist(subDir, filename):
                f = open("user.txt", 'w')
                json.dump(dict_data, f, indent=4)
                f.close()

        except Exception as ex:
            pass

    def checkDir(self, subDir):
        """
        Directory check whether ./data directory exists or not
        :return: boolean
        """
        try:
            dir = os.getcwd()
            if not (os.path.isdir(dir + subDir)):
                os.makedirs(os.path.join(dir + subDir))

            return True

        except OSError as e:
            print("Failed to create directory!!!!!")
            return False

    def getFilePath(self, subDir, filename):
        try:
            dir = os.getcwd()
            filepath = os.path.join(dir + subDir +"/{0}".format(filename))
            return filepath

        except Exception as ex:
            print("Failed to execute getFilePath!!!!")
            return None

    def isFileExist(self, subDir, filename):
        try:
            filepath = self.getFilePath(subDir, filename)

            if (subDir == "") and (os.path.isfile(filepath)):
                return True

            elif (subDir == "") and (not os.path.isfile(filepath)):
                f = open(filepath, "w")
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
                json.dump(data, f, indent=4)
                f.close()
                return True

            # subDir == /data
            elif (subDir != "") and (not os.path.isfile(filepath)):
                return False
            elif (subDir != "") and (os.path.isfile(filepath)):
                return True

        except Exception as ex:
            print("Failed to execute checkFiles!!!!")
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

    def checkDataFile(self):

        dt = datetime.now()
        stf = dt.strftime('%Y%m%d_%Hh')
        # checkData info Dictionary
        dict = {}
        dict["filepath"] = None
        dict["isNew"] = False

        # subDir variable
        subDir = "/data"

        # set filename
        filename = "data{0}.txt".format(stf)

        try:
            # default setting info
            filepath = self.getFilePath(subDir, filename)
            dict["filepath"] = filepath

            if not self.isFileExist(subDir, filename):
                # if not os.path.isfile(filepath):
                fid = open(filepath, "w")
                fid.close()
                dict["isNew"] = True

        except Exception as ex:
            print("Failed to execute checkDataFile!!!!")

        return dict

    def data_store(self, dict):

        # get dictionary type data of file status
        r_dict = self.checkDataFile()
        filepath = r_dict["filepath"]
        isNew = r_dict["isNew"]
        print(filepath)
        if filepath != None:
            try:

                with open(filepath, 'a+', newline='') as f:
                    # Create a csv.writer object
                    csv_writer = csv.writer(f)
                    # Newly create file needs keys
                    if isNew:
                        csv_writer.writerow(dict.keys())

                    # Add contents of list as last row in the file
                    csv_writer.writerow(dict.values())
                    f.close()

            except Exception as ex:
                print("Failed to store sensor data!!!")

    def data_load(self, filename):
        subDir = "/data"
        if self.isFileExist(subDir, filename):
            filepath = self.getFilePath(subDir, filename)
            dict_data = []
            with open(filepath, mode='r') as f:
                fieldnames = ['collect_time', 'duid', 'name', 'sex',
                              'age', 'height', 'weight', 'accelerationx',
                              'accelerationy', 'accelerationz', 'temperature',
                              'humidity', 'lightsensor', 'pad_value']
                data = csv.DictReader(f)

                for row in data:
                    dict_data.append(dict(row))

                return dict_data
