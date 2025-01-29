import logging
import time

from memory.game_modules import GameModules
from abc import ABC, abstractmethod


class DungeonStage(ABC):

    def __init__(self, process, stage_name, preconditions_dict=None, **game_modules_kwargs):
        self.stage_name = stage_name
        self.modules = GameModules(process, **game_modules_kwargs)
        self.preconditions_dict = preconditions_dict or {}
        self.allowed_entities_offsets = []
        self.logger = logging.getLogger("logger.{}".format(stage_name))

    def run(self):
        self.logger.info("Stage {} start".format(self.stage_name))
        start_time = time.monotonic()
        self.run_preconditions()
        self.run_stage()
        self.run_postconditions()
        self.logger.info("Stage {} end, took: {}".format(self.stage_name, time.monotonic() - start_time))

    def run_preconditions(self):
        start_cords = self.preconditions_dict.get("start_cords", None)
        entities = self.preconditions_dict.get("entities_offsets", [])
        entities_amount = self.preconditions_dict.get("entities_amount", 1000)
        expected_entities_amount = self.preconditions_dict.get("expected_entities_amount", len(entities))
        if start_cords:
            self.modules.player.wait_until_player_cords_in_range(*start_cords)
        if entities:
            self.modules.entity.wait_until_entities_appear(entities, ent_amt=entities_amount,
                                                           expected_entities_amount=expected_entities_amount)

    @abstractmethod
    def run_stage(self):
        pass

    def run_postconditions(self):
        pass


class DestroyMetinDungeonStage(DungeonStage):

    def __init__(self, process, stage_name, metin_offsets, metin_amount=None, pick_items=True, turn_buffs=True,
                 pull_mobs=False, random_first_choose=True, horseback_slash=False, **game_modules_kwargs):
        self.metin_offsets = metin_offsets
        self.metin_amount = metin_amount
        self.destroy_metin_arguments_dict = {
            "pick_items": pick_items,
            "turn_buffs": turn_buffs,
            "pull_mobs": pull_mobs,
            "random_first_choose": random_first_choose,
            "horseback_slash": horseback_slash
        }
        preconditions_dict = {
            "entities_offsets": self.metin_offsets,
            "expected_entities_amount": self.metin_amount
        }
        super().__init__(process=process, stage_name=stage_name, preconditions_dict=preconditions_dict,
                         **game_modules_kwargs)
        self.allowed_entities_offsets = [metin_offsets]

    def run_stage(self):
        metin_entities = self.modules.entity.get_filtered_entities(self.metin_offsets)
        if self.metin_amount is not None and len(metin_entities) != self.metin_amount:
            raise Exception("Stage {}, not found correct amount of metin".format(self.stage_name))
        self.modules.destroy_all_metin_in_distance_order(metin_entities, **self.destroy_metin_arguments_dict)


class KillMobsDungeonStage(DungeonStage):

    def __init__(self, process, stage_name, mob_offsets, waves_amount=1, wait_until_appear_offsets=None,
                 expected_entities_amount=0, timeout=180):
        self.mob_offsets = mob_offsets
        self.waves_amount = waves_amount
        self.wait_until_appear_offsets = wait_until_appear_offsets or mob_offsets
        self.expected_entities_amount = expected_entities_amount
        self.timeout = timeout
        super().__init__(process=process, stage_name=stage_name)

    def run_stage(self):
        self.modules.player.start_attacking()
        for _ in range(self.waves_amount):
            self.modules.entity.wait_until_entities_appear(self.mob_offsets, ent_amt=200)
            start_time = time.monotonic()
            while time.monotonic() - start_time < self.timeout:
                if self.modules.entity.check_entities_existence(filter_offsets=self.wait_until_appear_offsets,
                                                                expected_entities_amount=self.expected_entities_amount):
                    break
                self.modules.player.pick_close_items()
                self.modules.player.turn_on_all_buff_skills()
                self.modules.pull_mobs_if_they_far_away(self.mob_offsets, max_mob_distance=7)
                time.sleep(0.7)
            else:
                raise Exception("All mobs not died on time in Stage {}".format(self.stage_name))
        self.modules.player.stop_attacking()


class BossDungeonStage(DungeonStage):

    def __init__(self, process, stage_name, boss_offsets, collect_drop=False):
        self.boss_offsets = boss_offsets
        self.collect_drop = collect_drop
        preconditions_dict = {
            "entities": self.boss_offsets,
        }
        super().__init__(process=process, stage_name=stage_name, preconditions_dict=preconditions_dict)
        self.allowed_entities_offsets = [boss_offsets]

    def run_stage(self):
        boss_entity = self.modules.entity.get_filtered_entities(self.boss_offsets)[0]

        self.modules.player.send_attack_to_vid_and_wait_until_die(boss_entity.vid)
        if self.collect_drop:
            self.modules.player.pick_close_items(multiplier=3, break_on_lack_drop=False, in_player_range=False)


class SealsDungeonStage(DungeonStage):

    def __init__(self, process, stage_name, mob_offsets, seals_vid, seals_amount, quick_slot=2, slot_range=45,
                 timeout=180):
        self.mob_offsets = mob_offsets
        self.seals_vid = seals_vid
        self.seals_amount = seals_amount
        self.slot_range = slot_range
        self.quick_slot = quick_slot
        self.timeout = timeout
        super().__init__(process=process, stage_name=stage_name)

    def run_stage(self):
        self.modules.player.start_attacking()
        for _ in range(self.seals_amount):
            self.modules.player.pull_mobs()
            start_time = time.monotonic()
            while time.monotonic() - start_time < self.timeout:
                self.modules.player.pick_close_items()
                self.modules.player.turn_on_all_buff_skills()
                self.modules.pull_mobs_if_they_far_away(self.mob_offsets, max_mob_distance=7)
                seal_slot_id = self.modules.inventory_slots.find_vid_in_slots(self.seals_vid, self.slot_range)
                if seal_slot_id:
                    self.logger.info("Found seal on slot {}, trying to click".format(seal_slot_id))
                    for retry in range(5):
                        self.modules.player.set_quick_slot_reference_and_use_slot(self.quick_slot, seal_slot_id)
                        if self.modules.inventory_slots.get_slot_vid(seal_slot_id) != self.seals_vid:
                            break
                        time.sleep(0.5)
                    else:
                        raise Exception("Cannot use seal on slot {} in Stage {}".format(seal_slot_id, self.stage_name))
                    break
                time.sleep(0.6)
        self.modules.player.stop_attacking()
