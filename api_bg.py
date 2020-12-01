import asyncio
import datetime
import itertools
import json
import os
import sys
import time

from enum import Enum

import aiofiles.os
import aiohttp
import requests
import csv
# from aiocsv import AsyncReader, AsyncDictReader, AsyncWriter, AsyncDictWriter
import aiocsv

from timeit import default_timer as dt

class StateType(Enum):
    READY = 1
    LOADFILE = 2
    SEND = 3
    SEND_SUCCESS = 4
    SEND_FAIL = 5
    REMOVE_FILE = 6
    SEND_FILE_COMPLETE = 7
    SEND_SERVICE_COMPLETE = 7


class AsyncHttp:


    def __init__(self):

        self.s = dt()
        self.url = "http://182.173.185.246:3001/api/Bed/Sensor/SendData/Start"
        self.response_result = []
        self.load_list = []
        self.failed_list = []
        self.state = StateType.READY.name

    def isFileExist(self, subDir, filename):
        try:
            filepath = self.getFilePath(subDir, filename)

            # subDir == /data
            if (subDir != "") and (not os.path.isfile(filepath)):
                #print("{0} is not exist...".format(filename))
                return False
            elif (subDir != "") and (os.path.isfile(filepath)):
                print("{0} was found...".format(filename))
                return True

        except Exception as ex:
            print(ex)

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
            # print("Failed to create directory!!!!!")
            return False

    def getDirFiles(self, subDir):
        result = self.checkDir(subDir)
        try:
            if result:
                myPath = os.getcwd() + subDir
                file_list = [f for f in os.listdir(myPath) if os.path.isfile(os.path.join(myPath, f))]
                return file_list
        except Exception as ex:
            return None

    def getFilePath(self, subDir, filename):
        try:
            dir = os.getcwd()
            filepath = os.path.join(dir + subDir + "/{0}".format(filename))
            return filepath

        except Exception as ex:
            # print("Failed to execute getFilePath!!!!")
            return None

    def d_load(self, filename):
        subDir = "/data"
        if self.isFileExist(subDir, filename):
            filepath = self.getFilePath(subDir, filename)
            dict_data = []
            print("-----------------")
            try:
                with open(filepath, mode='r', encoding='UTF-8') as f:
                    data = csv.DictReader(f)

                for row in data:
                    print(row)
                    dict_data.append(dict(row))

                return dict_data

            except Exception as ex:
                print(ex)
                return False

    async def send_data_with_range(self, date_range):
        TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        FILE_FORMAT = "%Y%m%d_%Hh"

        try:
            begin_date = datetime.datetime.strptime(date_range["begin_date"], TIME_FORMAT)
            end_date = datetime.datetime.strptime(date_range["end_date"], TIME_FORMAT)

            index_time = 0
            while True:
                if begin_date+datetime.timedelta(hours=index_time) > end_date:
                    break
                set_date_with_time = begin_date+datetime.timedelta(hours=index_time)
                set_date_with_time = set_date_with_time.strftime(FILE_FORMAT)
                filename = "data{0}.txt".format(set_date_with_time)
                await self.load_data_to_send(filename)
                #print(filename)
                index_time += 1


            await asyncio.sleep(0.01)
            print(begin_date, end_date)
        except Exception as ex:
            print(ex)
        pass

    async def load_data_to_send(self, filename):

        subDir = "/data"
        if self.isFileExist(subDir, filename):
            filepath = self.getFilePath(subDir, filename)
            try:
                async with aiofiles.open(filepath, mode="r", encoding="utf-8", newline="") as f:
                    self.state = StateType.LOADFILE.value
                    async for row in aiocsv.AsyncDictReader(f):

                        # OrderedDict to Dict
                        dict_row = dict(row)

                        # async API data request
                        result = await self.async_request(dict_row)

                        if result["status"] != "success":
                            self.state = StateType.SEND_FAIL.name
                            self.failed_list.append(dict)
                        else:
                            self.state = StateType.SEND_SUCCESS.name
                            #print("Failed!!!")
                        await asyncio.sleep(0.1)
                        #print(dict_row)  # row is a dict
                        self.response_result.append(result)

                # if all records was successfully transferred. a file will be removed
                if len(self.failed_list) == 0:
                    self.state = StateType.REMOVE_FILE.name
                    await aiofiles.os.remove(filepath)
                    print("All data was successfully transferred and {0} was removed".format(filename))

                    #return dict_data
                self.state = StateType.SEND_FILE_COMPLETE.name
                return True
            except Exception as ex:
                print(ex)
                return False

    async def async_request(self, data=None):
        # requests의 Session 클래스 같은 역할입니다.
        async with aiohttp.ClientSession() as session:
            # 실제 요청을 비동기적으로 발생시킵니다.
            async with session.post(self.url, data=data) as response:
                self.state = StateType.SEND.name
                temp = await response.text()
                json_result = json.loads(temp)
                result = dict(json_result)
                return result

    def timeStamp(self):
        """

        :return:
        """
        dt = datetime.datetime.now()
        stamp = dt.strftime('%Y-%m-%d %H:%M:%S.%f')
        return stamp

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

                if self.state == StateType.SEND_SERVICE_COMPLETE:
                    break

            write(' ' * len(status) + '\x08' * len(status))

        except Exception as ex:
            print(ex)


    def loop_caller(self, range):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            loop.run_until_complete(self.send_data_with_range(range))
            loop.close()
        except Exception as ex:
            print(ex)