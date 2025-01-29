import time
import random
import math
import logging
from pymem.exception import MemoryReadError
from .pointer import Pointer
from .entity_list import EntityList
from utility.wrappers import sleep_after


class Player:

    def __init__(self, process, player_pointer=None, player_control_pointer=None, camera_pointer=None, dinput=None,
                 skills_pointer=None, effects_pointer=None, drop=None, player_config=None, **kwargs):
        self.process = process
        self.player_pointer = Pointer(self.process, player_pointer, "player_pointer") \
            if player_pointer is not None else None
        self.player_control_pointer = Pointer(self.process, player_control_pointer, "player_control_pointer") \
            if player_control_pointer is not None else None
        self.camera_pointer = Pointer(self.process, camera_pointer, "camera_pointer") \
            if camera_pointer is not None else None
        self.effects_pointer = Pointer(self.process, effects_pointer, "effects_pointer") \
            if effects_pointer is not None else None
        self.dinput = dinput if dinput is not None else None
        self.dropped_items = drop if drop is not None else None
        self.skills = skills_pointer if skills_pointer is not None else None
        self.player_config = player_config
        self.logger = logging.getLogger("logger.{}".format(self.__class__.__name__))

    @sleep_after(0.33)
    def send_talk_to_vid(self, vid):
        self.logger.debug("Sending talk to vid: {}".format(vid))
        self.player_control_pointer.set_address_value_for_offset_name("last_vid", vid)
        self.player_control_pointer.set_defined_address_value_for_offset_name("send_packet", "talk")

    @sleep_after(0.33)
    def send_attack_to_vid(self, vid):
        self.logger.debug("Sending attack to vid: {}".format(vid))
        self.player_control_pointer.set_address_value_for_offset_name("send_vid_attack", vid)

    @sleep_after(0.33)
    def use_horseback_slash(self, retries=20):
        if "skills" not in self.player_config.keys() or "horseback_slash" not in self.player_config["skills"].keys():
            return None
        elif self.check_if_mounted() is False:
            return None
        counter = 0
        while self.skills.get_skill_status("horseback_slash") == "off":
            self.use_slot(self.player_config["skills"]["horseback_slash"])
            time.sleep(0.03)
            if counter == retries:
                raise Exception("Cannot use horseback slash")
        return True

    def use_horseback_slash_and_send_attack_to_vid(self, vid):
        self.send_attack_to_vid(vid)
        time.sleep(.69)  # to set correct rotation to vid
        result = self.use_horseback_slash()
        if not result:
            return None
        self.send_attack_to_vid(vid)

    def send_attack_to_vid_with_horseback_slash(self, vid):
        self.use_horseback_slash_and_send_attack_to_vid(vid)
        while self.check_if_attacking() is False:
            if self.skills.get_skill_status("horseback_slash") == "off":
                self.use_horseback_slash_and_send_attack_to_vid(vid)
        self.dismount_horse()
        self.send_attack_to_vid(vid)
        self.mount_horse()

    def get_player_pos(self):
        return (self.player_pointer.get_address_value_for_offset_name("x") / 100,
                abs(self.player_pointer.get_address_value_for_offset_name("y") / 100))

    def check_if_attacking(self):
        actual_attacking = self.player_pointer.get_address_value_for_offset_name("attacking")
        idle_value = self.player_pointer.get_value_for_offset_name("attacking", "idle")
        if actual_attacking != idle_value:
            return True
        return False

    @sleep_after(0.13)
    def start_attacking(self):
        self.player_control_pointer.set_defined_address_value_for_offset_name("movement", "attack")

    @sleep_after(0.13)
    def stop_attacking(self):
        self.player_control_pointer.set_defined_address_value_for_offset_name("movement", "stay")

    @sleep_after(0.13)
    def start_rotating_attack(self, orientation):
        self.start_attacking()
        self.player_control_pointer.set_defined_address_value_for_offset_name("camera_spin", orientation)

    def stop_rotating_attack(self):
        self.player_control_pointer.set_defined_address_value_for_offset_name("camera_spin", "idle")
        self.stop_attacking()

    def check_if_poly(self):
        poly_value = self.player_pointer.get_address_value_for_offset_name("poly")
        weapon_type_value = self.player_pointer.get_address_value_for_offset_name("weapon_type")
        if weapon_type_value != 1 and poly_value == 0:
            return False
        return True

    def use_slot(self, slot):
        self.dinput.press_and_release_keys(str(slot))

    def mount_horse(self, slot_call=None, retries=10, mount_status=False):
        retry = 0
        if slot_call is not None:
            self.use_slot(slot_call)
            time.sleep(random.uniform(0.005, 0.011))

        while self.check_if_mounted() is mount_status:
            self.dinput.press_and_release_keys(["ctrl", "g"])
            if retry == retries:
                exception_message = "mount" if mount_status is False else "dismount"
                raise Exception("Cannot {} horse".format(exception_message))
            retry += 1
            time.sleep(0.55)

    def dismount_horse(self, retries=10):
        self.mount_horse(retries=retries, mount_status=True)

    def check_if_mounted(self):
        mounted_value = self.player_pointer.get_value_for_offset_name("mounted", "mounted")
        if self.player_pointer.get_address_value_for_offset_name("mounted") != mounted_value:
            return False
        return True

    @sleep_after(0.03)
    def pick_close_item(self):
        self.dinput.press_and_release_keys("z")

    def pick_close_items(self, multiplier=2.5, break_on_lack_drop=True, in_player_range=True):
        if in_player_range:
            def get_drop_amount():
                return self.dropped_items.get_drop_amount_in_player_range(*self.get_player_pos())

        else:
            get_drop_amount = self.dropped_items.get_drop_amount

        for _ in range(int(get_drop_amount() * multiplier)):
            self.pick_close_item()
            if break_on_lack_drop and get_drop_amount() == 0:
                break

    def check_if_player_cords_in_range(self, x_range, y_range):
        x, y = self.get_player_pos()
        if x_range[0] < x < x_range[-1] and y_range[0] < y < y_range[-1]:
            return True
        return False

    def wait_until_player_cords_in_range(self, x_range, y_range, timeout=30):
        start_time = time.monotonic()
        while time.monotonic() - start_time < timeout:
            try:
                x, y = self.get_player_pos()
                if x_range[0] < x < x_range[-1] and y_range[0] < y < y_range[-1]:
                    break
            except MemoryReadError:
                pass
            time.sleep(0.1)
        else:
            raise Exception("Player have not reached the cords")

    def use_auto_support_items(self):
        self.dinput.press_and_release_keys("f5")

    def wait_until_player_appear(self, timeout=30):
        start_time = time.monotonic()
        while time.monotonic() - start_time < timeout:
            result = self.check_if_player_disappear()
            if result is False:
                return
            time.sleep(0.1)
        else:
            raise Exception("Player not appeared")

    def check_if_player_disappear(self):
        try:
            weapon_type = self.player_pointer.get_address_value_for_offset_name("weapon_type")
            if weapon_type == 0:
                return True
        except MemoryReadError:
            return True
        return False

    def get_player_rotation(self):
        player_rotation = self.player_pointer.get_address_value_for_offset_name("rotation")
        self.logger.debug("Actual player rotation: {}".format(player_rotation))
        return player_rotation

    def set_player_rotation(self, value):
        self.logger.debug("Setting player rotation: {}".format(value))
        self.player_pointer.set_address_value_for_offset_name("rotation", value)

    def get_player_attack_target_vid(self):
        return self.player_control_pointer.get_address_value_for_offset_name("send_vid_attack")

    def get_player_last_vid(self):
        return self.player_control_pointer.get_address_value_for_offset_name("last_vid")

    def get_player_target_vid(self):
        return self.player_control_pointer.get_address_value_for_offset_name("actual_vid")

    def wait_until_attack_target_vid_die(self, timeout=30):
        start_time = time.monotonic()
        while time.monotonic() - start_time < timeout:
            if self.check_if_attack_target_vid_died:
                return True
            time.sleep(0.03)
        else:
            raise Exception("Attack target vid not die in time")

    def check_if_attack_target_vid_died(self):
        if self.get_player_attack_target_vid() == 0:
            return True
        return False

    def wait_until_target_vid_unset(self, timeout=30):
        start_time = time.monotonic()
        while time.monotonic() - start_time < timeout:
            if self.get_player_target_vid() == 0:
                return True
            time.sleep(0.03)
        else:
            raise Exception("Target vid not unset in time")

    def set_camera_horizontal_rotation(self, value):
        self.camera_pointer.set_address_value_for_offset_name("horizontal", value)

    def check_if_player_died(self):
        player_id_value = self.player_pointer.get_address_value_for_offset_name("died")
        if player_id_value == 0:
            return True
        return False

    def get_player_name(self):
        name_address = self.player_pointer.get_address_for_offset_name("name")
        try:
            return self.process.read_string(name_address, 18)
        except (MemoryReadError, UnicodeDecodeError):
            try:
                name_address = self.player_pointer.get_address_for_offset_name("nested_name")
                return self.process.read_string(name_address, 18)
            except (MemoryReadError, UnicodeDecodeError):
                self.logger.info("Failed to get player name!!!")

    def try_to_turn_on_skill(self, skill_name, retries=5):
        retry = 0
        while self.skills.get_skill_status(skill_name) == "off":
            self.use_slot(self.player_config["buff_skills"][skill_name])
            if retry == retries:
                break
            retry += 1
            time.sleep(0.23)

    def use_buff_skill_and_mount_horse(self, skill_name, retries=5):
        if skill_name not in self.player_config["buff_skills"]:
            self.logger.error("Skill name not defined in config!!")
            return None
        self.logger.info("Using skill: {}".format(skill_name))
        self.dismount_horse()
        self.try_to_turn_on_skill(skill_name, retries=retries)
        self.mount_horse()

    def get_all_buff_skills_statuses(self):
        return {buff_skill: self.skills.get_skill_status(buff_skill)
                for buff_skill in self.player_config["buff_skills"].keys()}

    def check_if_need_to_turn_on_buff_skills(self):
        buff_skills_status = self.get_all_buff_skills_statuses()
        for buff_skill, buff_skill_status in buff_skills_status.items():
            if buff_skill_status == "off":
                return True
        return False

    def turn_on_all_buff_skills(self):
        buff_skills_status = self.get_all_buff_skills_statuses()
        for buff_skill, buff_skill_status in buff_skills_status.items():
            if buff_skill_status == "off":
                self.use_buff_skill_and_mount_horse(buff_skill)

    def rebuff_skills_with_equipment_change(self):
        main_shield_vid = self.player_control_pointer.get_address_value_for_offset_name("shield_vid")
        while self.player_control_pointer.get_address_value_for_offset_name("shield_vid") == main_shield_vid:
            for shortcut in self.player_config["equipment_change"]:
                self.dinput.press_and_release_keys(shortcut["change"])
                time.sleep(0.4)
        self.dismount_horse(retries=20)
        for buff_skill in self.player_config["buff_skills"].keys():
            while self.skills.get_skill_status(buff_skill) == "on":
                self.use_slot(self.player_config["buff_skills"][buff_skill])
                time.sleep(0.1)
            self.use_buff_skill_and_mount_horse(buff_skill)
        while self.player_control_pointer.get_address_value_for_offset_name("shield_vid") != main_shield_vid:
            for shortcut in self.player_config["equipment_change"]:
                self.dinput.press_and_release_keys(shortcut["back"])
                time.sleep(0.1)

    def pull_mobs(self):
        self.use_slot(str(self.player_config["pull_mobs"]))

    def send_attack_to_vid_and_wait_until_die(self, vid, timeout=180, horseback_slash=False):
        self.use_auto_support_items()
        if horseback_slash:
            self.send_attack_to_vid_with_horseback_slash(vid)
        else:
            self.send_attack_to_vid(vid)

        timeout_start = time.monotonic()
        time.sleep(1)
        while time.monotonic() - timeout_start < timeout:
            self.turn_on_all_buff_skills()
            self.pick_close_items()
            if self.check_if_attack_target_vid_died() is True:
                break
            time.sleep(0.1)
        else:
            raise Exception("Target not died in time!")

    def move_to_pos(self, x, y, wait_for_rotation=True):
        dest_x_value, dest_y_value = x * 100, y * 100
        self.player_control_pointer.set_address_value_for_offset_name("dest_x", dest_x_value)
        self.player_control_pointer.set_address_value_for_offset_name("dest_y", dest_y_value)
        time.sleep(0.03)
        self.player_control_pointer.set_defined_address_value_for_offset_name("send_packet", "move")
        if not wait_for_rotation:
            return
        distance = EntityList.calculate_distance(*self.get_player_pos(), x, y)
        if distance < 7:
            return
        time.sleep(0.03)
        while distance - EntityList.calculate_distance(*self.get_player_pos(), x, y) < 7:
            self.player_control_pointer.set_defined_address_value_for_offset_name("send_packet", "move")
            time.sleep(0.03)
        self.player_control_pointer.set_defined_address_value_for_offset_name("send_packet", "move")

    def move_to_pos_with_horseback_slash(self, x, y):
        self.move_to_pos(x, y, wait_for_rotation=False)
        time.sleep(0.1)
        result = self.use_horseback_slash()
        if not result:
            return None
        self.move_to_pos(x, y, wait_for_rotation=True)
        while EntityList.calculate_distance(*self.get_player_pos(), x, y) > 5:
            self.move_to_pos(x, y, wait_for_rotation=False)
            self.use_horseback_slash()
            time.sleep(0.1)
            self.move_to_pos(x, y, wait_for_rotation=False)
        self.dismount_horse()
        self.mount_horse()

    def check_if_moving_fast(self, sleep_time=0.13): # Just real time checking if move
        act_x, act_y = self.get_player_pos()
        time.sleep(sleep_time)
        after_x, after_y = self.get_player_pos()
        distance = math.sqrt((after_x - act_x)**2 + (after_y - act_y)**2)
        self.logger.debug("Check if moving, distance moved: {} in time: {}".format(distance, sleep_time))
        if distance > 0:
            return True
        return False

    def get_quick_slots_page(self):
        return self.player_control_pointer.get_address_value_for_offset_name("quick_slots_page")

    def set_quick_slots_page(self, page):
        self.player_control_pointer.set_address_value_for_offset_name("quick_slots_page", page - 1)

    def _get_quick_slot_id_offsets(self, quick_slot_id):
        return self.player_control_pointer.get_value_for_offset_name("quick_slots_slot_reference",
                                                                     "slot_offset")(quick_slot_id)

    def get_quick_slot_reference(self, quick_slot_id):
        address = self.player_control_pointer.get_address_for_offsets(self._get_quick_slot_id_offsets(quick_slot_id))
        return self.process.read_int(address)

    def get_reference_value_for_inventory_slot_id(self, inventory_slot_id):
        reference_value_func = self.player_control_pointer.get_value_for_offset_name("quick_slots_slot_reference",
                                                                                     "slot_reference_value")
        return reference_value_func(inventory_slot_id)

    def set_quick_slot_reference(self, quick_slot_id, inventory_slot_id=None, raw_reference_value=None):
        address = self.player_control_pointer.get_address_for_offsets(self._get_quick_slot_id_offsets(quick_slot_id))
        ref_value = self.get_reference_value_for_inventory_slot_id(inventory_slot_id) if inventory_slot_id is not None \
            else raw_reference_value
        self.process.write_int(address, ref_value)

    def set_quick_slot_reference_and_use_slot(self, quick_slot_id, slot_reference_id):
        actual_quick_slot_reference = self.get_quick_slot_reference(quick_slot_id)
        self.set_quick_slot_reference(quick_slot_id, slot_reference_id)
        self.use_slot(quick_slot_id)
        self.set_quick_slot_reference(quick_slot_id, raw_reference_value=actual_quick_slot_reference)

    def get_private_messages_count(self):
        return self.player_control_pointer.get_address_value_for_offset_name("private_message_count")

    def get_effect_count(self):
        return self.player_control_pointer.get_address_value_for_offset_name("effect_count")

    def get_player_vid(self):
        return self.player_pointer.get_address_value_for_offset_name("vid")

    def get_player_destination_cords(self):
        return (abs(self.player_pointer.get_address_value_for_offset_name("dest_x") / 100),
                abs(self.player_pointer.get_address_value_for_offset_name("dest_y") / 100))

    def get_player_effects_count(self):
        return self.effects_pointer.get_address_value_for_offset_name("effects_count")