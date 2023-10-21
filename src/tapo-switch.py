from PyP100 import PyP110
from datetime import datetime

def log(message):
    now = datetime.now()
    print(now.strftime("%d/%m/%Y %H:%M:%S ") + str(message))

class SmartSwitch():
    def __init__ (self, ipAddress, email, password):
        self.device_on = False
        self.device_connected = False
        self.p110 = PyP110.P110(ipAddress, email, password)

        try:
            log("SmartSwitch: Handshake")
            self.p110.handshake()

            log("SmartSwitch: Login")
            self.p110.login()

            self.getState()

            self.device_connected = True

            log("SmartSwitch: Connected - " + str(self.device_connected))
            log("SmartSwitch: State - " + str(self.device_on))

            if(self.device_connected and self.device_on):
                self.p110.turnOff()
                self.getState()

        except BaseException as error:
            log("SmartSwitch: An exception occurred: " + str(error))
            self.device_connected = False

    def isConnected(self):
        return self.device_connected

    def getState(self):
        try:
            deviceInfo = self.p110.getDeviceInfo()
            
            self.device_on = deviceInfo["result"]["device_on"]

            log("SmartSwitch: State - " + str(self.device_on))

            return self.device_on
            
        except BaseException as error:
            log("SmartSwitch: An exception occurred: " + str(error))
        
        return False

    def turnOn(self):
        if (self.device_connected and not self.device_on):
            try:
                self.p110.turnOn()
                self.getState()
            except BaseException as error:
                log("SmartSwitch: An exception occurred: " + str(error))

        else:
            log("SmartSwitch: Connected - " + str(self.device_connected))

    def turnOff(self):
        if (self.device_connected and self.device_on):
            try:
                self.p110.turnOff()
                self.getState()
            except BaseException as error:
                log("SmartSwitch: An exception occurred: " + str(error))

        else:
            log("SmartSwitch: Connected - " + self.device_connected)