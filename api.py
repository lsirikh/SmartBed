from diskio import FileProcess
import requests
import json


class ApiServer:
    # file = None
    # prop_dict = {}

    def __init__(self):
        self.file = FileProcess()
        str = self.file.fileRead("", "network.txt")
        json_data = json.loads(str)
        self.prop_dict = dict(json_data)

    def setUrl(self):
        protocol = "http://"
        ip = self.prop_dict["cloud_server-ip"]
        port = self.prop_dict["cloud_server-port"]
        urls = self.prop_dict["cloud_server-urls"]
        return protocol+ip+":"+str(port)+urls


    def dataSend(self, dict_data):

        #url = 'http://182.173.185.246:3001/api/Bed/Sensor/SendData/Start'
        url = self.setUrl()
        header = {'Content-Type': 'application/json; charset=utf-8'}

        res = requests.post(url, headers=header, data=json.dumps(dict_data))

        # s.file.data_store(dict_data)
        self.file.data_store(dict_data)

        return res


    def storedDataSend(self, dict_list):
        url = self.setUrl()
        header = {'Content-Type': 'application/json; charset=utf-8'}
        dict_info = {}
        list_failed_data = []
        dict_info['result'] = True
        dict_info['list_failed_data'] = None

        for dict_data in dict_list:
            res = requests.post(url, headers=header, data=json.dumps(dict_data))

            if not res.ok:
                list_failed_data.append(dict_data)
                dict_info['result'] = False

        dict_info['list_failed_data'] = list_failed_data

        return dict_info
