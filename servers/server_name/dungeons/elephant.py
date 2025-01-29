import time
import random
from dungeon.dungeon import Dungeon
from dungeon.dungeon_stage import (DungeonStage, DestroyMetinDungeonStage, BossDungeonStage,
                                   SealsDungeonStage, KillMobsDungeonStage)


class Stage1(KillMobsDungeonStage):

    def __init__(self, process, **game_modules_kwargs):
        stage_name = "ElephantStage1"
        mob_offsets = {"id": 101, "type": 0}
        metin_offsets = {"id": 16616, "type": 2}

        super().__init__(process=process, stage_name=stage_name, mob_offsets=mob_offsets, expected_entities_amount=4,
                         wait_until_appear_offsets=metin_offsets, **game_modules_kwargs)
        self.preconditions_dict.update({"start_cords": (range(195, 210), range(215, 232))})


class Stage2(DestroyMetinDungeonStage):

    def __init__(self, process, **game_modules_kwargs):
        stage_name = "ElephantStage2"
        metin_offsets = {"id": 16616, "type": 2}
        metin_amount = 4

        super().__init__(process=process, stage_name=stage_name, metin_offsets=metin_offsets, metin_amount=metin_amount,
                         **game_modules_kwargs)


class Stage3(KillMobsDungeonStage):

    def __init__(self, process, **game_modules_kwargs):
        stage_name = "ElephantStage3"
        mob_offsets = {"type": 0}
        metin_offsets = {"id": 16617, "type": 2}
        mini_boss_offsets ={"id": 16622, "type": 0}
        metin_amount = 6

        super().__init__(process=process, stage_name=stage_name, timeout=300, mob_offsets=mob_offsets,
                         wait_until_appear_offsets=metin_offsets, expected_entities_amount=metin_amount,
                         **game_modules_kwargs)
        self.allowed_entities_offsets = [metin_offsets, mini_boss_offsets]

    def run_preconditions(self):
        self.modules.player.move_to_pos_with_horseback_slash(x=200 + random.randint(-3, 3),
                                                             y=222 + random.randint(-3, 3))
        super().run_preconditions()


class Stage4(DestroyMetinDungeonStage):

    def __init__(self, process, **game_modules_kwargs):
        stage_name = "ElephantStage4"
        metin_offsets = {"id": 16617, "type": 2}
        metin_amount = 6

        super().__init__(process=process, stage_name=stage_name, metin_offsets=metin_offsets, metin_amount=metin_amount,
                         **game_modules_kwargs)


class Stage5(KillMobsDungeonStage):

    def __init__(self, process, **game_modules_kwargs):
        stage_name = "ElephantStage5"
        mob_offsets = {"id": 101, "type": 0}
        self.miniboss_offsets = {"id": 16624, "type": 0}

        super().__init__(process=process, stage_name=stage_name, mob_offsets=mob_offsets,
                         wait_until_appear_offsets=self.miniboss_offsets, expected_entities_amount=1,
                         **game_modules_kwargs)

    def run_postconditions(self):
        miniboss_entity = self.modules.entity.get_filtered_entities(self.miniboss_offsets)[0]

        self.modules.player.send_attack_to_vid_and_wait_until_die(miniboss_entity.vid)


class Stage6(DungeonStage):

    def __init__(self, process, **game_modules_kwargs):
        stage_name = "ElephantStage6"
        self.statue_object = {"id": 16618, "type": 2}
        self.miniboss_offsets = {"id": 16625, "type": 0}
        self.metin_objects = {"id": 16619, "type": 2}
        preconditions_dict = {
            "entities": self.statue_object,
        }
        super().__init__(process=process, stage_name=stage_name, preconditions_dict=preconditions_dict,
                         **game_modules_kwargs)
        temp_miniboss_offsets = {'id': 16623, 'type': 0}
        self.allowed_entities_offsets = [self.miniboss_offsets, self.statue_object, self.metin_objects,
                                         temp_miniboss_offsets]

    def easy_penalty(self):
        metin_entities = self.modules.entity.get_filtered_entities(self.metin_objects)
        if len(metin_entities) < 2:
            self.logger.warning("Not found metin in easy penalty, going back to no penalty!")
            return
        self.modules.destroy_all_metin_in_distance_order(metin_entities, horseback_slash=True, pull_mobs=True)

    def hard_penalty(self):
        mini_boss_entity = self.modules.entity.get_filtered_entities(self.miniboss_offsets)
        if len(mini_boss_entity) != 1:
            self.logger.warning("Not found mini boss in hard penalty, going back to easy penalty!")
        else:
            self.modules.player.send_attack_to_vid_and_wait_until_die(mini_boss_entity[0].vid, horseback_slash=True)
        self.easy_penalty()

    def run_stage(self):
        statue_entity = self.modules.entity.get_filtered_entities(self.statue_object)
        challenge_start_time = time.monotonic()
        self.modules.player.send_attack_to_vid(statue_entity[0].vid)
        while self.modules.player.check_if_attack_target_vid_died() is False:
            self.modules.pull_mobs_if_they_far_away()
            time.sleep(0.5)
        challenge_done_time = time.monotonic() - challenge_start_time
        if challenge_done_time < 120:
            pass
        elif challenge_done_time < 180:
            self.easy_penalty()
        elif challenge_done_time > 180:
            self.hard_penalty()


