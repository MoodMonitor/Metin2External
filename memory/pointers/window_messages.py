import time
import random
import win32api
import win32gui
import win32con
from .pointer import Pointer
from memory.base_pointers import BasePointers


class WindowMessages:
    """
    Obsolete class used for passing clicks to the game window.

    This class was originally implemented to pass click events to the game window, but a better solution has been found.
    It is now considered outdated and should only be used if absolutely necessary.
    Future usage or modification of this class is discouraged unless no other alternatives exist.

    Now it is used only for sending some strings or messages to window.
    """

    def __init__(self, process, window_focus_pointer=None, window_handle=None, **kwargs):
        self.process = process
        self.window_pointer = Pointer(self.process, window_focus_pointer, "window_focus_pointer") \
            if window_focus_pointer else None
        self.window_hwnd = window_handle or BasePointers(self.process).window_hwnd

    def set_cursor_pos(self, x, y):
        self.window_pointer.set_address_value_for_offset_name("cursor_x", x)
        self.window_pointer.set_address_value_for_offset_name("cursor_y", y)

    def set_window_focus(self, focus_value):
        self.window_pointer.set_address_value_for_offset_name("focus", focus_value)

    def set_click_for_window_focus(self, click, focus_value):
        self.window_pointer.set_address_value_for_offset_name(click, focus_value)

    def check_focus_value(self, window_address, window_name):
        if self.process.read_string(window_address + 0x4, len(window_name)) == window_name:
            return True
        return False

    def get_window_size(self, window_address):
        x1 = self.process.read_int(window_address + 0x34)
        x2 = self.process.read_int(window_address + 0x3C)
        y1 = self.process.read_int(window_address + 0x38)
        y2 = self.process.read_int(window_address + 0x40)
        return x1, x2, y1, y2

    @staticmethod
    def get_single_inventory_cell_size(x1, x2, y1, y2, inventory_x_size=5, inventory_y_size=9):
        return abs(x2 - x1) / inventory_x_size, abs(y2 - y1) / inventory_y_size

    def get_inventory_slot_pos(self, slot_id, window_address, inventory_x_size=5, inventory_y_size=9):
        x1, x2, y1, y2 = self.get_window_size(window_address)
        x, y = self.get_single_inventory_cell_size(x1, x2, y1, y2, inventory_x_size, inventory_y_size)
        slot_x = slot_id % inventory_x_size or inventory_x_size
        slot_y = int(slot_id / inventory_x_size) + 1
        return x1 + x * slot_x - x / 2, y1 + y * slot_y - y / 2

    def click_on_inventory_slot(self, slot_id, window_address, key="right", inventory_x_size=5, inventory_y_size=9):
        self.mouse_click(*self.get_inventory_slot_pos(slot_id, window_address, inventory_x_size, inventory_y_size),
                         window_address, key)

    def mouse_click(self, x, y, window_address, key="right"):
        l_param = win32api.MAKELONG(int(x), int(y))
        win32gui.SendMessage(self.window_hwnd, win32con.WM_NCHITTEST, 0x0, l_param)
        win32gui.SendMessage(self.window_hwnd, win32con.WM_NCHITTEST, 0x0, l_param)
        win32gui.SendMessage(self.window_hwnd, win32con.WM_SETCURSOR, 1, l_param)
        win32gui.SendMessage(self.window_hwnd, win32con.WM_NCHITTEST, 1, l_param)
        win32gui.SendMessage(self.window_hwnd, win32con.WM_NCHITTEST, 1, l_param)
        win32gui.SendMessage(self.window_hwnd, win32con.WM_SETCURSOR, 1, l_param)
        self.set_window_focus(window_address)
        self.set_cursor_pos(int(x), int(y))
        win32gui.SendMessage(self.window_hwnd, win32con.WM_SETCURSOR, 1, l_param)
        if key == "right":
            self.set_click_for_window_focus("right_click", window_address)
            self.set_window_focus(window_address)
            win32api.PostMessage(self.window_hwnd, win32con.WM_RBUTTONDOWN, 1, l_param)
        elif key == "left":
            self.set_click_for_window_focus("left_click", window_address)
            self.set_window_focus(window_address)
            win32api.PostMessage(self.window_hwnd, win32con.WM_LBUTTONDOWN, 1, l_param)
        win32gui.SendMessage(self.window_hwnd, win32con.WM_SETCURSOR, 1, l_param)
        self.set_window_focus(window_address)
        self.set_cursor_pos(int(x), int(y))
        win32gui.SendMessage(self.window_hwnd, win32con.WM_SETCURSOR, 1, l_param)
        win32api.PostMessage(self.window_hwnd, win32con.WM_MOUSEMOVE, 1, l_param)
        win32gui.SendMessage(self.window_hwnd, win32con.WM_SETCURSOR, 1, l_param)
        time.sleep(0.1)
        if key == "right":
            win32api.PostMessage(self.window_hwnd, win32con.WM_RBUTTONUP, 1, l_param)
        elif key == "left":
            win32api.PostMessage(self.window_hwnd, win32con.WM_LBUTTONUP, 1, l_param)

    def send_string_to_window(self, string):
        for char in string:
            win32api.PostMessage(self.window_hwnd, win32con.WM_CHAR, ord(char), 0)
            time.sleep(random.uniform(0.07, 0.13))

    def __del__(self):
        win32gui.SendMessage(self.window_hwnd, win32con.WM_SETFOCUS, 0, 0)
        win32gui.SendMessage(self.window_hwnd, win32con.WM_CAPTURECHANGED, 0, 0)
        win32gui.SendMessage(self.window_hwnd, win32con.WM_CANCELMODE, 0, 0)
        win32gui.SendMessage(self.window_hwnd, win32con.WM_NCACTIVATE, 0, 0)
        win32gui.SendMessage(self.window_hwnd, win32con.WM_ACTIVATE, 0, 0)
        win32gui.SendMessage(self.window_hwnd, win32con.WM_ACTIVATEAPP, 0, 0x12C4)
        win32gui.SendMessage(self.window_hwnd, win32con.WM_KILLFOCUS, 0, 0)
        win32gui.SendMessage(self.window_hwnd, win32con.WM_IME_NOTIFY, 1, 0)
        win32gui.SendMessage(self.window_hwnd, win32con.WM_IME_SETCONTEXT, 0, 0xC000000F)
