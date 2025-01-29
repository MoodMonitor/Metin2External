from pymem.exception import MemoryReadError
from memory.pointers.pointer import Pointer
import math
import time
import logging


class Entity:

    def __init__(self, process, entity_address, entity_pointer=None, constant_offsets=None):
        constant_offsets = constant_offsets or ["id", "type", "vid"]
        self.process = process
        self.entity_address = entity_address
        self.entity_pointer = entity_pointer
        for constant_offset in constant_offsets:
            setattr(self, constant_offset, self.get_offset_value(constant_offset))
        self.name = self.try_to_get_entity_name()

    def __getattr__(self, name):
        try:
            return self.__dict__[name]
        except KeyError:
            return self.get_offset_value(name)

    @property
    def x(self):
        return abs(self.get_offset_value("x")) / 100

    @property
    def y(self):
        return abs(self.get_offset_value("y")) / 100

    @property
    def z(self):
        return abs(self.get_offset_value("z")) / 100

    @x.setter
    def x(self, new_value):
        self.set_offset_value("x", new_value * 100)

    @y.setter
    def y(self, new_value):
        self.set_offset_value("y", new_value * 100 * -1)

    @z.setter
    def z(self, new_value):
        self.set_offset_value("z", new_value * 100)

    def get_offset_value(self, offset_name):
        offset = self.entity_pointer.get_offsets_for_offset_name(offset_name)[0]
        value_type = self.entity_pointer.get_value_type_for_offset_name(offset_name)
        return self.process.read_ctype(self.entity_address + offset, value_type)

    def set_offset_value(self, offset_name, value):
        offset = self.entity_pointer.get_offsets_for_offset_name(offset_name)[0]
        value_type = self.entity_pointer.get_value_type_for_offset_name(offset_name)
        self.process.write_ctype(self.entity_address + offset, type(value_type)(value))

    def try_to_get_entity_name(self, string_length=100):
        try:
            buff = self.process.read_bytes(self.get_offset_value("name"), string_length)
            i = buff.find(b'\x00')
            if i != -1:
                buff = buff[:i]
            return buff.decode('windows-1250', errors='ignore')
        except MemoryReadError:
            return None

    def check_if_entity_died(self):
        if int(self.x) == 0:
            return True
        return False

    def __str__(self):
        return "Entity {} address: {}, vid: {}, type: {}, id: {}".format(
            self.name, hex(self.entity_address), self.vid, self.type, self.id)


