import asyncio

from tapo import ApiClient
from datetime import datetime

def log(message):
    now = datetime.now()
    print(now.strftime("%d/%m/%Y %H:%M:%S ") + str(message))

class SmartSwitch():
    def __init__ (self, ipAddress, email, password):
        self.device_on = False
        self.device_connected = False
        self.ipAddress = ipAddress
        self.client = ApiClient(email, password)

    def isConnected(self):
        return self.device_connected

    async def connect(self):
        if(self.device_connected):
            return

        try:
            log("SmartSwitch: Handshake")
            self.p110 = await self.client.p110(self.ipAddress)

            await self.getState()

            self.device_connected = True

            log("SmartSwitch: Connected - " + str(self.device_connected))
            log("SmartSwitch: State - " + str(self.device_on))

            if(self.device_connected and self.device_on):
                await self.p110.off()
                await self.getState()

        except BaseException as error:
            log("SmartSwitch: An exception occurred: " + str(error))
            self.device_connected = False

    def state(self):
        return self.device_on

    async def getState(self):
        try:
            deviceInfo = await self.p110.get_device_info_json()
            
            self.device_on = deviceInfo['device_on']

            return self.device_on
            
        except BaseException as error:
            log("SmartSwitch: An exception occurred: " + str(error))
            self.device_connected = False
        
        return False

    async def turnOn(self):
        await self.connect()

        if (self.device_connected and not self.device_on):
            try:
                await self.p110.on()
                await self.getState()
                log("SmartSwitch: State - " + str(self.device_on))
            except BaseException as error:
                log("SmartSwitch: An exception occurred: " + str(error))
                self.device_connected = False

        else:
            log("SmartSwitch: Connected - " + str(self.device_connected))

    async def turnOff(self):
        await self.connect()

        if (self.device_connected and self.device_on):
            try:
                await self.p110.off()
                await self.getState()
                log("SmartSwitch: State - " + str(self.device_on))
            except BaseException as error:
                log("SmartSwitch: An exception occurred: " + str(error))
                self.device_connected = False

        else:
            log("SmartSwitch: Connected - " + self.device_connected)