class Stage7(DestroyMetinDungeonStage):

    def __init__(self, process, **game_modules_kwargs):
        stage_name = "ElephantStage7"
        metin_offsets = {"id": 16620, "type": 2}
        self.seals_statue_offsets = {"id": 60005, "type": 1}
        metin_amount = 4
        super().__init__(process=process, stage_name=stage_name, metin_offsets=metin_offsets, metin_amount=metin_amount,
                         pull_mobs=True, horseback_slash=True, **game_modules_kwargs)
        self.challenge_start_time = None
        self.allowed_entities_offsets.append(self.seals_statue_offsets)

    def run_preconditions(self):
        self.modules.window_messages.send_string_to_window("\r/challenge_dungeon\r\r")
        self.challenge_start_time = time.monotonic()
        super().run_preconditions()

    def run_postconditions(self):
        self.modules.player.start_attacking()
        while (self.modules.entity.check_entities_existence(self.seals_statue_offsets, expected_entities_amount=3) and
               time.monotonic() - self.challenge_start_time < 120):
            self.modules.pull_mobs_if_they_far_away()
            time.sleep(0.5)
        self.modules.player.stop_attacking()
        challenge_done_time = time.monotonic() - self.challenge_start_time
        if challenge_done_time > 120:
            raise Exception("Challenge not done on time in Stage {}".format(self.stage_name))


class Stage8(SealsDungeonStage):

    def __init__(self, process, **game_modules_kwargs):
        stage_name = "ElephantStage8"
        mob_offsets = {"id": 101, "type": 0}
        seals_vid = 48020
        seals_amount = 4
        self.miniboss_offsets = {"id": 16625, "type": 0}
        super().__init__(process=process, stage_name=stage_name, mob_offsets=mob_offsets, seals_vid=seals_vid,
                         seals_amount=seals_amount, **game_modules_kwargs)
        self.allowed_entities_offsets = [self.miniboss_offsets, mob_offsets]

    def run_postconditions(self):
        self.modules.player.start_attacking()
        self.modules.player.pull_mobs()
        while self.modules.entity.check_entities_existence(self.miniboss_offsets, expected_entities_amount=0) is False:
            self.modules.pull_mobs_if_they_far_away()
            time.sleep(0.5)
        self.modules.player.stop_attacking()


class Stage9(DestroyMetinDungeonStage):

    def __init__(self, process, **game_modules_kwargs):
        stage_name = "ElephantStage9"
        metin_offsets = {"id": 16621, "type": 2}
        metin_amount = 4

        super().__init__(process=process, stage_name=stage_name, metin_offsets=metin_offsets, metin_amount=metin_amount,
                         random_first_choose=False, **game_modules_kwargs)


class Stage10(KillMobsDungeonStage):

    def __init__(self, process, **game_modules_kwargs):
        stage_name = "ElephantStage10"
        mob_offsets = {"id": 101, "type": 0}
        main_boss_offsets = {"id": 16626, "type": 0}

        super().__init__(process=process, stage_name=stage_name, mob_offsets=mob_offsets,
                         wait_until_appear_offsets=main_boss_offsets, expected_entities_amount=1,
                         **game_modules_kwargs)

    def run_preconditions(self):
        self.modules.player.move_to_pos_with_horseback_slash(x=200 + random.randint(-5, 5),
                                                             y=222 + random.randint(-5, 5))
        super().run_preconditions()


class Stage11(BossDungeonStage):

    def __init__(self, process, **game_modules_kwargs):
        stage_name = "ElephantStage11"
        main_boss_offsets = {"id": 16626, "type": 0}

        super().__init__(process=process, stage_name=stage_name, boss_offsets=main_boss_offsets, collect_drop=True)


class Elephant(Dungeon):

    def __init__(self, process, iteration_amount, **game_modules_kwargs):
        dungeon_name = "Elephant"
        dungeon_stages = [Stage1(process, **game_modules_kwargs), Stage2(process, **game_modules_kwargs),
                          Stage3(process, **game_modules_kwargs), Stage4(process, **game_modules_kwargs),
                          Stage5(process, **game_modules_kwargs), Stage6(process, **game_modules_kwargs),
                          Stage7(process, **game_modules_kwargs), Stage8(process, **game_modules_kwargs),
                          Stage9(process, **game_modules_kwargs), Stage10(process, **game_modules_kwargs),
                          Stage11(process, **game_modules_kwargs)]
        enter_npc_offsets = {"id": 60257, "type": 1}
        super().__init__(process=process, iterations_amount=iteration_amount, dungeon_stages=dungeon_stages,
                         dungeon_name=dungeon_name, enter_npc_offsets=enter_npc_offsets, **game_modules_kwargs)

    def start_dungeon(self):
        self.modules.player.turn_on_all_buff_skills()


if __name__ == "__main__":
    from servers.server_name.variables import POINTERS
    from memory.base_pointers import BasePointers
    from memory.game_modules import GameModules
    from logger.logger import init_logger

    LOGGER_PATH = r"HIDDEN"
    LOG_FILE_NAME = "HIDDEN"
    init_logger(LOGGER_PATH, LOG_FILE_NAME)
    process, window_hwnd = BasePointers.get_window_handle_and_pid()

    BasePointers(process, window_hwnd).initialize_pointers(POINTERS)
    player_config = {
        "buff_skills": {"enchanted_blade": "f2"},
        "pull_mobs": 1,
        "skills": {"horseback_slash": "2"}
    }
    modules = GameModules(process, player_config=player_config, window_hwnd=window_hwnd, **POINTERS)

    Elephant(process=process, iteration_amount=1).run_dungeon()
