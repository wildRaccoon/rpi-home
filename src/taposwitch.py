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

        max_retries = 3
        retry_delay = 5  # секунди (збільшено з 2 до 5)
        initial_delay = 3  # затримка перед першою спробою
        
        # Затримка перед першою спробою (можливо пристрій потребує часу)
        if not hasattr(self, '_first_connect_attempted'):
            log(f"SmartSwitch: Очікування {initial_delay} секунд перед першою спробою підключення...")
            await asyncio.sleep(initial_delay)
            self._first_connect_attempted = True
        
        for attempt in range(max_retries):
            try:
                log(f"SmartSwitch: Handshake (спроба {attempt + 1}/{max_retries})")
                # Додаткова затримка перед кожним handshake
                if attempt > 0:
                    await asyncio.sleep(1)
                
                self.p110 = await self.client.p110(self.ipAddress)

                await self.getState()

                self.device_connected = True

                log("SmartSwitch: Connected - " + str(self.device_connected))
                log("SmartSwitch: State - " + str(self.device_on))

                if(self.device_connected and self.device_on):
                    await self.p110.off()
                    await self.getState()
                
                return  # Успішне підключення

            except Exception as error:
                error_msg = str(error)
                log(f"SmartSwitch: Помилка при спробі {attempt + 1}: {error_msg}")
                
                # Якщо це помилка Rust panic, додаємо більшу затримку
                if "rust future panicked" in error_msg.lower() or "panicked" in error_msg.lower():
                    log("SmartSwitch: Виявлено помилку Rust panic - можлива проблема з бібліотекою tapo")
                    if attempt < max_retries - 1:
                        log(f"SmartSwitch: Повторна спроба через {retry_delay} секунд...")
                        await asyncio.sleep(retry_delay)
                    else:
                        log("SmartSwitch: Всі спроби підключення не вдалися")
                        log("SmartSwitch: Рекомендація: перевірте версію бібліотеки tapo (pip3 install --upgrade tapo)")
                        self.device_connected = False
                else:
                    if attempt < max_retries - 1:
                        log(f"SmartSwitch: Повторна спроба через {retry_delay} секунд...")
                        await asyncio.sleep(retry_delay)
                    else:
                        log("SmartSwitch: Всі спроби підключення не вдалися")
                        self.device_connected = False

    def state(self):
        return self.device_on

    async def getState(self):
        if not self.device_connected or not hasattr(self, 'p110'):
            return False
            
        try:
            deviceInfo = await self.p110.get_device_info_json()
            
            self.device_on = deviceInfo['device_on']

            return self.device_on
            
        except BaseException as error:
            log("SmartSwitch: An exception occurred: " + str(error))
            self.device_connected = False
        
        return False

    async def turnOn(self):
        if not self.device_connected:
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
            if not self.device_connected:
                log("SmartSwitch: Неможливо увімкнути - пристрій не підключено")
            else:
                log("SmartSwitch: Connected - " + str(self.device_connected))

    async def turnOff(self):
        if not self.device_connected:
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
            if not self.device_connected:
                log("SmartSwitch: Неможливо вимкнути - пристрій не підключено")
            else:
                log("SmartSwitch: Connected - " + str(self.device_connected))