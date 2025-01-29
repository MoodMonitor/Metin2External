import ctypes.wintypes

SKILLS = {
    "sig": "HIDDEN",
    "extra": 20,
    "offset": ["0xHIDDEN"],
    "offsets": {
        "skill_name": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_char(),
            "values": {
                "aura": "HIDDEN",
                "berserk": "HIDDEN",
                "enchanted_blade": "HIDDEN",
                "fear": "HIDDEN",
                "enchanted_armor": "HIDDEN",
                "horseback_slash": "HIDDEN"
            }
        },
        "skill_status": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_uint(),
            "values": {
                3: "on",
                2: "off"
            }
        }
    }
}

PLAYER_POINTER = {
        "sig": "HIDDEN",
        "extra": 1,
        "offset": ["0xHIDDEN"],
        "offsets": {
            "name": {
                "offset": ["0xHIDDEN"],
                "value_type": ctypes.c_char(),
                "validation_value": lambda x: x > 0.0
            },
            "nested_name": {
                "offset": ["0xHIDDEN"],
                "value_type": ctypes.c_char(),
                "validation_value": lambda x: x > 0.0
            },
            "x": {
                "offset": ["0xHIDDEN"],
                "value_type": ctypes.c_float(),
                "validation_value": lambda x: x > 0.0
            },
            "y": {
                "offset": ["0xHIDDEN"],
                "value_type": ctypes.c_float(),
                "validation_value": lambda x: x < 0.0
            },
            "z": {
                "offset": ["0xHIDDEN"],
                "value_type": ctypes.c_float(),
                "validation_value": lambda x: x > 0.0
            },
            "rotation": {
                "offset": ["0xHIDDEN"],
                "value_type": ctypes.c_float(),
                "validation_value": lambda x: 0.0 < x < 360.0
            },
            "dest_x": {
                "offset": ["0xHIDDEN"],
                "value_type": ctypes.c_float(),
                "validation_value": lambda x: x > 0.0
            },
            "dest_y": {
                "offset": ["0xHIDDEN"],
                "value_type": ctypes.c_float(),
                "validation_value": lambda x: x > 0.0
            },
            "vid": {
                "offset": ["0xHIDDEN"],
                "value_type": ctypes.c_uint(),
                "validation_value": lambda x: x > 0
            },
            "weapon_type": {
                "offset": ["0xHIDDEN"],
                "value_type": ctypes.c_uint(),
                "validation_value": lambda x: x > 0,
                "values": {"HIDDEN": "HIDDEN"}
            },
            "attacking": {
                "offset": ["0xHIDDEN"],
                "value_type": ctypes.c_uint(),
                "validation_value": lambda x: x == 2,
                "values": {
                    "idle": "HIDDEN"
                }
            },
            "poly": {
                "offset": ["0xHIDDEN"],
                "value_type": ctypes.c_uint(),
                "validation_value": lambda x: x >= 0,
                "values": {
                    "no_poly": "HIDDEN"
                }
            },
            "mounted": {
                "offset": ["0xHIDDEN"],
                "value_type": ctypes.c_byte(),
                "validation_value": lambda x: x >= 0,
                "values": {"HIDDEN": "HIDDEN"}
            },
            "died": {
                "offset": ["0xHIDDEN"],
                "value_type": ctypes.c_uint(),
                "validation_value": lambda x: x >= 0,
                "values": {"HIDDEN": "HIDDEN"}
            },
        }
}

WINDOW_INPUT = {
    "sig": "HIDDEN",
    "extra": 2,
    "offset": ["0xHIDDEN"],
    "offsets": {
         "capture_window": {
             "offset": ["0xHIDDEN"],
             "value_type": ctypes.c_uint(),
             "validation_value": lambda x: x == "HIDDEN" or x == "HIDDEN",
             "values": {
                 "HIDDEN": "HIDDEN"
             }
         },
         "capture_input": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_uint(),
            "validation_value": lambda x: x == "HIDDEN" or x == "HIDDEN",
            "values": {
                "HIDDEN": "HIDDEN"
            }
        }
    }
}


