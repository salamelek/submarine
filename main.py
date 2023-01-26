import pyrf24
import serial
import keyboard

usbPort = "COM3"
baudRate = 9600


# Configure the serial connection to the RF24 module
ser = serial.Serial(usbPort, baudRate)
radio = pyrf24.RF24(ser)

# Set the radio parameters
radio.begin()
radio.setChannel(0x60)                      # 0x60 is 96 in hex
radio.setDataRate(pyrf24.RF24_250KBPS)      # data rate
radio.setPALevel(pyrf24.RF24_PA_LOW)        # set to RF24_PA_MAX for max range

# Set the radio addresses
addr = [0xF0, 0xF0, 0xF0, 0xF0, 0xE1]
radio.openWritingPipe(addr)

# Send keyboard input over the radio
while True:
    if keyboard.is_pressed('w'):
        radio.write('w')
