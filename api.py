from diskio import FileProcess
import requests
import json


class ApiServer:

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
        # Wifi setting Check

        url = self.setUrl()
        header = {'Content-Type': 'application/json; charset=utf-8'}
        res = None
        try:
            res = requests.post(url,
                                timeout=2,
                                headers=header,
                                data=json.dumps(dict_data))

            # res is not ok will be stored
            if not res.ok:
                print("failed to send API server")
                self.file.data_store(dict_data)
        except Exception as ex:
            self.file.data_store(dict_data)
            print("Failed to send API server", ex)

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
