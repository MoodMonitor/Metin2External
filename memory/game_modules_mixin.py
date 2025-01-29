import time
import random


class GameModulesMixin: 

    def get_entities_with_player_distance(self, filter_offsets, entities_amount=1000):
        entities = self.entity.get_filtered_entities(filter_offsets, entities_amount)
        return self.entity.calculate_distances_for_entities(*self.player.get_player_pos(), entities)

    def destroy_all_metin_in_distance_order(self, metin_entities, horseback_slash=False, pick_items=True,
                                            turn_buffs=True, pull_mobs=False, random_first_choose=True, timeout=180):
        for _ in range(len(metin_entities)):
            if random_first_choose:
                metin_entity = random.choice(metin_entities)
                metin_entities.remove(metin_entity)
                random_first_choose = False
            else:
                metin_entity = self.entity.get_nearest_entity(*self.player.get_player_pos(),entities=metin_entities)
                metin_entities.remove(metin_entity)

            self.player.use_horseback_slash_and_send_attack_to_vid(metin_entity.vid) if horseback_slash \
                else self.player.send_attack_to_vid(metin_entity.vid)
            start_time = time.monotonic()
            while time.monotonic() - start_time < timeout:
                if self.player.check_if_attack_target_vid_died() is True:
                    break
                self.player.pick_close_items() if pick_items else None
                self.player.turn_on_all_buff_skills() if turn_buffs else None
                self.pull_mobs_if_they_far_away() if pull_mobs else None
                time.sleep(0.1)
            else:
                raise Exception("Metin not destroyed on time!")

    def pull_mobs_if_they_far_away(self, filter_offsets=None, max_mob_distance=7, entities_amount=1000):
        filter_offsets = filter_offsets or {"type": self.entity.MOB_TYPE}
        mob_entities = self.entity.get_filtered_entities(filter_offsets, ent_amt=entities_amount)
        comparison_function = lambda actual_mob_distance, max_distance: actual_mob_distance >= max_distance
        far_entities = self.entity.filter_entities_by_distance(*self.player.get_player_pos(), mob_entities,
                                                               max_mob_distance, comparison_function)
        self.player.pull_mobs() if far_entities else None
