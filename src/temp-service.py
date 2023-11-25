import adafruit_max31855, board, jsonpickle, drivers, os, asyncio
from aiohttp import web
from wsgiref.simple_server import make_server
from digitalio import DigitalInOut
from w1thermsensor import W1ThermSensor
from taposwitch import log, SmartSwitch
from contract import Sensors

temps = Sensors()
smartSwitch = SmartSwitch(os.getenv("TAPO_IP_ADDRESS"), os.getenv("TAPO_USERNAME"), os.getenv("TAPO_PASSWORD"))

available_sensors = W1ThermSensor.get_available_sensors()
display = drivers.Lcd()

spi = board.SPI()
cs = DigitalInOut(board.D5)
k_sensor = adafruit_max31855.MAX31855(spi, cs)

state = "off"

async def read_temp_every_1s():
    while True:
        #log(jsonpickle.encode(temps))

        for sensor in available_sensors:
            temps.set_sensor(str(sensor.id), float(sensor.get_temperature()))

        try:
            temps.set_sensor("k", float(k_sensor.temperature))
        except RuntimeError:
            log("Sensor k - error")

        try:
            if not smartSwitch.isConnected():
                state = "disct"
            elif await smartSwitch.getState():
                state = "on"
            else:
                state = "off"
        except BaseException as error:
            log("Unable to write switch status on display: " + str(error))
        
        try:
            display.lcd_display_string(f'Smoke:{temps.Smoke:2.2f} {state}', 1)
            display.lcd_display_string(f'Stowe:{temps.Stowe:2.2f}', 2)
            display.lcd_display_string(f'   Up:{temps.Up:2.2f}', 3)
            display.lcd_display_string(f' Down:{temps.Down:2.2f}', 4)
        except BaseException as error:
            log("Unable to write on display: " + str(error))

        try:
            if(temps.switch() and not smartSwitch.state()):
                await smartSwitch.turnOn()
            elif (not temps.switch() and smartSwitch.state()):
                await smartSwitch.turnOff()
        except BaseException as error:
            log("Unable to change switch status: " + str(error))

        await asyncio.sleep(1)
    
#web api

async def handle(request):
    body = jsonpickle.encode(temps)
    return web.json_response(text=body)


app = web.Application()
app.add_routes([web.get('/', handle),
                web.get('/sensors', handle)])

async def runner():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8000)
    await site.start()


async def main():
    log('Run app loop....')
    asyncio.create_task(read_temp_every_1s())

    log('Starting Server....')
    await runner()

if __name__ == "__main__":
    asyncio.run(main())