KEYS_INPUT = {
    "sig": "HIDDEN",
    "extra": 6,
    "offset": ["0xHIDDEN"],
    "offsets": {
        "capture_key_input": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_uint(),
            "validation_value": lambda x: x == 1 or x == 0,
            "values": {
                "HIDDEN": "HIDDEN"
            }
        }
    }
}

WINDOW_FOCUS = {
    "sig": "HIDDEN",
    "extra": 1,
    "offset": ["0xHIDDEN"],
    "offsets": {
        "focus": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_uint(),
            "validation_value": lambda x: x >= 0,
        },
        "cursor_x": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_uint(),
            "validation_value": lambda x: x >= 0,
        },
        "cursor_y": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_uint(),
            "validation_value": lambda x: x >= 0,
        },
        "left_click": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_uint(),
            "validation_value": lambda x: x >= 0,
        },
        "right_click": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_uint(),
            "validation_value": lambda x: x >= 0,
        },
    }
}

DINPUT_KEYS = {
    "esc": {
        "offset": ["0xHIDDEN"],
        "key_down": 32768
    },
    "space": {
        "offset": ["0xHIDDEN"],
        "key_down": 32768
    },
    "ctrl": {
        "offset": ["0xHIDDEN"],
        "key_down": 32768
    },
    "q": {
        "offset": ["0xHIDDEN"],
        "key_down": 128
    },
    "w": {
        "offset": ["0xHIDDEN"],
        "key_down": 32768
    },
    "e": {
        "offset": ["0xHIDDEN"],
        "key_down": 8388608
    },
    "1": {
        "offset": ["0xHIDDEN"],
        "key_down": 8388608
    },
    "2": {
        "offset": ["0xHIDDEN"],
        "key_down": 2147483648
    },
    "3": {
        "offset": ["0xHIDDEN"],
        "key_down": 128
    },
    "4": {
        "offset": ["0xHIDDEN"],
        "key_down": 32768
    },
    "f1": {
        "offset": ["0xHIDDEN"],
        "key_down": 2147483648
    },
    "f2": {
        "offset": ["0xHIDDEN"],
        "key_down": 128
    },
    "f3": {
        "offset": ["0xHIDDEN"],
        "key_down": 32768
    },
    "f4": {
        "offset": ["0xHIDDEN"],
        "key_down": 8388608
    },
    "f5": {
        "offset": ["0xHIDDEN"],
        "key_down": 2147483648
    },
    "f6": {
        "offset": ["0xHIDDEN"],
        "key_down": 128
    },
    "f7": {
        "offset": ["0xHIDDEN"],
        "key_down": 32768
    },
    "f8": {
        "offset": ["0xHIDDEN"],
        "key_down": 8388608
    },
    "f9": {
        "offset": ["0xHIDDEN"],
        "key_down": 2147483648
    },
    "z": {
        "offset": ["0xHIDDEN"],
        "key_down": 128
    },
    "g": {
        "offset": ["0xHIDDEN"],
        "key_down": 8388608
    },
    "i": {
        "offset": ["0xHIDDEN"],
        "key_down": 2147483648
    },
    "p": {
        "offset": ["0xHIDDEN"],
        "key_down": 32768
    },
    "enter": {
        "offset": ["0xHIDDEN"],
        "key_down": 128
    },
}

