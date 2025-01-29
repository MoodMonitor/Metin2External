from memory.base_pointers import BasePointers
from memory.utilities import get_address_from_offsets


class Pointer:
    def __init__(self, process, pointer_dict, pointer_name):
        """
        Initialize a Pointer object to interact with memory structures in a process.

        :param process:
            The pymem object representing the target process.
        :param pointer_dict:
            A dictionary containing information about the memory pointer and offsets.
            The expected format of the dictionary is:
            {
                "sig": str,                # A string representing the signature or identifier for the pointer.
                "extra": int,              # An additional offset for address.
                "offset": int,             # An additional offset for the pointer.
                "offsets": {               # A dictionary of named offsets for finer control.
                    "offset_name": {
                        "offset": list,         # A list of offsets to resolve the final memory address.
                        "value_type": ctype,    # The data type of the value at the memory address
                                                  (e.g., ctypes.c_uint()).
                        "validation_value": function,  # A function to validate the value read from memory.
                        "values": dict          # A dictionary of predefined possible values.
                    }
                }
            }
        :param pointer_name:
            Name of the pointer, that will be set in BASE_POINTERS
        """
        self.process = process
        self.pointer_dict = pointer_dict
        self.pointer_address = BasePointers(self.process).initialize_pointer(pointer_name, self.pointer_dict)
        self.offset_addresses = {}

    def get_offsets_for_offset_name(self, offset_name):
        return self.pointer_dict["offsets"][offset_name]["offset"]

    def get_values_for_offset_name(self, offset_name):
        return self.pointer_dict["offsets"][offset_name]["values"]

    def get_value_for_offset_name(self, offset_name, value_name):
        return self.get_values_for_offset_name(offset_name)[value_name]

    def get_value_type_for_offset_name(self, offset_name):
        return self.pointer_dict["offsets"][offset_name]["value_type"]

    def get_validation_value_for_offset_name(self, offset_name):
        return self.pointer_dict["offsets"][offset_name]["validation_value"]

    def get_address_for_offsets(self, offsets):
        return get_address_from_offsets(self.process.process_handle, self.pointer_address, offsets)

    def get_address_for_offset_name(self, offset_name):
        return self.get_address_for_offsets(self.get_offsets_for_offset_name(offset_name))

    def get_address_value_for_offset_name(self, offset_name):
        address, value_type = (self.get_address_for_offset_name(offset_name),
                               self.get_value_type_for_offset_name(offset_name))
        return self.process.read_ctype(address, value_type)

    def set_address_value_for_offset_name(self, offset_name, value):
        address, value_type = (self.get_address_for_offset_name(offset_name),
                               self.get_value_type_for_offset_name(offset_name))
        self.process.write_ctype(address, type(value_type)(value))

    def set_defined_address_value_for_offset_name(self, offset_name, value_name):
        self.set_address_value_for_offset_name(offset_name, self.get_value_for_offset_name(offset_name, value_name))

