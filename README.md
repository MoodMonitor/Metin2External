# Metin2External

## **Important Notice**

- This code cannot be run in its current form – all memory addresses have been hidden for security reasons.  
- The program automates repetitive tasks in the game, but **it does not include features such as DMG hacks or WaitHack**.

The BOT was created solely for educational purposes. Its source code is provided to demonstrate how such solutions can be implemented in Python without using compiled languages.

## **Project Description**

**Metin2External** is a BOT that automates specific processes in the game **Metin2**. The project combines a passion for programming and gaming, offering functions to streamline repetitive tasks such as:

- Dungeon automation
- Automatic shop browsing

## **How Does the BOT Work?**
It is an **external BOT**, which means it **is not injected into the game memory**, but connects to it externally and can read and modify values in the game process's memory.

The BOT uses **reverse engineering** to find key memory addresses related to game mechanics. The process involves:

1. Finding the **game memory addresses** responsible for the character, items, and NPCs.
2. Reading their values and **sending signals to the game**, simulating real player actions.
3. **Sending commands** by emulating keyboard and mouse inputs, e.g., by intercepting **DINPUT**.
4. Automatically **controlling the character** by modifying memory values related to movement.

## **Directory Structure**

```
Metin2External/  
├── dungeon/           # Dungeon modules  
│   ├── dungeon.py     # Class managing dungeons
│   ├── dungeon_stage.py  # Class managing a single dungeon stage
├── logger/            # Logging modules  
│   ├── logger.py      # File initializing the logger
├── memory/            # Modules for managing game memory
│   ├── base_pointers.py      # Class managing memory pointers
│   ├── game_modules.py       # Class managing game modules
│   ├── game_modules_mixin.py # Extending functionality with mixins
│   ├── observer.py           # Observer for game memory values
│   ├── utilities.py          # Tools for memory handling
│   ├── pointers/             # Modules responsible for specific game data
│   │   ├── dinput.py         # Module for sending keys to the game
│   │   ├── dropped_items.py  # Module managing dropped items in the game
│   │   ├── entity_list.py    # Module responsible for the list of entities in the game
│   │   ├── inventory_slots.py # Module handling the player's inventory
│   │   ├── player.py         # Module storing the player's character data
│   │   ├── pointer.py        # Base class for all pointers
│   │   ├── shop.py           # Module managing in-game shops
│   │   ├── skills.py         # Module managing the player's skills
│   │   ├── window_messages.py # Module sending messages to the game window
├── servers/            # Server-specific modules
│   ├── server_name/    # Modules dedicated to specific servers
│   │   ├── variables.py       # Memory addresses for the server
│   │   ├── dungeons/          # Dungeon implementation for the server
│   │   │   ├── elephant.py    # Module for the "Elephant" dungeon
├── utility/           # General auxiliary resources
│   ├── wrappers.py     # Decorators and wrappers for functionality
└── README.md          # Project documentation
```

## **Development Plans**

- **GUI Implementation** – A graphical user interface to facilitate the configuration and usage of the program.
- **Video Presentation** – A demo video showing the BOT in action.
- **Support for Additional Servers** – Enabling adaptation for different versions of Metin2.

## **Summary**

Metin2External is a project combining automation and reverse engineering, demonstrating that game bots can be created in Python without the need for compiled languages. The code does not include features affecting combat mechanics, and its primary goal is education and the analysis of game memory structure.

---

**Disclaimer:** This project is for educational purposes. We do not encourage its use in ways that violate the Metin2 game terms of service.


