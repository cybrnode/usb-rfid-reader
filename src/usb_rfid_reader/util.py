import evdev
from .scancodes import SCAN_CODES


def decode_keydown_event(event):
    if event.type == evdev.ecodes.EV_KEY:
        data = evdev.categorize(event)  # Save the event temporarily to introspect it
        if data.keystate == 1:  # Down events only
            key_lookup = SCAN_CODES.get(data.scancode) or "UNKNOWN:{}".format(data.scancode)  # Lookup or return UNKNOWN:XX
            return key_lookup
