import time
import logging
import subprocess
import ctypes
import winsound
from threading import Thread
from .game_modules import GameModules
from pymem.exception import MemoryReadError


class Observer:

    def __init__(self, process, allowed_entity_offsets=None, notify_mp3_path=None, **game_modules_kwargs):
        self.process = process
        self.modules = GameModules(process, **game_modules_kwargs)
        self.allowed_entity_offsets = allowed_entity_offsets
        self.last_effects_count = 0
        self.player_vid = None
        self.player_destination_cords = (0, 0)
        self.player_destination_distance = 0

        self.stop_thread = None
        self._last_notify = 0
        self.notify_mp3_path = notify_mp3_path
        self.logger = logging.getLogger("logger.{}".format(self.__class__.__name__))

    def notify(self, delay=30):
        if time.monotonic() - self._last_notify < delay:
            return
        elif self.notify_mp3_path:
            subprocess.run(r"start {}".format(self.notify_mp3_path), check=True, shell=True)
        else:
            frequency = 500
            duration = 3000
            winsound.Beep(frequency, duration)
            ctypes.windll.user32.MessageBoxW(0, "Observer notify!!", "Observer notify", 0)
        self._last_notify = time.monotonic()


    def check_buff_counts(self, callback=None):
        try:
            actual_buff_count = self.modules.player.get_player_effects_count()
            if abs(self.last_effects_count - actual_buff_count) > 1:
                callback = callback or self.modules.player.use_auto_support_items
                callback()
            self.last_effects_count = actual_buff_count
        except MemoryReadError as e:
            self.logger.warning("Failed to get player buff count: {}".format(e))

    def check_if_same_map(self, callback=None):
        actual_player_vid = self.modules.player.get_player_vid()
        if actual_player_vid != self.player_vid:
            callback = callback or self.notify
            callback()
            self.logger.warning("Old player vid: {}, actual player vid: {}".format(self.player_vid,
                                                                                   actual_player_vid))

    def check_if_player_died(self, callback=None):
        try:
            if self.modules.player.check_if_player_died() is False:
                return
            callback = callback or self.notify
            self.logger.info("Player died!")
            callback()
            time.sleep(5)
        except MemoryReadError as e:
            self.logger.warning("Failed to check if player died: {}".format(e))

    def check_message_count(self, callback=None):
        try:
            message_count = self.modules.player.get_private_messages_count()
            if message_count == 0:
                return
            callback = callback or self.notify
            self.logger.info("Message count is {}!".format(message_count))
            callback()
        except MemoryReadError as e:
            self.logger.warning("Failed to get player messages: {}".format(e))

    def checker_function(self):
        player_died_time = buff_counts_time = message_count_time = same_map_time = unallowed_mobs_time \
            = player_moved_time = time.monotonic()
        self.player_vid = self.modules.player.get_player_vid()
        self.last_effects_count = self.modules.player.get_player_effects_count()
        while self.stop_thread is not True:
            start_time = time.monotonic()
            player_died_time = self.use_checker_function_and_return_time(start_time, player_died_time, 3,
                                                                         self.check_if_player_died)
            buff_counts_time = self.use_checker_function_and_return_time(start_time, buff_counts_time, 3,
                                                                         self.check_buff_counts)
            message_count_time = self.use_checker_function_and_return_time(start_time, message_count_time, 3,
                                                                           self.check_message_count)
            same_map_time = self.use_checker_function_and_return_time(start_time, same_map_time, 3,
                                                                      self.check_if_same_map)
            unallowed_mobs_time = self.use_checker_function_and_return_time(start_time, unallowed_mobs_time, 3,
                                                                            self.check_if_unallowed_mobs)
            player_moved_time = self.use_checker_function_and_return_time(start_time, player_moved_time, 3,
                                                                          self.check_if_player_moved)
            time.sleep(1)

    @staticmethod
    def use_checker_function_and_return_time(actual_time, old_time, interval, checker_function, *args, **kwargs):
        if actual_time - old_time > interval:
            checker_function(*args, **kwargs)
            return time.monotonic()
        return old_time

    def start_checker_function(self):
        thread = Thread(target=self.checker_function, daemon=True)
        self.stop_thread = False
        thread.start()

    def stop_checker_function(self):
        self.stop_thread = True

    def check_if_unallowed_mobs(self, callback=None):
        if not self.allowed_entity_offsets:
            return
        unmatched_entities = self.modules.entity.get_filtered_entities(self.allowed_entity_offsets, ent_amt=5000,
                                                                       return_unmatched_entities=True)
        if unmatched_entities:
            printed_unmatched_entities = "\n ".join(str(obj) for obj in unmatched_entities)
            self.logger.warning("There are unallowed entities nearby:\n {}".format(printed_unmatched_entities))
            callback = callback or self.notify
            callback()

    def check_if_player_moved(self, callback=None):  # TODO: tb reviewed, shall maybe include last player pos
        """
         To check if the player's coordinates have been changed by the game master (GM),
         we monitor the destination player's position.
         If the difference between the previous distance to the destination point and the current distance
         is less than -3 (allowing for a small bias close to 0), it indicates that the player has been moved.
         This is because the player always moves in a straight line toward the destination point.
        """
        player_pos = self.modules.player.get_player_pos()
        player_dest = self.modules.player.get_player_destination_cords()
        if player_dest == (0, 0):
            return
        if self.modules.entity.calculate_distance(*player_dest, *self.player_destination_cords) < 3:
            actual_player_destination_distance = self.modules.entity.calculate_distance(*player_pos, *player_dest)
            distance_difference = self.player_destination_distance - actual_player_destination_distance
            if distance_difference < -3:
                callback = callback or self.notify
                callback()
                self.logger.warning("Difference between destination distance is: {} and destination points are: {} {}"
                                    .format(distance_difference, player_dest, self.player_destination_cords))
            self.player_destination_distance = actual_player_destination_distance
        self.player_destination_cords = player_dest
