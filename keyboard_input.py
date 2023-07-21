import keyboard

default_values = [
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

key_map = {
    "w": (1, 1),    # the key w will affect index 1 by incrementing it
    "a": (2, 1),
    "s": (1, -1),
    "d": (2, -1)    # the key d will affect index 2 by decrementing it
}

# TODO idk im still reading the docs
