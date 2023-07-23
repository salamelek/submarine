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
# inverseKey: to know if the key assigned to the inverse function is pressed or not
key_map = {
    "space": {"pressed": False, "index": 0, "sign": 1, "sleepTime": 0, "inverseKey": "shift"},  # empty syringes
    "shift": {"pressed": False, "index": 0, "sign": -1, "sleepTime": 0, "inverseKey": "space"},  # fill syringes
    "w": {"pressed": False, "index": 1, "sign": 1, "sleepTime": 1 / 128, "inverseKey": "s"},  # motor forward
    "s": {"pressed": False, "index": 1, "sign": -1, "sleepTime": 1 / 128, "inverseKey": "w"},  # motor backward
    "a": {"pressed": False, "index": 2, "sign": 1, "sleepTime": 1 / 128, "inverseKey": "d"},  # bow thruster left
    "d": {"pressed": False, "index": 2, "sign": -1, "sleepTime": 1 / 128, "inverseKey": "a"}  # bow thruster right
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
            time.sleep(1 / 60)

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

            value = clamp(int(current_values[self.index]) + self.sign, 0, 255)

            # filter out instant accelerations
            if self.sleepTime == 0:
                value = max(0, (self.sign * 255))

            current_values[self.index] = str(value).zfill(3)

            # stop loop if it already reached its max or min
            if value == 255 or value == 0:
                self.active = False
                break

            time.sleep(max(self.sleepTime - (time.time() - start), 0))

    def stop(self):
        self.active = False
        return False


class AccToValue(Thread):
    def __init__(self, key, index, targetValue, sleepTime):
        Thread.__init__(self)

        self.active = False

        self.index = index
        self.targetValue = targetValue
        self.sleepTime = sleepTime
        self.key = key
        self.inverseKey = key_map[self.key]["inverseKey"]

    def run(self):
        self.active = True

        # active just to be able to stop it when needed, not on key or inverse key pressed, so it doesn't interfere
        while self.active and not key_map[self.key]["pressed"] and not key_map[self.inverseKey]["pressed"]:
            start = time.time()

            # filter out instant accelerations
            if self.sleepTime == 0:
                current_values[self.index] = str(self.targetValue).zfill(3)

            if current_values[self.index] > self.targetValue:
                value = clamp(int(current_values[self.index]) - 1, 0, 255)

            elif current_values[self.index] < self.targetValue:
                value = clamp(int(current_values[self.index]) + 1, 0, 255)

            else:
                self.active = False
                break

            current_values[self.index] = str(value).zfill(3)

            time.sleep(max(self.sleepTime - (time.time() - start), 0))

    def stop(self):
        self.active = False
        return False


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
                AccToValue(key, args["index"], default_values[args["index"]], args["sleepTime"]).start()


if __name__ == '__main__':
    keyboard.hook(onKeyUpdate)

    printer = MyPrinter()
    printer.start()

    keyboard.wait("esc")

    printer.stop()
