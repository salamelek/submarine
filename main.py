import time
import serial

from threading import Thread
from pynput import keyboard

# Open the serial port
serial_port = serial.Serial('COM5', 9600)
serial_port.flushInput()


# default values
values_list = [
	"000",  # fullness
	"000",  # motor
	"000",  # bow_t_1
	"000",  # bow_t_2
	"000",  # pitch
	"000",  # yaw
	"000",  # depth
	"000",  # angle
	"000",  # grabber
	"000",  # lights
]


def onKeyPress(key):
	try:
		key_char = key.char
		# TODO change values in values_list :')

	except AttributeError:
		# special keys
		pass

	if key == keyboard.Key.esc:  # Replace with the desired key
		print("Esc pressed... quitting")
		# TODO exit all threads


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

	def stop(self):
		self.active = False
		return False


def sendSerial():
	# to modify data, modify the values_list

	"""
	Example data:
	000255000000000000000000000255

	:return:
	"""
	data = ','.join(str(value) for value in values_list)

	if len(data) != 30:
		raise "Data len is not 30!"

	serial_port.write(data.encode('utf-8'))



