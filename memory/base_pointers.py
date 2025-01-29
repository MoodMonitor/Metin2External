import threading
import time
import win32gui
import win32process
import pymem
import logging
import psutil
from memory.utilities import get_address_from_sig


class BasePointers:

    LOGGER = logging.getLogger("logger.{}".format("BasePointers"))
    _instances = {}

    def __new__(cls, process=None, window_hwnd=None, *args, **kwargs):
        if not process:
            process, window_hwnd = BasePointers.get_window_handle_and_pid()
        pid = process.process_id
        if pid not in cls._instances:
            new_instance = super().__new__(cls)
            new_instance.process = process
            new_instance.process_name = psutil.Process(pid).name()
            new_instance.window_hwnd = window_hwnd
            BasePointers.LOGGER.info("Created instance for process pid: {}, name: {}".format(pid,
                                                                                             new_instance.process_name))
            cls._instances[pid] = new_instance
        return cls._instances[pid]

    def initialize_pointers(self, pointers):
        BasePointers.LOGGER.info("Start initializing pointers for {}".format(self.process_name))
        threads = [threading.Thread(target=self.initialize_pointer, args=(pointer_name, pointer_details,))
                   for pointer_name, pointer_details in pointers.items()]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def initialize_pointer(self, pointer_name, pointer_details):
        pointer = self.get_variable(pointer_name)
        if pointer is None:
            pointer = get_address_from_sig(pointer_details["sig"], self.process, pointer_details["extra"],
                                           pointer_details["offset"])
            BasePointers.LOGGER.info("Setting {} - {} for {}".format(pointer_name, hex(pointer), self.process_name))
            self.set_variable(pointer_name, pointer)
        return pointer

    def set_variable(self, variable, value):
        setattr(self, variable, value)

    def get_variable(self, variable):
        try:
            return getattr(self, variable)
        except AttributeError:
            return None

    @staticmethod
    def get_window_handle_and_pid():
        BasePointers.LOGGER.info("Click on window, wait 2 sec to get handle and process from window")
        time.sleep(2)
        window_handle = win32gui.GetForegroundWindow()

        _, process_pid = win32process.GetWindowThreadProcessId(window_handle)
        BasePointers.LOGGER.info("Found process pid and window handle")
        return pymem.Pymem(process_pid), window_handle
