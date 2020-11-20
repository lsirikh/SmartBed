SUCCESS = "success"
FAIL = "failure"


class TypeMessage:
    """
    ᆞTypeMessage : 메시지 타입
    """
    typeMessage = ""

    def __init__(self, dict):
        self.typeMessage = dict["TypeMessage"]


class RequestData(TypeMessage):
    """
    수집데이터 전송 요청
    {
       "TypeMessage":1,
       "RequestData_Option": {
          "Target" : 0,
          "Range_Start" : "2019-08-23 12:00:00",
          "Range_Stop" : "2019-08-23 12:00:00",
          "Bed_Num" : "8800000000000"
       }
    }
    """

    def __init__(self, dict):
        super().__init__(dict)
        self.target = dict["RequestData_Option"]["Target"]
        self.range_start = dict["RequestData_Option"]["Range_Start"]
        self.range_end = dict["RequestData_Option"]["Range_Stop"]
        self.bed_num = dict["RequestData_Option"]["Bed_Num"]

    def __str__(self):
        return "{},{},{},{},{}".format(self.typeMessage, self.target,
                                       self.range_start, self.range_end,
                                       self.bed_num)

    def checkBedNum(self, num):
        if num != self.bed_num:
            return False
        else:
            return True

    def setRequest(self):
        dict_data = dict()
        try:

            dict_data["target"] = 0
            dict_data["range_start"] = self.range_start
            dict_data["range_stop"] = self.range_end
            dict_data["bed_num"] = self.bed_num
            return dict_data

        except Exception as ex:
            print(ex)
            return False


    def response(self, flag):
        """
        {
           "TypeMessage":101,
           "RequestData_Option": {
              "RequestData_Set" : "success"
           }
        }
        :param flag: True or False boolean value
        :return: Dict type data will be converted into json message
        """
        dict_return = {"TypeMessage": self.typeMessage+100,
                       "RequestData_Option":
                           {
                               "RequestData_Set": "",
                           }
                       }
        if flag:
            dict_return["RequestData_Option"]["RequestData_Set"] = SUCCESS
        else:
            dict_return["RequestData_Option"]["RequestData_Set"] = FAIL

        return dict_return


class User(TypeMessage):
    """
    사용자 정보 설정
    {
       "TypeMessage":2,
       "User_Option": {
          "Name" : "홍길동",
          "Sex" : "male",
          "Age" : "19",
          "Height" : "185",
          "Weight" : "78"
       }
    }
    """

    def __init__(self, dict):
        super().__init__(dict)
        self.name = dict["User_Option"]["Name"]
        self.sex = dict["User_Option"]["Sex"]
        self.age = dict["User_Option"]["Age"]
        self.height = dict["User_Option"]["Height"]
        self.weight = dict["User_Option"]["Weight"]

    def __str__(self):
        return "{},{},{},{},{},{}".format(self.typeMessage, self.name, self.sex,
                                          self.age, self.height, self.weight)

    def getData(self):
        dict_data = {
            'name': self.name, 'sex': self.sex,
            'age': self.age, 'height': self.height,
            'weight': self.weight}
        return dict_data

    def response(self, flag):
        """
        {
           "TypeMessage":102,
           "User_Option": {
              "User_Setting" : "success"
           }
        }
        :param flag: True or False boolean value
        :return: Dict type data will be converted into json message
        """
        dict_return = {"TypeMessage": self.typeMessage+100,
                       "User_Option":
                           {
                               "User_Setting": "",
                           }
                       }
        if flag:
            dict_return["User_Option"]["User_Setting"] = SUCCESS
        else:
            dict_return["User_Option"]["User_Setting"] = FAIL

        return dict_return


class InfoTime(TypeMessage):
    """
    시간 정보 설정
    {
       "TypeMessage":3,
       "Time_Option": {
          "Date" : "2019-08-26",
          "Time" : "17:00:00"
       }
    }
    """

    def __init__(self, dict):
        super().__init__(dict)
        self.date = dict["Time_Option"]["Date"]
        self.time = dict["Time_Option"]["Time"]

    def __str__(self):
        return "{},{},{}".format(self.typeMessage, self.date, self.time)

    def response(self, flag):
        """
        {
           "TypeMessage":103,
           "Time_Option": {
              "Time_Setting" : "success"
           }
        }
        :param flag: True or False boolean value
        :return: Dict type data will be converted into json message
        """
        dict_return = {"TypeMessage": self.typeMessage+100,
                       "Time_Option":
                           {
                               "Time_Setting": "",
                           }
                       }
        if flag:
            dict_return["Time_Option"]["Time_Setting"] = SUCCESS
        else:
            dict_return["Time_Option"]["Time_Setting"] = FAIL

        return dict_return


