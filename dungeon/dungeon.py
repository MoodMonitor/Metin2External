import logging
import traceback
import time
from memory.game_modules import GameModules
from memory.observer import Observer


class Dungeon:

    def __init__(self, process, dungeon_name, dungeon_stages, iterations_amount, enter_npc_offsets,
                 **game_modules_kwargs):
        self.process = process
        self.dungeon_name = dungeon_name
        self.modules = GameModules(process, **game_modules_kwargs)
        self.dungeon_stages = dungeon_stages
        self.iterations_amount = iterations_amount
        self.enter_npc_offsets = enter_npc_offsets

        self.logger = logging.getLogger("logger.{}".format(self.dungeon_name))

    def run_dungeon(self):
        self.start_dungeon()
        self.enter_dungeon()
        time.sleep(1)
        allowed_entity_offsets = self._get_actual_entity_offsets_and_extend_allowed_entities()
        observer = Observer(process=self.process, allowed_entity_offsets=allowed_entity_offsets)
        observer.start_checker_function()
        for iteration in range(1, self.iterations_amount + 1):
            self.logger.info("Dungeon {} iteration {} start".format(self.dungeon_name, iteration))
            start_dungeon_time = time.monotonic()
            self.run_all_stages()
            stage_time = time.monotonic() - start_dungeon_time
            self.logger.info("Iteration {} took {}".format(iteration, stage_time))
            if iteration != self.iterations_amount:
                self.re_enter_dungeon()
        observer.stop_checker_function()
        self.end_dungeon()

    def run_all_stages(self):
        for dungeon_stage in self.dungeon_stages:
            try:
                dungeon_stage.run()
            except Exception as e:
                self.logger.error("Stage {} not done properly, because of - {}, type rerun to try again, skip to go to "
                                  "next stage or exit to quit the dungeon \n".
                                  format(dungeon_stage.stage_name, traceback.format_exc()))
                user_input = input()
                if user_input == "rerun":
                    dungeon_stage.run()
                elif user_input == "skip":
                    continue
                elif user_input == "exit":
                    raise e

    def enter_dungeon(self):
        entity_scan = self.modules.entity.get_filtered_entities(self.enter_npc_offsets, ent_amt=700)
        if len(entity_scan) != 1:
            raise Exception("Found more than one or zero enter dungeon npc!")
        self.modules.player.send_talk_to_vid(entity_scan[0].vid)
        time.sleep(1)
        while self.modules.player.check_if_player_disappear() is False:
            self.modules.dinput.press_and_release_keys("enter")
            time.sleep(1)
        self.modules.player.wait_until_player_appear()

    def re_enter_dungeon(self):
        self.modules.window_messages.send_string_to_window("\r/restart_dungeon\r\r")

    def start_dungeon(self):
        pass

    def end_dungeon(self):
        pass

    def _get_all_allowed_entities_offsets_from_stages(self):
        allowed_entities_offsets = []
        for stage in self.dungeon_stages:
            allowed_entities_offsets.extend(getattr(stage, "allowed_entities_offsets"))
        return allowed_entities_offsets

    def _get_actual_entity_offsets_and_extend_allowed_entities(self):
        allowed_entity_offsets = self._get_all_allowed_entities_offsets_from_stages()
        actual_entity_offsets = self.modules.entity.get_filtered_entities(allowed_entity_offsets, ent_amt=2000,
                                                                          return_unmatched_entities=True)
        actual_entity_offsets = [{"id": entity_offsets.id, "type": entity_offsets.type}
                                 for entity_offsets in actual_entity_offsets]
        allowed_entity_offsets.extend(actual_entity_offsets)
        self.logger.info("Allowed entity offsets: {}".format(allowed_entity_offsets))
        return allowed_entity_offsets
