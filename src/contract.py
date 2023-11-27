import time

class Sensors():
    UpTs = 0
    Up = 0

    Down = 0
    DownTs = 0

    Stowe = 0
    StoweTS = 0

    Smoke = 0
    SmokeTs = 0

    SwithchOn = False

    def set_sensor(self, key, value):
        if(key == "011913c47b0c"):
            self.Up = value
            self.UpTs = time.time()

        elif(key == "011913a78132"):
            self.Down = value
            self.DownTs = time.time()

        elif(key == "011913a8f76d"):
            self.Stowe = value
            self.StoweTS = time.time()

        elif(key == "k"):
            self.Smoke = value
            self.SmokeTs = time.time()
    
    def switch(self):
        if(self.Up > 80 or self.Smoke > 52):
            self.SwithchOn = True
        else:
            self.SwithchOn = False
        return self.SwithchOn

