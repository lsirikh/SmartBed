import time
import sys

from api import ApiServer
from bt import *
import threading

from diskio import FileProcess
from uart import *

#UartData class create
uart = UartRead()
#uartWrite = UartWrite()

#bt_receiver thread start
# uart.init()
# uart.setAllThreadOn()
# uart.start()
#uart.init()

#BTReceive class create
bt_receiver = BTReceive()
#bt_receiver thread start
#bt_receiver.init()

# file = FileProcess()
# dict_list=file.data_load("data20201109.txt")
# api = ApiServer()
# r_dict_info=api.storedDataSend(dict_list)
# print("Sending Data Success:", r_dict_info['result'])
# print("Sending Data Failure:", r_dict_info['list_failed_data'].__len__())


#exit process
def close():

    #uartWrite.finish()
    if bt_receiver.finish() and uart.finish():
        print("all threads were finished.")
        sys.exit()


count=0
# Main thread
while True:
    try:
        # local variable will be initialized
        typeMessage = None

        # Check msg is None or not
        if bt_receiver.msg is not None:
            typeMessage = bt_receiver.msg.typeMessage

        # Each action will be taken
        if typeMessage == 1:
            pass
        elif typeMessage == 2:
            obj = bt_receiver.msg
            result = False

            pass
        elif typeMessage == 3:
            pass
        elif typeMessage == 4:
            pass
        elif typeMessage == 5:
            obj = bt_receiver.msg
            result = False
            result = uart.uartSet(obj.converter())
            bt_receiver.sendMessageTo(str(obj.response(result)))
        elif typeMessage == 6:
            pass
        elif typeMessage == 7:
            pass
        elif typeMessage == 8:
            obj = bt_receiver.msg
            result = False
            if obj.operation():
                result = uart.uartSet(SPEED01)
            else:
                result = uart.uartSet(SPEED00)
            bt_receiver.sendMessageTo(str(obj.response(result)))


    except Exception as ex:
        pass

    # if bt_receiver.op_code == 'stop':
    #     close()
    #     break
    # elif bt_receiver.op_code == 'on':
    #     print("uart set on")
    #     uart.op_code = bt_receiver.op_code
    #     result = uart.uartSet(bt_receiver.op_level)
    #     bt_receiver.sendMessageTo(str(bt_receiver.msg.response(result)))
    #
    # elif bt_receiver.op_code == 'off':
    #     print("uart set off")
    #     uart.op_code = bt_receiver.op_code
    #     uart.uartSet(bt_receiver.op_level)


    bt_receiver.op_code=''
    bt_receiver.msg=None
    uart.op_code = ''

    time.sleep(0.1)



