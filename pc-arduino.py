# Program that reads serial monitor and sends chars to the arduino via serial

from threading import Thread
import serial
from pynput import keyboard
from time import sleep

# Open the serial port
serial_port = serial.Serial('COM5', 9600)
serial_port.flushInput()


def onKeyPress(key):
    try:
        key_char = key.char
        sendSerial(key_char)

    except AttributeError:
        pass

    if key == keyboard.Key.esc:  # Replace with the desired key
        print("Esc pressed... quitting")
        myKey.stop()
        MyMonitor.stop()


class SerialMonitor(Thread):
    def __init__(self):
        Thread.__init__(self)

        self.active = False

    def run(self):
        self.active = True

        while self.active:
            if serial_port.inWaiting() > 0:
                arduino_output = serial_port.readline().decode().rstrip()
                print("Arduino:", arduino_output)

    def stop(self):
        self.active = False
        return False


def on_keyboard_press(key):
    print(f'Keyboard key {key} pressed')


class KeyListener(Thread):
    def __init__(self):
        Thread.__init__(self)

        self.active = False
        self.keyboard_listener = keyboard.Listener(on_press=onKeyPress)

    def run(self):
        self.active = True
        self.keyboard_listener.start()

        while self.active:
            sleep(1)

    def stop(self):
        self.active = False
        return False


def sendSerial(data):
    serial_port.write(data.encode())


MyMonitor = SerialMonitor()
MyMonitor.start()
myKey = KeyListener()
myKey.start()
