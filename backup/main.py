import time
import sys

from bt import BTSetup, BTReceive
import threading

from uart import UartRead

#UartData class create
uartRead = UartRead()
#uartWrite = UartWrite()

#bt_receiver thread start
uartRead.init()
uartRead.setAllThreadOn()
uartRead.start()

#BTReceive class create
bt_receiver = BTReceive()
#bt_receiver thread start
bt_receiver.setThreadOn()
bt_receiver.start()



#exit process
def close():

    bt_receiver.finish()
    #uartWrite.finish()
    uartRead.finish()
    if bt_receiver.is_alive():
        bt_receiver.join(timeout=3)
    if uartRead.is_alive():
        uartRead.join(timeout=3)

    sys.exit()


while True:
    if bt_receiver.op_code == 'start':
        uartRead.op_code = bt_receiver.op_code
        uartRead.uartSet()
    elif bt_receiver.op_code == 'end':
        uartRead.op_code = bt_receiver.op_code
        uartRead.uartSet()
    if bt_receiver.op_code == 'break':
        close()
        break
    time.sleep(0.1)

    #bt_receiver.op_code = None

    #uart.op_code = bt_receiver.op_code


