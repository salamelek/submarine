import time
import serial
import keyboard
import threading

from threading import Thread
from input_options import InputMode

usb_port = 'COM5'
baud_rate = 115200
desired_ups = 60
active = True
quitCommand = "esc"
mode = InputMode.KEYBOARD
global_acc_factor = 2

# Open the serial port
try:
	serial_port = serial.Serial(usb_port, baud_rate)
	serial_port.flushInput()
	print(f"Connected to arduino on port {usb_port}!\n")
except serial.serialutil.SerialException:
	print(f"No arduino board detected on {usb_port}!\n")

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
# step: if the value should be incremented or decremented (and by how much)
# sleepTime: how much time of sleep
# inverseKey: to know if the key assigned to the inverse function is pressed or not
key_map = {
	"space": {"pressed": False, "hold": False, "index": 0, "step": 1, "sleepTime": 0, "inverseKey": "shift"},  # empty syringes
	"shift": {"pressed": False, "hold": False, "index": 0, "step": -1, "sleepTime": 0, "inverseKey": "space"},  # fill syringes
	"w": {"pressed": False, "hold": False, "index": 1, "step": 1, "sleepTime": 1 / 128, "inverseKey": "s"},  # motor forward
	"s": {"pressed": False, "hold": False, "index": 1, "step": -1, "sleepTime": 1 / 128, "inverseKey": "w"},  # motor backward
	"a": {"pressed": False, "hold": False, "index": 2, "step": 1, "sleepTime": 1 / 128, "inverseKey": "d"},  # bow thruster left
	"d": {"pressed": False, "hold": False, "index": 2, "step": -1, "sleepTime": 1 / 128, "inverseKey": "a"},  # bow thruster right
	"up": {"pressed": False, "hold": False, "index": 3, "step": -1, "sleepTime": 1 / 128, "inverseKey": "down"},  # pitch down
	"down": {"pressed": False, "hold": False, "index": 3, "step": 1, "sleepTime": 1 / 128, "inverseKey": "up"},  # pitch down
	"right": {"pressed": False, "hold": False, "index": 4, "step": 1, "sleepTime": 1 / 128, "inverseKey": "left"},  # yaw right
	"left": {"pressed": False, "hold": False, "index": 4, "step": -1, "sleepTime": 1 / 128, "inverseKey": "right"}  # yaw right
}


def clamp(value, min_value, max_value):
	return max(min(value, max_value), min_value)


def stopAll():
	global active

	print("\nstopAll() called... quitting")
	# maybe use daemon threads to quit them quickly

	active = False

	for thread in threading.enumerate():
		try:
			thread.stop()
		except AttributeError:
			# main thread
			pass


class SerialSender(Thread):
	"""
	This class constantly streams data to the arduino via serial
	The only parameter is ups, and it is the frequency of data sends
	"""

	def __init__(self, ups=60):
		Thread.__init__(self, name="SerialSenderThread")

		self.ups = ups
		self.active = False

	def run(self):
		self.active = True
		print(f"Thread '{self.name}' starting")

		while self.active:
			start = time.time()

			# to modify data, modify values_list
			data = (''.join(str(value) for value in current_values)) + "\n"
			if len(data) != 28:
				stopAll()
				raise ValueError(f"Data len is not 28! It's {len(data)}")

			try:
				serial_port.write(data.encode('utf-8'))
			except NameError:
				self.active = False
				print("Serial sender quitting")

			time.sleep(max((1. / self.ups) - (time.time() - start), 0))

	def stop(self):
		print(f"Thread '{self.name}' stopping")
		self.active = False
		return False


class SerialMonitor(Thread):
	def __init__(self):
		Thread.__init__(self, name="SerialMonitorThread")

		self.active = False

	def run(self):
		self.active = True
		print(f"Thread '{self.name}' starting")

		try:
			serial_port.name
		except NameError:
			self.active = False
			print("Serial sender quitting")

		while self.active:
			if serial_port.inWaiting() > 0:
				try:
					arduino_output = serial_port.readline().decode().rstrip()
				except UnicodeDecodeError:
					arduino_output = "?"
				print(f"{usb_port}: {arduino_output}")

	def stop(self):
		print(f"Thread '{self.name}' stopping")
		self.active = False
		return False


class AccThread(Thread):
	def __init__(self, key, index, step, sleepTime):
		Thread.__init__(self, name=f"Acc{index}{step}Thread", daemon=True)

		self.active = False

		self.key = key
		self.step = step
		self.index = index
		self.sleepTime = sleepTime

	def run(self):
		self.active = True

		while self.active and key_map[self.key]["pressed"]:
			start = time.time()

			value = clamp(int(current_values[self.index]) + self.step * global_acc_factor, 0, 255)

			# filter out instant accelerations
			if self.sleepTime == 0:
				value = max(0, (self.step * 255))

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
	def __init__(self, key, index, targetValue, sleepTime, step):
		Thread.__init__(self)

		self.active = False

		self.index = index
		self.step = step
		self.targetValue = targetValue
		self.sleepTime = sleepTime
		self.key = key
		self.inverseKey = key_map[self.key]["inverseKey"]
		self.step = step

	def run(self):
		self.active = True

		# active just to be able to stop it when needed, not on key or inverse key pressed, so it doesn't interfere
		while self.active and not key_map[self.key]["pressed"] and not key_map[self.inverseKey]["pressed"]:
			start = time.time()

			# filter out instant accelerations
			if self.sleepTime == 0:
				current_values[self.index] = str(self.targetValue).zfill(3)

			if current_values[self.index] > self.targetValue:
				value = clamp(int(current_values[self.index]) - global_acc_factor * abs(self.step), 0, 255)

			elif current_values[self.index] < self.targetValue:
				value = clamp(int(current_values[self.index]) + global_acc_factor * abs(self.step), 0, 255)

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
					AccThread(key, args["index"], args["step"], args["sleepTime"]).start()

	if keyEvent.event_type == keyboard.KEY_UP:
		for key, args in key_map.items():
			if keyEvent.name == key:
				key_map[key]["pressed"] = False
				if not key_map[key]["hold"]:
					AccToValue(key, args["index"], default_values[args["index"]], args["sleepTime"], args["step"]).start()


if __name__ == '__main__':
	if mode == InputMode.KEYBOARD:
		keyboard.hook(onKeyUpdate)

	elif mode == InputMode.JOYSTICK:
		# joystick
		pass

	elif mode == InputMode.XBOX:
		# xbox controller
		pass

	elif mode == InputMode.PS:
		# ps controller
		pass

	else:
		raise ValueError("ffs choose a fking option")

	sm = SerialMonitor()
	ss = SerialSender(desired_ups)

	sm.start()
	ss.start()

	try:
		keyboard.wait(quitCommand)
	except KeyboardInterrupt:
		pass

	stopAll()

	print("\ngoodbye")