class WifiInfo(TypeMessage):
    """
    Wifi 연결 정보 확인 요청
    {
       "TypeMessage":4,
       "Wifi_Option": {
          "Option_Sel" : 0,
          "Wifi_Info_Chk" : "on"
       }
    }
    """

    def __init__(self, dict):
        super().__init__(dict)
        self.option_sel = dict["Wifi_Option"]["Option_Sel"]
        self.wifi_info_chk = dict["Wifi_Option"]["Wifi_Info_Chk"]


    def __str__(self):
        return "{},{},{}".format(self.typeMessage, self.option_sel, self.wifi_info_chk)

    # def getSsid(self):
    #     if self.wifi_info_chk == "on" or self.wifi_info_chk == "On":
    #         return True
    #     else:
    #         return False


    def response(self, ssid):
        """
        {
           "TypeMessage":104,
           "Wifi_Option": {
              "Option_Sel" : 0,
              "Wifi_Info_Name" : "imc_wifi"
           }
        }
        :param ssid: Wifi_Info_Name
        :return: Dict type data will be converted into json message
        """
        dict_return = {"TypeMessage": self.typeMessage+100,
                       "Wifi_Option":
                           {
                               "Option_Sel": self.option_sel,
                               "Wifi_Info_Name": "",
                           }
                       }
        dict_return["Wifi_Option"]["Wifi_Info_Name"] = ssid
        #print(dict_return)

        return dict_return


class WifiSetting(TypeMessage):
    """
    Wifi 연결 정보 설정 요청
    {
       "TypeMessage":4,
       "Wifi_Option": {
          "Option_Sel" : 1,
          "Wifi_Name" : "imc_wifi",
          "Wifi_Password" : "wifi12345"
       }
    }
    """

    def __init__(self, dict):
        super().__init__(dict)
        self.option_sel = dict["Wifi_Option"]["Option_Sel"]
        self.wifi_name = dict["Wifi_Option"]["Wifi_Name"]
        self.wifi_password = dict["Wifi_Option"]["Wifi_Password"]

    def __str__(self):
        return "{},{},{},{}".format(self.typeMessage, self.option_sel, self.wifi_name, self.wifi_password)

    def setWifi(self, dict_data):
        try:
            dict_data["wifi-ssid"] = self.wifi_name
            dict_data["wifi-password"] = self.wifi_password
            return dict_data

        except Exception as ex:
            print(ex)
            return False

    def response(self, flag):
        """
        {
           "TypeMessage":104,
           "Wifi_Option": {
             "Option_Sel" : 1,
              "Wifi_Setting" : "success"
           }
        }
        :param flag: True or False boolean value
        :return: Dict type data will be converted into json message
        """
        dict_return = {"TypeMessage": self.typeMessage+100,
                       "Wifi_Option":
                           {
                               "Option_Sel": self.option_sel,
                               "Wifi_Setting": ""
                           }
                       }
        if flag:
            dict_return["Wifi_Option"]["Wifi_Setting"] = SUCCESS
        else:
            dict_return["Wifi_Option"]["Wifi_Setting"] = FAIL

        return dict_return


