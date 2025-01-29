import time
import logging
import threading
import pydirectinput
from .pointer import Pointer
from pymem.process import module_from_name
from pymem.exception import WinAPIError


class DINPUT:

    _lock = threading.Lock()
    _pressed_keys = []
    _captured = False

    def __init__(self, process, window_input_pointer=None, key_input_pointer=None, dinput_keys=None, **kwargs):
        self.process = process
        self.window_pointer = Pointer(self.process, window_input_pointer, "window_input_pointer")
        self.key_input_pointer = Pointer(self.process, key_input_pointer, "key_input_pointer") \
            if key_input_pointer else None

        self.dinput_base = module_from_name(self.process.process_handle, "DINPUT8.dll").lpBaseOfDll
        self.dinput_keys = dinput_keys
        self.logger = logging.getLogger("logger.{}".format(self.__class__.__name__))
        self.update_dinput_keys_offset()

    def update_dinput_keys_offset(self, key="z"):
        """
        Update the memory offset for the `dinput8.dll` module, which may vary across different computers.
        """
        self.logger.info("Start searching for the offset for dinput keys, ensure the game window is in focus")
        key_address = self.dinput_base + self.dinput_keys[key]["offset"]
        pydirectinput.keyDown(key)
        time.sleep(0.3)
        for i in range(10000):
            try:
                if self.process.read_int(key_address + 0x1 * i) == self.dinput_keys[key]["key_down"]:
                    self.logger.info("Found offset for dinput: {}".format(hex(0x1 * i)))
                    offset = 0x1 * i
                    break
                if self.process.read_int(key_address + 0x1 * -i) == self.dinput_keys[key]["key_down"]:
                    self.logger.info("Found offset for dinput: {}".format(hex(0x1 * -i)))
                    offset = 0x1 * -i
                    break
            except WinAPIError:
                pass
        else:
            raise Exception("Not found offset for dinput!!")
        pydirectinput.keyUp(key)

        for key in self.dinput_keys.keys():
            self.dinput_keys[key]["offset"] += offset

    def capture_dinput(self):
        dinput_captured = self.window_pointer.get_address_value_for_offset_name("capture_input")
        if dinput_captured != self.window_pointer.get_value_for_offset_name("capture_input", "capture"):
            self.window_pointer.set_defined_address_value_for_offset_name("capture_window", "capture")
            time.sleep(0.02)
            self.window_pointer.set_defined_address_value_for_offset_name("capture_input", "capture")
            DINPUT._captured = True
        return DINPUT._captured

    def uncapture_dinput(self):
        key_input = self.key_input_pointer.get_address_value_for_offset_name("capture_key_input")
        if (key_input == self.key_input_pointer.get_value_for_offset_name("capture_key_input", "deactivate")
                and len(self._pressed_keys) == 0 and DINPUT._captured is True):
            self.window_pointer.set_defined_address_value_for_offset_name("capture_window", "uncapture")
            DINPUT._captured = False
        return DINPUT._captured

    def press_key(self, key):
        if key in self._pressed_keys:
            return
        with DINPUT._lock:
            self.capture_dinput()
            key_address = self.dinput_base + self.dinput_keys[key]["offset"]
            actual_value = self.process.read_int(key_address)
            if actual_value < 0:
                self.process.write_int(key_address, 0)
                actual_value = 0
            self.process.write_int(key_address, actual_value + self.dinput_keys[key]["key_down"])
            self._pressed_keys.append(key)
            time.sleep(0.01)

    def release_key(self, key):
        key_address = self.dinput_base + self.dinput_keys[key]["offset"]
        actual_value = self.process.read_int(key_address)
        key_value = self.dinput_keys[key]["key_down"]
        with DINPUT._lock:
            if abs(actual_value) - abs(key_value) >= 0:
                self.process.write_int(key_address, actual_value - key_value)
                self._pressed_keys.remove(key)
                time.sleep(0.02)
                self.uncapture_dinput()

    def press_and_release_keys(self, keys):
        keys = keys if isinstance(keys, list) else [keys]
        for key in keys:
            self.press_key(key)
        time.sleep(0.01)
        for key in keys:
            self.release_key(key)

    def get_available_keys(self):
        return list(self.dinput_keys.keys())

    def __del__(self):
        if not self.key_input_pointer:
            return
        key_input = self.key_input_pointer.get_address_value_for_offset_name("capture_key_input")
        self.logger.info("Uncapture dinput: {}".format(key_input))
        if key_input == self.key_input_pointer.get_value_for_offset_name("capture_key_input", "deactivate"):
            self.window_pointer.set_defined_address_value_for_offset_name("capture_window", "uncapture")