ENTITY_POINTER = {
        "sig": "HIDDEN",
        "extra": 1,
        "offset": ["0xHIDDEN"],
        "offsets": {
            "weapon_type": {
                "offset": ["0xHIDDEN"],
                "value_type": ctypes.c_uint(),
                "validation_value": lambda x: x > 0,
                "values": {"HIDDEN": "HIDDEN"}
            },
            "id": {
                "offset": ["0xHIDDEN"],
                "value_type": ctypes.c_uint(),
                "validation_value": lambda x: x >= 0.0
            },
            "type": {
                "offset": ["0xHIDDEN"],
                "value_type": ctypes.c_uint(),
                "validation_value": lambda x: x >= 0.0,
            },
            "vid": {
                "offset": ["0xHIDDEN"],
                "value_type": ctypes.c_uint(),
                "validation_value": lambda x: x > 0
            },
            "x": {
                "offset": ["0xHIDDEN"],
                "value_type": ctypes.c_float(),
                "validation_value": lambda x: x > 0.0
            },
            "y": {
                "offset": ["0xHIDDEN"],
                "value_type": ctypes.c_float(),
                "validation_value": lambda x: x > 0.0
            },
            "z": {
                "offset": ["0xHIDDEN"],
                "value_type": ctypes.c_float(),
                "validation_value": lambda x: x > 0.0
            },
            "rotation": {
                "offset": ["0xHIDDEN"],
                "value_type": ctypes.c_float(),
                "validation_value": lambda x: 0.0 < x < 360.0
            },
            "can_be_damaged": {
                "offset": ["0xHIDDEN"],
                "value_type": ctypes.c_uint(),
                "validation_value": lambda x: x >= 0.0,
                "values": {
                    "can_be_damaged": 0
                },
            },
            "name": {
                "offset": ["0xHIDDEN"],
                "value_type": ctypes.c_uint(),
                "validation_value": lambda x: x > 0.0
            }
        }
}

INVENTORY_SLOTS = {
    "sig": "HIDDEN",
    "extra": 1,
    "offset": ["0xHIDDEN"],
    "offsets": {
        "slot_vid": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_uint(),
            "validation_value": lambda x: x >= 0,
            "values": {
                "slot_offset": lambda slot_id: "HIDDEN" + 107 * (slot_id - 1)
            }
        },
        "slot_quantity": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_uint(),
            "validation_value": lambda x: x >= 0,
            "values": {
                "slot_offset": lambda slot_id: "HIDDEN" + 107 * (slot_id - 1)
            }
        }
    }
}

PLAYER_CONTROL = {
    "sig": "HIDDEN",
    "extra": 1,
    "offset": ["0xHIDDEN"],
    "offsets": {
        "movement": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_uint(),
            "validation_value": lambda x: x == "HIDDEN",
            "values": {"HIDDEN": "HIDDEN"}
        },
        "send_packet": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_uint(),
            "validation_value": lambda x: x == 0,
            "values": {"HIDDEN": "HIDDEN"}
        },
        "send_vid_attack": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_uint(),
            "validation_value": lambda x: x == 0
        },
        "actual_vid": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_uint(),
            "validation_value": lambda x: x == 0
        },
        "last_vid": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_uint(),
            "validation_value": lambda x: x == 0
        },
        "shield_vid": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_int(),
            "validation_value": lambda x: x > 0
        },
        "book_inventory": {
            "values": {
                "vid": lambda slot_id: "HIDDEN" + 0x66 * (slot_id - 1),
                "amount": lambda slot_id: "HIDDEN" + 0x66 * (slot_id - 1),
            }
        },
        "soul_stone_inventory": {
            "values": {
                "vid": lambda slot_id: "HIDDEN" + 0x66 * (slot_id - 1),
                "amount": lambda slot_id: "HIDDEN" + 0x66 * (slot_id - 1),
            }
        },
        "improver_inventory": {
            "values": {
                "vid": lambda slot_id: "HIDDEN" + 0x66 * (slot_id - 1),
                "amount": lambda slot_id: "HIDDEN" + 0x66 * (slot_id - 1),
            }
        },
        "case_inventory": {
            "values": {
                "vid": lambda slot_id: "HIDDEN" + 0x66 * (slot_id - 1),
                "amount": lambda slot_id: "HIDDEN" + 0x66 * (slot_id - 1),
            }
        },
        "dest_x": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_float(),
            "validation_value": lambda x: x > 0.0
        },
        "dest_y": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_float(),
            "validation_value": lambda x: x > 0.0
        },
        "quick_slots_page": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_uint(),
            "validation_value": lambda x: x == 0
        },
        "quick_slots_slot_reference": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_uint(),
            "validation_value": lambda x: x == 0,
            "values": {
                "slot_offset": lambda quick_slot_id: "HIDDEN" + 0x3 * (quick_slot_id - 1),
                "slot_reference_value": lambda slot_id: "HIDDEN" * (slot_id - 1) + 1 if slot_id > 0 else 0
            }
        },
        "effect_count": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_uint(),
        },
        "private_message_count": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_uint(),
            "validation_value": lambda x: x == 0
        }
    }
}


