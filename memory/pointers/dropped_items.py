from .pointer import Pointer
from ..utilities import get_address_from_offsets
from pymem.exception import MemoryReadError
from .entity_list import EntityList
import logging



class DroppedItems:

    def __init__(self, process, drop_pointer=None, **kwargs):
        self.process = process
        self.drop_pointer = Pointer(self.process, drop_pointer, "drop_pointer")
        self.logger = logging.getLogger("logger.{}".format(self.__class__.__name__))

    def get_drop_amount(self):
        return self.drop_pointer.get_address_value_for_offset_name("drop_amount")

    def get_dropped_items_info(self):
        dropped_items_info = []
        drop_amount = self.get_drop_amount()
        if drop_amount == 0:
            return dropped_items_info
        items_offset = list(self.drop_pointer.get_offsets_for_offset_name("items"))
        change_offset_index = items_offset.index(".")

        item_offset = 0x0
        found_items = 0
        while found_items != drop_amount:
            items_offset[change_offset_index] = item_offset
            item_address = self.drop_pointer.get_address_for_offsets(items_offset)
            item_pos = self.get_pos_for_item_address(item_address)
            if item_pos:
                item_vid = self.get_vid_for_item_address(item_address)
                dropped_items_info.append({"x": item_pos[0], "y": item_pos[1], "vid": item_vid})
                found_items += 1
            item_offset += 0x4
        return dropped_items_info

    def get_dropped_items_info_in_player_range(self, player_x, player_y, player_range=2.8):
        dropped_items_info = self.get_dropped_items_info()
        return [item for item in dropped_items_info
                if EntityList.calculate_distance(player_x, player_y, item["x"], item["y"]) <= player_range]

    def get_drop_amount_in_player_range(self, player_x, player_y, player_range=2.8):
        return len(self.get_dropped_items_info_in_player_range(player_x, player_y, player_range))

    def get_pos_for_item_address(self, item_address):
        x_offset = self.drop_pointer.get_offsets_for_offset_name("x")
        x_address = get_address_from_offsets(self.process.process_handle, item_address, x_offset)
        try:
            x = self.process.read_float(x_address)
            if x == 0:
                return None
            y_offset = self.drop_pointer.get_offsets_for_offset_name("y")
            y_address = get_address_from_offsets(self.process.process_handle, item_address, y_offset)
            return abs(x / 100), abs(self.process.read_float(y_address) / 100)
        except MemoryReadError:
            return None

    def get_vid_for_item_address(self, item_address):
        vid_offset = self.drop_pointer.get_offsets_for_offset_name("item_vid")
        vid_address = get_address_from_offsets(self.process.process_handle, item_address, vid_offset)
        vid = self.process.read_int(vid_address)
        return vid if vid > 0 else 0
