from .pointers.player import Player
from .pointers.entity_list import EntityList
from .pointers.skills import Skills
from .pointers.dropped_items import DroppedItems
from .pointers.dinput import DINPUT
from .pointers.inventory_slots import InventorySlots
from .pointers.window_messages import WindowMessages
from .game_modules_mixin import GameModulesMixin


class GameModules(GameModulesMixin):

    _instances = {}

    def __new__(cls, process, *args, **kwargs):
        pid = process.process_id
        if pid not in cls._instances:
            new_instance = super().__new__(cls)
            modules = GameModules.initialize_modules(process, *args, **kwargs)
            for module_name, module in modules.items():
                setattr(new_instance, module_name, module)
            cls._instances[pid] = new_instance
        return cls._instances[pid]

    @staticmethod
    def initialize_modules(process, player_pointer=None, player_config=None, player_control_pointer=None,
                           drop_pointer=None, dinput_keys=None, skills_pointer=None, window_input_pointer=None,
                           key_input_pointer=None, inventory_slots_pointer=None, entity_pointer=None,
                           window_hwnd=None, window_focus_pointer=None, effects_pointer=None,
                           **kwargs):
        dinput = DINPUT(process=process, window_input_pointer=window_input_pointer,
                        key_input_pointer=key_input_pointer, dinput_keys=dinput_keys)
        skills = Skills(process=process, skills=skills_pointer)
        dropped_items = DroppedItems(process=process, drop_pointer=drop_pointer)
        player = Player(process=process, player_pointer=player_pointer, player_control_pointer=player_control_pointer,
                        dinput=dinput, skills_pointer=skills, drop=dropped_items, player_config=player_config,
                        effects_pointer=effects_pointer)
        entity = EntityList(process=process, entity_pointer=entity_pointer)
        inventory_slots = InventorySlots(process=process, inventory_slots_pointer=inventory_slots_pointer)
        window_messages = WindowMessages(process=process, window_handle=window_hwnd,
                                         window_focus_pointer=window_focus_pointer)
        return {"dinput": dinput,
                "skills": skills,
                "dropped_items": dropped_items,
                "player": player,
                "entity": entity,
                "inventory_slots": inventory_slots,
                "window_messages": window_messages}