class EntityList:

    MOB_TYPE = 0
    METIN_TYPE = 2
    NPC_TYPE = 3

    def __init__(self, process, entity_pointer=None, **kwargs):
        self.process = process
        self.entity_pointer = Pointer(self.process, entity_pointer, "entity_pointer")
        self.logger = logging.getLogger("logger.{}".format(self.__class__.__name__))

    def get_filtered_entities(self, filter_offsets, ent_amt=331, return_unmatched_entities=False):
        """
        :param filter_offsets: List of dictionaries containing filter offsets for entities, eg.
               [{"id": 16616, "type": 2}, {"type": 0}]
        :param ent_amt: The maximum number of entities to retrieve.
        :param return_unmatched_entities: Return unmatched entities instead matched entities
        :return: List with entities
        """
        filter_keys = {}
        filter_offsets = filter_offsets if isinstance(filter_offsets, list) else [filter_offsets]
        for filters in filter_offsets:
            for offset, value in filters.items():
                if offset not in filter_keys:
                    filter_keys[offset] = [value]
                else:
                    filter_keys[offset].append(value)

        used_vids = []
        matched_entities, unmatched_entities = [], []
        for i in range(0, ent_amt):
            offset = 0x04 * i
            try:
                entity_address_ref = self.entity_pointer.get_address_for_offsets([offset])
                entity_address = self.process.read_uint(entity_address_ref)
                entity = Entity(self.process, entity_address, self.entity_pointer)
                vid = entity.vid
                if vid <= 0 or vid in used_vids or vid > 100000000:
                    continue
                used_vids.append(vid)
                result = self.filter_entity(filter_keys, entity) if filter_keys else ({}, True)
                x_value, y_value = entity.x, entity.y
                if x_value < 1 or y_value < 1 or x_value > 10000 or y_value > 10000:
                    continue
                entity_type, entity_id = entity.type, entity.id
                if entity_type > 1000 or entity_id > 1000000 or (entity_id == 0 and entity_type == 0):  # just trying to catch legacy entities
                    continue
                matched_entities.append(entity) if result is True else unmatched_entities.append(entity)
            except MemoryReadError:
                pass
        return matched_entities if return_unmatched_entities is False else unmatched_entities

    @staticmethod
    def filter_entity(filter_keys, entity):
        result = True
        for offset_name, available_values in filter_keys.items():
            value = getattr(entity, offset_name)
            if value not in available_values:
                result = False
        return result

    @staticmethod
    def calculate_distance(entity1_x, entity1_y, entity2_x, entity2_y):
        return math.sqrt((entity1_x - entity2_x)**2 + (entity1_y - entity2_y)**2)

    @staticmethod
    def calculate_distances_for_entities(entity_x, entity_y, entities):
        return {entity: EntityList.calculate_distance(entity_x, entity_y, entity.x, entity.y) for entity in entities}

    @staticmethod
    def filter_entities_by_distance(entity_x, entity_y, entities, distance, comparison_function=None):
        filtered_entities = []
        comparison_function = comparison_function or (lambda x, y: x <= y)
        for entity in entities:
            calculated_distance = EntityList.calculate_distance(entity_x, entity_y, entity.x, entity.y)
            if comparison_function(calculated_distance, distance):
                filtered_entities.append(entity)
        return filtered_entities

    @staticmethod
    def _check_if_expected_entities_amount(entities, expected_entities_amount):
        if expected_entities_amount == 0:
            if len(entities) == 0:
                return True
            return False
        elif len(entities) >= expected_entities_amount:
            return entities
        return False

    def check_entities_existence(self, filter_offsets=None, ent_amt=1000, expected_entities_amount=None):
        filter_offsets = filter_offsets or {"type": EntityList.MOB_TYPE}
        expected_entities_amount = len(filter_offsets) if expected_entities_amount is None else expected_entities_amount
        entity_scan = self.get_filtered_entities(filter_offsets, ent_amt)
        return self._check_if_expected_entities_amount(entity_scan, expected_entities_amount)

    def check_entities_existence_in_entity_range(self, filter_offsets, ent_amt=1000, expected_entities_amount=None,
                                                 entity_x=None, entity_y=None, max_distance=None):
        entity_scan = self.check_entities_existence(filter_offsets, ent_amt, expected_entities_amount)
        if entity_scan is False:
            return False
        entity_scan = self.filter_entities_by_distance(entity_x, entity_y, entity_scan, max_distance)
        return self._check_if_expected_entities_amount(entity_scan, expected_entities_amount)

    def wait_until_entities_appear(self, filter_offsets, ent_amt=331, expected_entities_amount=None, timeout=30):
        start_time = time.monotonic()
        while time.monotonic() - start_time < timeout:
            entities = self.check_entities_existence(filter_offsets, ent_amt, expected_entities_amount)
            if entities is not False:
                return entities
            time.sleep(0.1)
        else:
            raise Exception("Entities have not appeared on time")

    def wait_until_entities_appear_in_entity_range(self, filter_offsets, ent_amt=331, expected_entities_amount=None,
                                                   timeout=30, entity_x=None, entity_y=None, max_distance=None):
        start_time = time.monotonic()
        while time.monotonic() - start_time < timeout:
            entities = self.check_entities_existence_in_entity_range(filter_offsets, ent_amt, expected_entities_amount,
                                                                     entity_x, entity_y, max_distance)
            if entities is not False:
                return entities
            time.sleep(0.1)
        else:
            raise Exception("Entities have not appeared on time")

    def get_entities_filtered_by_distance(self, entity_x, entity_y, filter_offsets, max_distance, ent_amt=1000):
        scan_entities = self.get_filtered_entities(filter_offsets, ent_amt)
        return self.filter_entities_by_distance(entity_x, entity_y, scan_entities, max_distance)

    def check_if_entities_nearby(self, entity_x, entity_y, max_distance=3, ent_amt=1000, filter_offsets=None):
        filter_offsets = filter_offsets or {"type": EntityList.MOB_TYPE}
        filtered_entities = self.get_entities_filtered_by_distance(entity_x, entity_y, filter_offsets, max_distance,
                                                                   ent_amt)
        if filtered_entities:
            return True
        return False

    def get_nearest_entity(self, entity_x, entity_y, entities=None, filter_offsets=None, ent_amt=1000):
        filter_offsets = filter_offsets or {"type": EntityList.MOB_TYPE}
        scan_entities = entities or self.get_filtered_entities(filter_offsets, ent_amt)
        entity_distances = self.calculate_distances_for_entities(entity_x, entity_y, scan_entities)
        try:
            return min(entity_distances, key=entity_distances.get)
        except (IndexError, KeyError):
            return None

    def scan_entities(self, ent_amt=1000, wanted_offsets=None):
        wanted_offsets = wanted_offsets or ["x", "y"]
        used_vids = []
        offset = 0x0
        for i in range(0, ent_amt):
            entity_address_ref = self.entity_pointer.get_address_for_offsets([offset])
            entity_address = self.process.read_uint(entity_address_ref)
            entity = Entity(self.process, entity_address, self.entity_pointer)
            try:
                vid = entity.vid
                if vid <= 0 or vid in used_vids:
                    continue
                used_vids.append(vid)

                string_list = []
                for offset_name in wanted_offsets:
                    value = getattr(entity, offset_name)
                    string_list.append("{}: {}".format(offset_name, value))
                print(hex(offset), entity, "||", ", ".join(string_list))  # temp solution
            except MemoryReadError:
                pass
            offset += 0x04

    @staticmethod
    def convert_to_ascii(string):
        ascii_string = ""
        for s in string:
            if s.isascii() is False:
                break
            ascii_string += s
        return ascii_string