class WifiIP(TypeMessage):
    """
    Wifi IP 정보 설정 요청
    {
       "TypeMessage":4,
       "Wifi_Option": {
          "Option_Sel" : 2,
          "Wifi_Setip_Info" : "192.168.0.202"
       }
    }
    """

    def __init__(self, dict):
        super().__init__(dict)
        self.option_sel = dict["Wifi_Option"]["Option_Sel"]
        self.wifi_setip_info = dict["Wifi_Option"]["Wifi_Setip_Info"]

    def __str__(self):
        return "{},{},{}".format(self.typeMessage, self.option_sel, self.wifi_setip_info)

    def response(self, flag):
        """
        {
           "TypeMessage":104,
           "Wifi_Option": {
             "Option_Sel" : 1,
              "Wifi_Ip_Setting" : "success"
           }
        }
        :param flag: True or False boolean value
        :return: Dict type data will be converted into json message
        """
        dict_return = {"TypeMessage": self.typeMessage+100,
                       "Wifi_Option":
                           {
                               "Option_sel": self.option_sel,
                               "Wifi_Ip_Setting": "",
                           }
                       }
        if flag:
            dict_return["Wifi_Option"]["Wifi_Ip_Setting"] = SUCCESS
        else:
            dict_return["Wifi_Option"]["Wifi_Ip_Setting"] = FAIL

        return dict_return


class WifiAPList(TypeMessage):
    """
    Wifi IP 정보 설정 요청
    {
       "TypeMessage":4,
       "Wifi_Option": {
          "Option_Sel" : 3,
          "Wifi_AP_List_Request" : "on"
       }
    }
    """

    def __init__(self, dict):
        super().__init__(dict)
        self.option_sel = dict["Wifi_Option"]["Option_Sel"]
        self.wifi_ap_list_request = dict["Wifi_Option"]["Wifi_AP_List_Request"]

    def __str__(self):
        return "{},{},{}".format(self.typeMessage, self.option_sel, self.wifi_ap_list_request)

    def request(self):
        if self.wifi_ap_list_request == "on":
            return True
        else:
            return False

    def response(self, ap_list):
        """
        {
           "TypeMessage":104,
           "Wifi_Option": {
             "Option_Sel" : 3,
              "Wifi_AP_List" : ["a","b",...]
           }
        }
        :param flag: True or False boolean value
        :return: Dict type data will be converted into json message
        """


        dict_return = {"TypeMessage": self.typeMessage+100,
                       "Wifi_Option":
                           {
                               "Option_Sel": self.option_sel,
                               "Wifi_AP_List": "",
                           }
                       }
        if ap_list is not None:
            dict_return["Wifi_Option"]["Wifi_AP_List"] = ap_list
        else:
            dict_return["Wifi_Option"]["Wifi_AP_List"] = []

        return dict_return


class CloudInfo(TypeMessage):
    """
    클라우드 서버 연결 정보 확인 요청
    {
       "TypeMessage":5,
       "CloudServer_Option": {
          "Option_sel" : 0,
           "CloudServer_Info_Chk" : "on"
       }
    }
    """

    def __init__(self, dict):
        super().__init__(dict)
        self.option_sel = dict["CloudServer_Option"]["Option_Sel"]
        self.cloudserver_info_chk = dict["CloudServer_Option"]["CloudServer_Info_Chk"]

    def __str__(self):
        return "{},{},{}".format(self.typeMessage, self.option_sel, self.cloudserver_info_chk)

    def response(self, dict_info):
        """
        {
           "TypeMessage":105,
           "CloudServer_Option": {
              "Option_sel" : 0,
              "CloudServer_Info_host" : "imc_cloud",
              "CloudServer_Info_Database" : "imc_db"
           }
        }
        :param dict_info:
        :return:
        """
        dict_return = {"TypeMessage": self.typeMessage+100,
                       "CloudServer_Option":
                           {
                               "Option_sel": self.option_sel,
                               "CloudServer_Info_host": "",
                               "CloudServer_Info_Database": ""
                           }
                       }

        # dict_info["CloudServer_Info_host"]
        # dict_info["CloudServer_Info_Database"]
        dict_return["CloudServer_Option"]["CloudServer_Info_host"] = dict_info["CloudServer_Info_host"]
        dict_return["CloudServer_Option"]["CloudServer_Info_Database"] = dict_info["CloudServer_Info_Database"]
        return dict_return


