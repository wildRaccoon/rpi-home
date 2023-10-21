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

        self.connect()


    def isConnected(self):
        return self.device_connected

    def connect(self):
        if(self.device_connected):
            return

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

    def state(self):
        return self.device_on

    def getState(self):
        try:
            deviceInfo = self.p110.getDeviceInfo()
            
            self.device_on = deviceInfo["result"]["device_on"]

            return self.device_on
            
        except BaseException as error:
            log("SmartSwitch: An exception occurred: " + str(error))
            self.device_connected = False
        
        return False

    def turnOn(self):
        self.connect()

        if (self.device_connected and not self.device_on):
            try:
                self.p110.turnOn()
                self.getState()
                log("SmartSwitch: State - " + str(self.device_on))
            except BaseException as error:
                log("SmartSwitch: An exception occurred: " + str(error))
                self.device_connected = False

        else:
            log("SmartSwitch: Connected - " + str(self.device_connected))

    def turnOff(self):
        self.connect()

        if (self.device_connected and self.device_on):
            try:
                self.p110.turnOff()
                self.getState()
                log("SmartSwitch: State - " + str(self.device_on))
            except BaseException as error:
                log("SmartSwitch: An exception occurred: " + str(error))
                self.device_connected = False

        else:
            log("SmartSwitch: Connected - " + self.device_connected)