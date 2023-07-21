import time
import serial
import keyboard
import threading

from threading import Thread
from enum import Enum

usb_port = 'COM5'
desired_ups = 60
active = True

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
	"000",  # bow_t
	"000",  # pitch
	"000",  # yaw
	"000",  # depth
	"000",  # angle
	"000",  # grabber
	"000",  # lights
]

key_actions = {
	"w": (1, 1),
	"a": (2, 1),
	"s": (1, -1),
	"d": (2, -1)
}


def clamp(value, min_value, max_value):
	return max(min(value, max_value), min_value)


def stopAll():
	global active

	print("\nEsc pressed... quitting")
	# maybe use daemon threads to quit them quickly

	active = False

	for thread in threading.enumerate():
		try:
			thread.stop()
		except AttributeError:
			# main thread
			pass


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


class InputMode(Enum):
	KEYBOARD = "keyboard"
	JOYSTICK = "joystick"
	XBOX = "xbox"
	PS = "ps"


class SerialMonitor(Thread):
	def __init__(self):
		Thread.__init__(self)

		self.active = False

	def run(self):
		self.active = True

		while self.active:
			if serial_port.inWaiting() > 0:
				arduino_output = serial_port.readline().decode().rstrip()
				print(f"{usb_port}: {arduino_output}")

	def stop(self):
		self.active = False
		return False


def main(mode=InputMode.KEYBOARD, ups=60, acceleration=5):
	"""
	The main function that does stuff

	:param mode:
	:param ups:
	:param acceleration:
		number of seconds that pass from being at 0 to 255 (linear?)

	:return:
	"""

	if mode.name not in InputMode.__members__:
		raise ValueError("Invalid input mode")

	print(f"Input mode: {mode.name}")

	while active:
		start = time.time()

		if mode == InputMode.KEYBOARD:
			# keyboard and mouse
			for key, arg in key_actions.items():
				if keyboard.is_pressed(key):
					index, sign = arg[0], arg[1]

					if index < 0 or index > 10:
						raise ValueError("Invalid index")

					# apply acceleration
					value = clamp(int(values_list[index]) + (acceleration * sign), 0, 255)
					# TODO for some stuff you dont want the same acceleration so i need custom acceleration for every value possibly (remake the system ;-;)

					# convert int to char[3]
					value = str(value).zfill(3)

					values_list[index] = value

		elif mode == InputMode.JOYSTICK:
			# joystick
			pass

		elif mode == InputMode.XBOX:
			# xbox controller
			pass

		elif mode == InputMode.PS:
			# ps controller
			pass

		print(values_list)

		# ======================================================== #
		# =================| YOU SHALL NOT PASS |================= #
		# ======================================================== #

		if keyboard.is_pressed("esc"):
			stopAll()

		time.sleep(max((1. / ups) - (time.time() - start), 0))


if __name__ == '__main__':
	serialMonitor = SerialMonitor()

	# serialMonitor.start()
	main(ups=10)
