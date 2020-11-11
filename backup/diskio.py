import os
from datetime import datetime
import json

class FileProcess:


    def bt_file_read(self):
        f = open("test/network.txt", 'r')
        line = f.read()
        f.close()
        return line


    def checkDir(self):
        """
        Directory check whether ./data directory exists or not
        :return: boolean
        """
        try:
            dir = os.getcwd()
            if not (os.path.isdir(dir+"/data")):
                os.makedirs(os.path.join(dir+"/data"))

            return True

        except OSError as e:
            print("Failed to create directory!!!!!")
            return False

    def checkFile(self):

        dt = datetime.now()
        stf = dt.strftime('%Y%m%d')
        filepath = None

        try:
            if self.checkDir():
                dir = os.getcwd()
                dir +="/data/"
                filepath = os.path.join(dir+"data{0}.txt".format(stf))
                if not os.path.isfile(filepath):
                    fid = open(filepath, "w")
                    #fid.write("Text file creation example.")
                    fid.close()

        except Exception as ex:
            print("Failed to create data file!!!!")

        return filepath
    def data_store(self, dict):

        filepath = self.checkFile()
        if filepath != None :
            try:
                with open(filepath, 'a') as f:
                    json.dump(dict, f, indent=4)

            except Exception as ex:
                print("Failed to store sensor data!!!")