DROPPED_ITEMS = {
    "sig": "HIDDEN",
    "extra": 1,
    "offset": ["0xHIDDEN"],
    "offsets": {
        "drop_amount": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_uint(),
            "validation_value": lambda x: x == 0
        },
        "items": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_uint(),
            "validation_value": lambda x: x == 0
        },
        "item_vid":
            {
                "offset": ["0xHIDDEN"],
                "value_type": ctypes.c_uint(),
                "validation_value": lambda x: x == 0
            },
        "x": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_float(),
            "validation_value": lambda x: x > 0
        },
        "y": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_float(),
            "validation_value": lambda x: x > 0
        },
    }
}

EFFECTS_POINTER = {
    "sig": "HIDDEN",
    "extra": 2,
    "offset": ["0xHIDDEN"],
    "offsets": {
        "effects_count": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_uint(),
            "validation_value": lambda x: x > 0,
        }
    },

}

SHOP = {
    "sig": "HIDDEN",
    "extra": 1,
    "offset": ["0xHIDDEN"],
    "offsets": {
        "shop_open": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_uint(),
            "validation_value": lambda x: x == 0,
            "values": {
                "open": 1,
                "closed": 0
            }
        },
        "vid": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_uint(),
            "validation_value": lambda x: x == 0,
            "values": {
                "offset": ["0xHIDDEN"],
            }
        },
        "price": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_uint64(),
            "validation_value": lambda x: x == 0,
            "values": {
                "offset": ["0xHIDDEN"],
            }
        },
        "amount": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_uint16(),
            "validation_value": lambda x: x == 0,
            "values": {
                "offset": ["0xHIDDEN"],
            }
        },
        "type": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_ubyte(),
            "validation_value": lambda x: x == 0,
            "values": {
                "offset": ["0xHIDDEN"],
            }
        },
        "bonus_type": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_ubyte(),
            "validation_value": lambda x: x == 0
        },
        "bonus_value": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_int16(),
            "validation_value": lambda x: x == 0
        },
        "bonus_type_mystical_soul_stone": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_ubyte(),
            "validation_value": lambda x: x == 0
        },
        "bonus_value_mystical_soul_stone": {
            "offset": ["0xHIDDEN"],
            "value_type": ctypes.c_uint16(),
            "validation_value": lambda x: x == 0
        }
    }
}

POINTERS = {
    "skills_pointer": SKILLS,
    "player_pointer": PLAYER_POINTER,
    "window_input_pointer": WINDOW_INPUT,
    "key_input_pointer": KEYS_INPUT,
    "window_focus_pointer": WINDOW_FOCUS,
    "dinput_keys": DINPUT_KEYS,
    "entity_pointer": ENTITY_POINTER,
    "inventory_slots_pointer": INVENTORY_SLOTS,
    "player_control_pointer": PLAYER_CONTROL,
    "drop_pointer": DROPPED_ITEMS,
    "effects_pointer": EFFECTS_POINTER,
    "shop": SHOP,
}

__all__ = ["POINTERS"]