import datetime
import os


class Logs:

    INFO = "0"
    NOTICE = "1"
    WARNING = "2"
    ERROR = "3"

    def __init__(self, cName=None):
        self.cName = cName

    def getFileTimeStamp(self):

        dt = datetime.datetime.now()
        stf = dt.strftime('%Y%m%d_%Hh')
        return stf

    def getLogTimeStamp(self):

        dt = datetime.datetime.now()
        stf = dt.strftime('%Y%m%d %H:%M:%S.%f')
        return stf

    def setFormat(self, level, cName, mName):
        """

        :param level:
        :param cName:
        :param mName:
        :return:
        """
        stf = self.getLogTimeStamp()
        lName = None

        if level == self.INFO:
            lName = "INFO"
        elif level == self.NOTICE:
            lName = "NOTICE"
        elif level == self.WARNING:
            lName = "WARNING"
        elif level == self.ERROR:
            lName = "ERROR"

        str_data = "[{0}] {1} [Class:{2}][Method:{3}]".format(lName, stf, cName, mName)

        return str_data

    def write(self, level, mName, comment):
        """
        Format
        [INFO] 2020-11-20 13:14:1 1123 [Class:FileProcess][Method:fileRead] (str)failed to open file blablabla
        log
        :param level:
        :param cName:
        :param mName:
        :param comment:
        :return:
        """

        log_format=self.setFormat(level, self.cName, mName)
        log_line = "{0} {1}".format(log_format, comment)

        self.save(log_line)


    def save(self, log):
        """

        :param log:
        :return:
        """
        filename = "logs_{0}".format(self.getFileTimeStamp())
        subDir = "/logs"
        self.fileWrite(subDir, filename, log)



    def fileWrite(self, subDir, filename, data):
        try:
            if self.isFileExist(subDir, filename):
                filename=self.getFilePath(subDir, filename)
                f = open(filename, 'a+', newline='', encoding='UTF-8')
                f.write(data+"\n")
                f.close()
            else:
                filename = self.getFilePath(subDir, filename)
                f = open(filename, 'w', newline='', encoding='UTF-8')
                f.write(data+"\n")
                f.close()

            return True
        except Exception as ex:
            print(ex)
            return False

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

        except OSError as ex:
            print(ex)
            return False

    def getFilePath(self, subDir, filename):
        try:
            dir = os.getcwd()
            filepath = os.path.join(dir + subDir +"/{0}".format(filename))
            return filepath

        except Exception as ex:
            print(ex)
            return None

    def isFileExist(self, subDir, filename):
        try:
            filepath = self.getFilePath(subDir, filename)
            self.checkDir(subDir)
            # subDir == /logs
            if not os.path.isfile(filepath):
                return False
            elif os.path.isfile(filepath):
                return True

        except Exception as ex:
            print(ex)
            return False