class CloudStatus(TypeMessage):
    """
    클라우드 서버 연결 상태 확인 요청
    {
       "TypeMessage":5,
       "CloudServer_Option": {
          "Option_sel" : 1,
          "Connect_Check" : "on"
       }
    }
    """

    def __init__(self, dict):
        super().__init__(dict)
        self.option_sel = dict["CloudServer_Option"]["Option_Sel"]
        self.connect_check = dict["CloudServer_Option"]["Connect_Check"]

    def __str__(self):
        return "{},{},{}".format(self.typeMessage, self.option_sel, self.connect_check)

    def response(self, flag):
        """
        {
           "TypeMessage":105,
           "CloudServer_Option": {
              "Option_sel" : 1,
              "Connect_Check_Result" : "connect"
           }
        }
        :param flag:
        :return:
        """
        dict_return = {"TypeMessage": self.typeMessage+100,
                       "CloudServer_Option":
                           {
                               "Option_sel": self.option_sel,
                               "Connect_Check_Result": "connect"
                           }
                       }

        if flag:
            dict_return["CloudServer_Option"]["Connect_Check_Result"] = "connect"
            return dict_return
        else:
            dict_return["CloudServer_Option"]["Connect_Check_Result"] = "disconnect"
            return dict_return


class CloudInfoSet(TypeMessage):
    """
    클라우드 서버 정보 설정 요청
    {
       "TypeMessage":5,
       "CloudServer_Option": {
          "Option_sel" : 2,
          "Target" : 0
          "HostName" : "imctest.com",
          "Id" : "naver",
          "Password" : "naver1234",
       }
    }
    """

    def __init__(self, dict):
        super().__init__(dict)
        self.option_sel = dict["CloudServer_Option"]["Option_Sel"]
        self.target = dict["CloudServer_Option"]["Target"]
        self.hostname = dict["CloudServer_Option"]["HostName"]
        self.id = dict["CloudServer_Option"]["Id"]
        self.password = dict["CloudServer_Option"]["Password"]

    def __str__(self):
        return "{},{},{}".format(self.typeMessage, self.option_sel, self.target,
                                 self.hostname, self.id, self.password)

    def response(self, flag):
        """
        {
           "TypeMessage":105,
           "CloudServer_Option": {
              "Option_sel" : 2,
              "CloudServer_Setting" : "success"
           }
        }
        :param flag:
        :return:
        """
        dict_return = {"TypeMessage": self.typeMessage+100,
                       "CloudServer_Option":
                           {
                               "Option_sel": self.option_sel,
                               "CloudServer_Setting": "success"
                           }
                       }

        if flag:
            dict_return["CloudServer_Option"]["CloudServer_Setting"] = SUCCESS
            return dict_return
        else:
            dict_return["CloudServer_Option"]["CloudServer_Setting"] = FAIL
            return dict_return


class CloudCycleSet(TypeMessage):
    """
    클라우드 서버 데이터 전송주기 설정 요청
    {
    "TypeMessage":5,
    "CloudServer_Option": {
      "Option_sel" : 3,
      "Target" : 0
      "Send_Cycle" : "100ms"
    }
    }
    """

    def __init__(self, dict):
        super().__init__(dict)
        self.option_sel = dict["CloudServer_Option"]["Option_Sel"]
        self.target = dict["CloudServer_Option"]["Target"]
        self.send_cycle = dict["CloudServer_Option"]["Send_Cycle"]

    def __str__(self):
        return "{},{},{},{}".format(self.typeMessage, self.option_sel,
                                    self.target, self.send_cycle)

    def converter(self):
        if self.send_cycle == "100ms":
            return 's01'
        elif self.send_cycle == "200ms":
            return 's02'
        elif self.send_cycle == "300ms":
            return 's03'
        elif self.send_cycle == "400ms":
            return 's04'
        elif self.send_cycle == "500ms":
            return 's05'
        elif self.send_cycle == "600ms":
            return 's06'
        elif self.send_cycle == "700ms":
            return 's07'
        elif self.send_cycle == "800ms":
            return 's08'
        elif self.send_cycle == "900ms":
            return 's09'
        elif self.send_cycle == "1000ms":
            return 's10'

    def response(self, flag):
        """
        {
           "TypeMessage":105,
           "CloudServer_Option": {
              "Option_sel" : 3,
              "CloudServer_Setting" : "success"
           }
        }
        :param flag:
        :return:
        """
        dict_return = {"TypeMessage": self.typeMessage+100,
                       "CloudServer_Option":
                           {
                               "Option_sel": self.option_sel,
                               "CloudServer_Setting": "success"
                           }
                       }

        if flag:
            dict_return["CloudServer_Option"]["CloudServer_Setting"] = SUCCESS
            return dict_return
        else:
            dict_return["CloudServer_Option"]["CloudServer_Setting"] = FAIL
            return dict_return


