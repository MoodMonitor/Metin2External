import logging
from pymem.exception import MemoryReadError
from .pointer import Pointer


class Skills:

    def __init__(self, process, skills, **kwargs):
        self.process = process
        self.skills_pointer = Pointer(self.process, skills, "skills_pointer")
        self.logger = logging.getLogger("logger.{}".format(self.__class__.__name__))
        self.skill_dict = self.find_skill_offsets()

    def find_skill_offsets(self, pointer_offset=300, pointers_amount=1000, offsets_amount=1000):
        skill_dict = {}
        skill_names = self.skills_pointer.get_values_for_offset_name("skill_name")
        reversed_skill_names = {skill_id: skill_name for skill_name, skill_id in skill_names.items()}
        skill_status = self.skills_pointer.get_offsets_for_offset_name("skill_status")
        len_longest_skill_name = sorted([len(skill_name) for skill_name in reversed_skill_names.keys()])[-1]

        self.skills_pointer.pointer_address -= 0x4 * pointer_offset
        for _ in range(pointers_amount):
            offset = 0x0
            for __ in range(offsets_amount):
                skill_name_address = self.skills_pointer.get_address_for_offsets([offset])
                try:
                    skill_name = self.process.read_string(skill_name_address, len_longest_skill_name)
                    if skill_name in reversed_skill_names.keys():
                        skill_dict[reversed_skill_names[skill_name]] = skill_name_address + skill_status
                        del reversed_skill_names[skill_name]
                except (MemoryReadError, UnicodeDecodeError):
                    pass
                offset += 0x4
            self.skills_pointer.pointer_address += 0x4
            if not reversed_skill_names:
                break
        else:
            self.logger.error("Not found all skills offsets!!!!")
        self.logger.info("Skill dict: {}".format(skill_dict))
        return skill_dict

    def get_skill_status(self, skill_name):
        status = self.process.read_int(self.skill_dict[skill_name])
        try:
            return self.skills_pointer.get_value_for_offset_name("skill_status", status)
        except KeyError:
            return "off"