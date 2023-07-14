import time
import serial
import threading

from threading import Thread
from pynput import keyboard


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


def onKeyPress(key):
	try:
		key_char = key.char

	except AttributeError:
		# special keys
		pass

	if key == keyboard.Key.esc:  # Replace with the desired key
		print("Esc pressed... quitting")

		for thread in threading.enumerate():
			try:
				thread.stop()
			except AttributeError:
				# main thread
				pass


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


class Sender(Thread):
	def __init__(self, ups=60):
		Thread.__init__(self)

		self.active = False
		self.ups = ups

	def run(self):
		self.active = True

		while self.active:
			start = time.time()

			# TODO do stuff here
			print("working")

			time.sleep(max((1. / self.ups) - (time.time() - start), 0))

	def stop(self):
		self.active = False


if __name__ == '__main__':
	listener = KeyListener()
	serialMonitor = SerialMonitor()
	sender = Sender(1)

	sender.start()
	listener.start()