class ApiSendData:
    """
    클라우드 서버 전송 데이터 포멧
    """

    def __init__(self, byte_data, data_dict):
        tmp_data = byte_data.decode('utf-8').split(',')[1:]
        self.collect_time = data_dict['collect_time']
        self.duid = data_dict['duid']
        self.name = data_dict['name']
        self.sex = data_dict['sex']
        self.age = data_dict['age']
        self.height = data_dict['height']
        self.weight = data_dict['weight']
        self.accelerationx = float(tmp_data[-6])
        self.accelerationy = float(tmp_data[-5])
        self.accelerationz = float(tmp_data[-4])
        self.temperature = float(tmp_data[-3])
        self.humidity = float(tmp_data[-2])
        self.lightsensor = float(tmp_data[-1])
        self.pad_value = [int(i) for i in tmp_data[:-6]]

    # def getData(self):
    #     return self.__dict__()


class PressStatus(TypeMessage):
    """
    압력센서 수집모듈 고장 상태 확인
    """

    def __init__(self, dict):
        super().__init__(dict)
        self.option_sel = dict["Module_Chk_Option"]["Option_Sel"]

    def __str__(self):
        return "{},{}".format(self.typeMessage, self.option_sel)


class StoredDataList(TypeMessage):
    """
          Stored data request
        {
           "TypeMessage":6,
           "StoredFiles_Option": {
              "Option_Sel" : 0,
              "Stored_Data_list_Request" : "on",
           }
        }
        """

    def __init__(self, dict):
        super().__init__(dict)
        self.option_sel = dict["StoredFiles_Option"]["Option_Sel"]
        self.stored_data_list_request = dict["StoredFiles_Option"]["Stored_Data_list_Request"]

    def __str__(self):
        return "{},{},{}".format(self.typeMessage, self.option_sel, self.stored_data_list_request)

    def request(self):
        if self.stored_data_list_request == "on":
            return True
        else:
            return False

    def response(self, data_list):
        """
        {
           "TypeMessage":106,
           "StoredFiles_Option": {
             "Option_Sel" : 0,
              "Stored_Data_List" : ["a.txt","b.txt",...]
           }
        }
        :param data_list:
        :return: Dict type data will be converted into json message
        """

        dict_return = {"TypeMessage": self.typeMessage + 100,
                       "StoredFiles_Option":
                           {
                               "Option_Sel": self.option_sel,
                               "Stored_Data_List": "",
                           }
                       }
        if data_list is not None:
            dict_return["StoredFiles_Option"]["Stored_Data_List"] = data_list
        else:
            dict_return["StoredFiles_Option"]["Stored_Data_List"] = []

        return dict_return


class ControlUart(TypeMessage):
    """
    Uart 데이터 전송 On/Off
    {"TypeMessage": 8,
        "Uart_Cmd_Data":{
            "Op_Mode":"on"
        }
    }
    """

    def __init__(self, dict):
        super().__init__(dict)
        self.op = dict["Uart_Cmd_Data"]["Op_Mode"]

    def __str__(self):
        return "{},{}".format(self.typeMessage, self.op)

    def operation(self):
        """

        :return:
        """
        if self.op == "on":
            # print("operation is on")
            return True
        elif self.op == "off":
            # print("operation is off")
            return False
        else:
            return False

    def response(self, flag):
        """"
        {
           "TypeMessage":108,
           "Uart_Cmd_Data": {
              "Uart_Cmd_Setting" : "success"
           }
        }
        :param flag:
        :return:
        """

        dict_return = {"TypeMessage": self.typeMessage+100,
                       "Uart_Cmd_Setting":
                           {
                               "Uart_Cmd_Setting": "success"
                           }
                       }

        if flag:
            dict_return["Uart_Cmd_Setting"]["Uart_Cmd_Setting"] = SUCCESS
        else:
            dict_return["Uart_Cmd_Setting"]["Uart_Cmd_Setting"] = FAIL

        return dict_return
