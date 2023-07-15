import time
import serial
import threading

from threading import Thread
from pynput import keyboard
from enum import Enum

usb_port = 'COM5'
desired_ups = 60

# Open the serial port
try:
	serial_port = serial.Serial(usb_port, 9600)
	serial_port.flushInput()
except serial.serialutil.SerialException:
	print(f"No arduino board detected on {usb_port}!")

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


class InputMode(Enum):
	KEYBOARD = "keyboard"
	JOYSTICK = "joystick"
	XBOX = "xbox"
	PS = "ps"


def stopAll():
	print("Esc pressed... quitting")
	# maybe use daemon threads to quit them quickly

	for thread in threading.enumerate():
		try:
			thread.stop()
		except AttributeError:
			# main thread
			pass


def setValue(index, value):
	if index < 0 or index > 10:
		raise ValueError("Invalid index")

	if value < 0 or value > 255:
		raise ValueError("Invalid value")

	values_list[index] = value


def onKeyPress(key):
	try:
		key_char = key.char

	except AttributeError:
		# special keys
		pass

	if key == keyboard.Key.esc:  # Replace with the desired key
		stopAll()


def sendSerial():
	"""
	Example data:
	000255000000000000000000255000

	:return:
	"""

	# to modify data, modify the values_list
	data = ','.join(str(value) for value in values_list)

	if len(data) != 30:
		raise "Data len is not 30!"

	serial_port.write(data.encode('utf-8'))


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


class Sender(Thread):
	def __init__(self, mode, ups=60, smoothing=0):
		Thread.__init__(self)

		if mode.name not in InputMode.__members__:
			raise ValueError("Invalid input mode")

		self.active = False
		self.mode = mode
		self.ups = ups
		self.smoothing = smoothing

	def run(self):
		self.active = True
		print(f"Input mode: {self.mode.name}")

		while self.active:
			start = time.time()

			if self.mode == InputMode.KEYBOARD:
				# keyboard and mouse
				pass

			elif self.mode == InputMode.JOYSTICK:
				# joystick
				pass

			elif self.mode == InputMode.XBOX:
				# xbox controller
				pass

			elif self.mode == InputMode.PS:
				# ps controller
				pass

			time.sleep(max((1. / self.ups) - (time.time() - start), 0))

	def stop(self):
		self.active = False


if __name__ == '__main__':
	serialMonitor = SerialMonitor()
	sender = Sender(mode=InputMode.KEYBOARD, ups=60)

	sender.start()
