import time, adafruit_max31855, board, falcon, jsonpickle, drivers
from wsgiref.simple_server import make_server
from digitalio import DigitalInOut
from w1thermsensor import W1ThermSensor
from timeloop import Timeloop
from datetime import timedelta
from taposwitch import log, SmartSwitch
from contract import Sensors

temps = Sensors()
smartSwitch = SmartSwitch("ip", "user", "pass")

available_sensors = W1ThermSensor.get_available_sensors()
display = drivers.Lcd()

spi = board.SPI()
cs = DigitalInOut(board.D5)
k_sensor = adafruit_max31855.MAX31855(spi, cs)

tl = Timeloop()

state = "off"

@tl.job(interval=timedelta(seconds=1))
def read_temp_every_1s():
    for sensor in available_sensors:
        temps.set_sensor(str(sensor.id), float(sensor.get_temperature()))

    try:
        temps.set_sensor("k", float(k_sensor.temperature))
    except RuntimeError:
        log("Sensor k - error")

    try:
        if not smartSwitch.isConnected():
            state = "disct"
        elif smartSwitch.getState():
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
            smartSwitch.turnOn()
        elif (not temps.switch() and smartSwitch.state()):
            smartSwitch.turnOff()
    except BaseException as error:
        log("Unable to change switch status: " + str(error))
    
#web api

class TempResource(object):
    def on_get(self, req, resp):
        resp.body = jsonpickle.encode(temps)
        resp.status = falcon.HTTP_200

api = falcon.App()
temp_endpoint = TempResource()
api.add_route('/sensors',temp_endpoint)

if __name__ == '__main__':
    tl.start(block=False)
    with make_server('0.0.0.0', 8000, api) as httpd:
        log('Serving on port 8000...')

        # Serve until process is killed
        httpd.serve_forever()