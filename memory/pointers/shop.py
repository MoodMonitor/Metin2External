import os
import time
import ctypes
from .pointer import Pointer
from .exceptions import BadShopStatus


class Shop:

    def __init__(self, process, shop_pointer):
        self.process = process
        self.shop_pointer = Pointer(self.process, shop_pointer, "shop_pointer")
        self.shops_data = {}
        self.last_known_slots_info = {}
        self.save_data_path = os.path.dirname(__file__)

    def get_offset_value_for_slot_id(self, offset_name, slot_id):
        offsets = self.shop_pointer.get_value_for_offset_name(offset_name, "offset")(slot_id)
        value_type = self.shop_pointer.get_value_type_for_offset_name(offset_name)
        address = self.shop_pointer.get_address_for_offsets([offsets])
        return self.process.read_ctype(address, value_type)

    def get_item_info_for_slot_id(self, slot_id):
        vid = self.get_offset_value_for_slot_id("vid", slot_id)
        if vid == 0:
            return None
        price = self.get_offset_value_for_slot_id("price", slot_id)
        amount = self.get_offset_value_for_slot_id("amount", slot_id)
        single_price = price / amount
        item_type = self.get_offset_value_for_slot_id("type", slot_id)
        return vid, single_price, amount, item_type

    def get_bonus_offsets_info_for_slot_id(self, slot_id):
        bonus_info = {}
        start_offset = self.shop_pointer.get_value_for_offset_name("amount", "offset")(slot_id) + 1
        end_offset = self.shop_pointer.get_value_for_offset_name("vid", "offset")(slot_id + 1) - 1
        for num, offset in enumerate(range(start_offset, end_offset)):
            value = self.process.read_ctype(self.shop_pointer.get_address_for_offsets([offset]), ctypes.c_ubyte())
            if value != 0:
                bonus_info["+{}".format(num)] = value
        return bonus_info

    def check_shop_status(self, wanted_shop_status):
        """
        :param wanted_shop_status: open/closed
        """
        shop_status = self.shop_pointer.get_address_value_for_offset_name("shop_open")
        return shop_status == self.shop_pointer.get_value_for_offset_name("shop_open", wanted_shop_status)

    def wait_until_shop_status(self, wanted_shop_status, timeout=10):
        start_time = time.monotonic()
        while time.monotonic() - start_time < timeout:
            if self.check_shop_status(wanted_shop_status) is True:
                return
        else:
            raise BadShopStatus("Shop not {} in time!".format(wanted_shop_status))

    def try_to_change_shop_status(self, wanted_shop_status, timeout, retries=3):
        for _ in range(retries):
            try:
                self.wait_until_shop_status(wanted_shop_status, timeout)
            except BadShopStatus:
                pass
        else:
            raise BadShopStatus("SHOP STATUS NOT CHANGED TO {}".format(wanted_shop_status))

    @staticmethod
    def format_value(value):
        if value < 1000:
            return "{:.0f}".format(value)
        elif value < 1e6:
            return "{:.1f}k".format(value / 1e3)
        elif value < 1e9:
            return "{:.1f}kk".format(value / 1e6)
        else:
            return "{:.1f}kkk".format(value / 1e9)
