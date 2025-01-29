from memory.pointers.pointer import Pointer


class InventorySlots:

    def __init__(self, process, inventory_slots_pointer=None, **kwargs):
        self.process = process
        self.inventory_slots_pointer = Pointer(self.process, inventory_slots_pointer, "inventory_slots")

    def get_slot_vid(self, slot_id):
        slot_offset = self.inventory_slots_pointer.get_value_for_offset_name("slot_vid", "slot_offset")(slot_id)
        return self.process.read_int(self.inventory_slots_pointer.get_address_for_offsets(slot_offset))

    def get_slot_quantity(self, slot_id):
        slot_offset = self.inventory_slots_pointer.get_value_for_offset_name("slot_quantity", "slot_offset")(slot_id)
        return self.process.read_int(self.inventory_slots_pointer.get_address_for_offsets(slot_offset))

    def find_vid_in_slots(self, vid, slot_range=180):
        for slot_id in range(1, slot_range + 1):
            if self.get_slot_vid(slot_id) == vid:
                return slot_id
        return None
