import keyboard
import time
from threading import Thread

default_values = [
    "127",  # fill (either empties(-127) or fills(128) or stays still(0))
    "127",  # motor
    "127",  # bow_t
    "127",  # pitch
    "127",  # yaw
    "000",  # depth
    "127",  # angle
    "000",  # grabber
    "000",  # lights
]

current_values = default_values[:]

# index: which index does the letter affect
# sign: if the value should be incremented or decremented
# sleepTime: how much time of sleep
key_map = {
    "space": {"pressed": False, "index": 0, "sign": 1, "sleepTime": 0},  # empty syringes
    "shift": {"pressed": False, "index": 0, "sign": -1, "sleepTime": 0},  # fill syringes
    "w": {"pressed": False, "index": 1, "sign": 1, "sleepTime": 1/128},  # motor forward
    "s": {"pressed": False, "index": 1, "sign": -1, "sleepTime": 1/128},  # motor backward
    "a": {"pressed": False, "index": 2, "sign": 1, "sleepTime": 1/128},  # bow thruster left
    "d": {"pressed": False, "index": 2, "sign": -1, "sleepTime": 1/128}  # bow thruster right
}


def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)


class MyPrinter(Thread):
    def __init__(self):
        Thread.__init__(self, name="PrinterThread")

        self.active = False

    def run(self):
        self.active = True

        while self.active:
            print(current_values)
            time.sleep(1 / 5)

    def stop(self):
        self.active = False
        return False


class AccThread(Thread):
    def __init__(self, key, index, sign, sleepTime):
        Thread.__init__(self, name=f"Acc{index}{sign}Thread", daemon=True)

        self.active = False

        self.key = key
        self.sign = sign
        self.index = index
        self.sleepTime = sleepTime

    def run(self):
        self.active = True

        while self.active and key_map[self.key]["pressed"]:
            start = time.time()

            # current_values[self.index] += self.sign

            value = clamp(int(current_values[self.index]) + self.sign, 0, 255)
            value = str(value).zfill(3)
            current_values[self.index] = value

            # stop loop if it already reached its max or min
            if value == 255 or value == 0:
                self.active = False
                break

            # time.sleep(max((1. / ups) - (time.time() - start), 0))
            time.sleep(max(self.sleepTime - (time.time() - start), 0))


def onKeyUpdate(keyEvent):
    if keyEvent.event_type == keyboard.KEY_DOWN:
        for key, args in key_map.items():
            if keyEvent.name == key:
                if not key_map[key]["pressed"]:
                    key_map[key]["pressed"] = True
                    AccThread(key, args["index"], args["sign"], args["sleepTime"]).start()

    if keyEvent.event_type == keyboard.KEY_UP:
        for key, args in key_map.items():
            if keyEvent.name == key:
                key_map[key]["pressed"] = False
                current_values[args["index"]] = default_values[args["index"]]


if __name__ == '__main__':
    keyboard.hook(onKeyUpdate)

    printer = MyPrinter()
    printer.start()

    keyboard.wait("esc")

    printer.stop()
