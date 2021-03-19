import threading
from typing import Callable, List, Tuple
from .util import decode_keydown_event
from evdev import InputDevice

from selectors import DefaultSelector, EVENT_READ


import queue


class USBRFIDReader:
    def __init__(self, device_filenames=[]):

        self.scanner_thread: threading.Thread = None
        self.devices: List[InputDevice] = list(map(InputDevice, device_filenames))

        self._init_queue()
        self._register_selector()

    def _register_selector(self):
        self._selector = DefaultSelector()
        for device in self.devices:
            self._selector.register(device, EVENT_READ)

    def _init_queue(self):
        self.scanned_card_queue = queue.Queue()
        self._last_scanned = dict()

        for device in self.devices:
            self._last_scanned[device.path] = ""

    def _start(self):
        while True:
            for device in self.get_event_ready_devices():
                self._process_device_event(device)

    def _process_device_event(self, device):
        for event in device.read():
            key_lookup = decode_keydown_event(event)
            if not key_lookup:
                continue
            if key_lookup == "CRLF":
                self.scanned_card_queue.put([device.path, self._last_scanned[device.path]])
                self._last_scanned[device.path] = ""
                break
            else:
                self._last_scanned[device.path] += key_lookup

    def get_event_ready_devices(self):
        # Note: Taken from https://python-evdev.readthedocs.io/en/latest/tutorial.html#reading-events-from-multiple-devices-using-selectors
        for key, _ in self._selector.select():
            # This blocks until any file in self._selector has EVENT_READ status ( until input available )
            device: InputDevice = key.fileobj
            yield device

    def start(self):

        if self.scanner_thread:
            raise Exception("scanner already running")

        self.scanner_thread = threading.Thread(target=self._start)
        self.scanner_thread.start()

    def register_callback(self, callback: Callable[[str, str], None]):
        self.callback = callback

    def process_scans(self):
        if not self.scanner_thread:
            raise Exception("scanner not running, did you forget to call .start()?")  # TODO: make proper custom exception classes

        if not self.callback:
            raise Exception("No Callback registered, did you call .register_callback()")  # TODO: make proper custom exception classes

        while True:
            # TODO: Think if this is a problem, because this will block all other callbacks if a callback takes too long, or raises Exception
            try:
                device_path, scanned_id = self.scanned_card_queue.get(block=False)
            except queue.Empty:
                continue

            self.callback(device_path, scanned_id)
            self.scanned_card_queue.task_done()

    def is_card_available(self):
        return self.scanned_card_queue.empty()

    def get_last_scanned_card(self) -> Tuple[str, str]:
        """Will return None if no card is available, otherwise returns a Tuple[device_path, scanned_str]"""
        try:
            return self.scanned_card_queue.get(block=False)
        except queue.Empty:
            return None


if __name__ == "__main__":

    _devices = [
        "/dev/input/by-path/pci-0000:00:14.0-usb-0:1:1.0-event-kbd",
        "/dev/input/by-path/pci-0000:00:14.0-usb-0:3:1.0-event-kbd",
    ]
    reader = USBRFIDReader(_devices)
    reader.start()

    reader.register_callback(print)
    reader.process_scans()
