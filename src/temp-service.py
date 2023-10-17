import time, adafruit_max31855, board, falcon, jsonpickle, drivers
from wsgiref.simple_server import make_server
from digitalio import DigitalInOut
from w1thermsensor import W1ThermSensor
from timeloop import Timeloop
from datetime import timedelta


key_mapping = {
    "011913a8f76d": "Up:",
    "011913a78132": "Down:",
    "011913c47b0c": "Kotel:",
    "k":"Dim:"
}

temps = {}

available_sensors = W1ThermSensor.get_available_sensors()
display = drivers.Lcd()

spi = board.SPI()
cs = DigitalInOut(board.D5)
k_sensor = adafruit_max31855.MAX31855(spi, cs)

tl = Timeloop()

@tl.job(interval=timedelta(seconds=1))
def read_temp_every_1s():
    i = 1
    for sensor in available_sensors:
        temps[sensor.id] = TempValue(sensor.id, sensor.get_temperature())
        display.lcd_display_string(key_mapping[sensor.id] + str(temps[sensor.id].value)+ "    ", i)
        i = i + 1
        
    try:
        temps["k"] = TempValue("k", k_sensor.temperature)
        display.lcd_display_string(key_mapping["k"] + str(temps["k"].value) + "    ", i)
    except RuntimeError:
        print("Sensor k - error")


class TempValue(object):
    value = 0
    key = ""
    ts = 0

    def __init__(self, k, v):
        self.key = k
        self.value = v
        self.ts = time.time()
    

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
        print('Serving on port 8000...')

        # Serve until process is killed
        httpd.serve_forever()