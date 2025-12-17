# RenPyStein - Main Script and Data File

# --- Persistent Data ---
default persistent.stein_quality_mode = 1  # 0=High, 1=Low, 2=Ultra Low, 3=MS Paint is Better
default persistent.sayoristein_arena_highscore = 0
default persistent.stein_kills = 0
default persistent.tradu_coins = 0
default persistent.stein_pistol_level = 0
default persistent.stein_shotgun_level = 0
default persistent.stein_shotgun_unlocked = False
default persistent.stein_level1_cleared = False
default persistent.stein_level2_cleared = False
default persistent.stein_level3_cleared = False

# --- Save-Specific Data ---
# These variables hold the LIVE game state. They are initialized by reset_stein_state.
default player_x = 22.0
default player_y = 11.5
default player_dirx = -1.0
default player_diry = 0.0
default player_planex = 0.0
default player_planey = 0.66
default stein_enemies = []
default stein_sprites = []
default stein_session_coins = 0
default stein_has_shotgun = False
default stein_current_round = 0
default stein_inter_round_timer = 0.0
default stein_sniper_count = 0
default worldMap = []
default exits = []


init python:
    # --- Level 1 Data ---
    level1_data = {
        "worldMap": [
            [8,8,8,8,8,8,8,8,8,8,8,4,4,6,4,4,6,4,6,4,4,4,6,4],
            [8,0,0,0,0,0,0,0,0,0,8,4,0,0,0,0,0,0,0,0,0,0,0,4],
            [8,0,3,3,0,0,0,0,0,8,8,4,0,0,0,0,0,0,0,0,0,0,0,6],
            [8,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,6],
            [8,0,3,3,0,0,0,0,0,8,8,4,0,0,0,0,0,0,0,0,0,0,0,4],
            [8,0,0,0,0,0,0,0,0,0,8,4,0,0,0,0,0,6,6,6,0,6,4,6],
            [8,8,8,8,0,8,8,8,8,8,8,4,4,4,4,4,4,6,0,0,0,0,0,6],
            [7,7,7,7,0,7,7,7,7,0,8,0,8,0,8,0,8,4,0,4,0,6,0,6],
            [7,7,0,0,0,0,0,0,7,8,0,8,0,8,0,8,8,6,0,0,0,0,0,6],
            [7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8,6,0,0,0,0,0,4],
            [7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8,6,0,6,0,6,0,6],
            [7,7,0,0,0,0,0,0,7,8,0,8,0,8,0,8,8,6,4,6,0,6,6,6],
            [7,7,7,7,0,7,7,7,7,8,8,4,0,6,8,4,8,3,3,3,0,3,3,3],
            [2,2,2,2,0,2,2,2,2,4,6,4,0,0,6,0,6,3,0,0,0,0,0,3],
            [2,2,0,0,0,0,0,2,2,4,0,0,0,0,0,0,4,3,0,0,0,0,0,3],
            [2,0,0,0,0,0,0,0,2,4,0,0,0,0,0,0,4,3,0,0,0,0,0,3],
            [1,0,0,0,0,0,0,0,1,4,4,4,4,4,6,0,6,3,3,0,0,0,3,3],
            [2,0,0,0,0,0,0,0,2,2,2,1,2,2,2,6,6,0,0,5,0,5,0,5],
            [2,2,0,0,0,0,0,2,2,2,0,0,0,2,2,0,5,0,5,0,0,0,5,5],
            [2,0,0,0,0,0,0,0,2,0,0,0,0,0,2,5,0,5,0,5,0,5,0,5],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5],
            [2,0,0,0,0,0,0,0,2,0,0,0,0,0,2,5,0,5,0,5,0,5,0,5],
            [2,2,0,0,0,0,0,2,2,2,0,0,0,2,2,0,5,0,5,0,0,0,5,5],
            [2,2,2,2,1,2,2,2,2,2,2,1,2,2,2,5,5,5,5,5,5,5,5,5]
        ],
        "player_x": 22.0, "player_y": 11.5,
        "player_dirx": -1.0, "player_diry": 0.0,
        "player_planex": 0.0, "player_planey": 0.66,
        "enemies": [
            (18.5, 10.5, 4, 5), (5.5, 16.5, 4, 5)
        ],
        "sprites": [
            (20.5, 11.5, 2), (18.5,4.5, 2), (10.0,4.5, 2), (10.0,12.5,2),
            (3.5, 6.5, 2), (3.5, 20.5,2), (3.5, 14.5,2), (14.5,20.5,2)
        ],
        "exits": [
            (1.5, 1.5, "Exit 1"), (1.5, 22.5, "Exit 2"),
            (21.5, 1.5, "Exit 3"), (21.5, 22.5, "Exit 4")
        ]
    }

    # --- Level 2 Data ---
    level2_data = {
        "worldMap": [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,2,2,2,0,0,3,3,0,0,2,2,2,0,1],
            [1,0,2,0,0,0,0,3,0,0,0,0,0,2,0,1],
            [1,0,2,0,0,5,5,5,5,5,5,0,0,2,0,1],
            [1,0,0,0,0,5,0,0,0,0,5,0,0,0,0,1],
            [1,0,3,3,0,5,0,4,4,0,5,0,3,3,0,1],
            [1,0,0,0,0,0,0,4,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,4,0,0,0,0,0,0,0,1],
            [1,0,3,3,0,5,0,4,4,0,5,0,3,3,0,1],
            [1,0,0,0,0,5,0,0,0,0,5,0,0,0,0,1],
            [1,0,2,0,0,5,5,5,5,5,5,0,0,2,0,1],
            [1,0,2,0,0,0,0,3,0,0,0,0,0,2,0,1],
            [1,0,2,2,2,0,0,3,3,0,0,2,2,2,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        ],
        "player_x": 8.0, "player_y": 8.0,
        "player_dirx": 0.0, "player_diry": 1.0,
        "player_planex": 0.66, "player_planey": 0.0,
        "enemies": [ (13.5, 2.5, 4, 5), (2.5, 13.5, 4, 5), (7.5, 13.5, 4, 5) ],
        "sprites": [ (2.5, 2.5, 2), (13.5, 13.5, 2) ],
        "exits": [ (1.5, 1.5, "Exit") ]
    }

    # --- Level 3 Data ---
    level3_data = {
        "worldMap": [
            [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],
            [2,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,5,0,0,0,0,0,0,0,0,0,0,0,2],
            [2,0,2,2,2,2,2,0,2,0,4,4,4,4,4,4,4,4,0,5,0,4,4,4,0,4,4,4,4,4,0,2],
            [2,0,2,0,0,0,2,0,2,0,4,0,0,0,0,0,0,4,0,5,0,4,0,0,0,0,0,0,0,4,0,2],
            [2,0,2,0,2,0,2,0,0,0,4,0,4,4,4,4,0,4,0,0,0,4,0,4,4,4,4,4,0,4,0,2],
            [2,0,2,0,2,0,2,2,2,0,4,0,4,0,0,4,0,4,4,4,4,4,0,4,0,0,0,0,0,4,0,2],
            [2,0,0,0,2,0,0,0,0,0,4,0,0,0,0,4,0,0,0,0,0,0,0,4,4,0,4,4,4,4,0,2],
            [2,2,2,2,2,2,2,2,2,5,5,5,5,0,5,5,5,5,5,5,5,5,0,4,0,0,0,0,0,4,0,2],
            [6,6,6,6,6,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,6,6,6,0,6,0,2],
            [6,0,0,0,0,0,6,0,6,0,6,6,6,6,6,6,0,6,6,6,6,6,6,6,0,6,0,0,0,6,0,2],
            [6,0,3,3,0,0,0,0,0,0,0,0,0,0,0,6,0,6,0,0,0,0,0,6,0,6,0,6,6,6,0,2],
            [6,0,3,3,0,0,6,0,6,0,6,6,6,6,0,6,0,6,0,6,6,6,0,6,0,0,0,0,0,0,0,2],
            [6,0,0,0,0,0,6,0,6,0,6,0,0,0,0,0,0,0,0,6,0,6,0,6,6,6,6,6,6,6,6,6],
            [6,6,6,6,6,6,6,0,6,0,6,0,6,6,6,6,6,6,6,6,0,6,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,0,1],
            [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,1,0,0,0,0,0,0,0,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,1,0,1,0,1],
            [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,1,0,1,0,0,0,1,0,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,1,1,1,0,1,0,1],
            [1,1,1,1,1,1,1,1,8,8,8,8,8,8,8,8,8,8,8,0,8,8,0,0,0,0,0,0,0,1,0,1],
            [3,3,3,3,3,3,3,3,8,0,0,0,8,0,0,0,0,0,8,0,8,0,0,1,1,1,1,1,0,0,0,1],
            [3,0,0,0,0,0,0,3,8,0,8,0,8,0,8,8,8,0,8,0,8,0,8,8,0,0,0,8,0,8,8,8],
            [3,0,3,3,3,3,0,3,8,0,0,0,0,0,8,0,0,0,0,0,0,0,0,0,0,8,0,0,0,0,0,8],
            [3,0,3,0,0,3,0,3,8,8,8,8,8,0,8,8,8,8,8,8,8,8,8,8,0,8,8,8,8,8,0,8],
            [3,0,3,0,0,3,0,3,3,3,3,3,8,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8,0,8],
            [3,0,3,3,3,3,0,0,0,0,0,3,8,8,8,8,8,0,8,8,8,8,8,8,8,8,8,8,0,8,0,8],
            [3,0,0,0,0,0,0,3,3,3,0,3,7,7,7,7,8,0,8,7,7,7,7,7,7,7,0,0,0,8,0,8],
            [3,3,3,3,3,3,3,3,0,0,0,0,7,0,0,0,0,0,0,0,0,0,7,0,0,0,0,7,7,7,0,8],
            [7,7,7,7,7,7,7,7,0,7,7,7,7,0,7,7,7,7,7,7,7,0,7,0,7,7,7,7,0,0,0,8],
            [7,0,0,0,0,0,0,0,0,7,0,0,0,0,7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,0,8],
            [7,0,7,7,7,7,7,7,7,7,0,7,7,7,7,0,7,7,7,7,7,7,7,7,7,7,7,7,0,0,0,8],
            [7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,8,8,8,8]
        ],
        "player_x": 1.5, "player_y": 1.5,
        "player_dirx": 0.0, "player_diry": 1.0,
        "player_planex": 0.66, "player_planey": 0.0,
        "enemies": [
            (3.5, 4.5, 4, 5, 100), (6.5, 7.5, 4, 5, 100),
            (7.5, 12.5, 4, 5, 100), (7.5, 20.5, 4, 5, 100),
            (10.5, 2.5, 4, 5, 100), (10.5, 5.5, 4, 5, 100), (11.5, 4.5, 4, 5, 100),
            (12.5, 15.5, 4, 5, 100), (12.5, 18.5, 4, 5, 100),
            (15.5, 3.5, 4, 5, 100), (15.5, 7.5, 4, 5, 100), (15.5, 11.5, 4, 5, 100),
            (16.5, 5.5, 4, 5, 100), (16.5, 9.5, 4, 5, 100),
            (21.5, 2.5, 4, 5, 100), (22.5, 12.5, 4, 5, 100), (24.5, 5.5, 4, 5, 100),
            (25.5, 28.5, 4, 5, 100), (20.5, 29.5, 4, 5, 100),
            (29.5, 25.5, 4, 5, 150), (29.5, 27.5, 4, 5, 150),
            (30.5, 28.5, 4, 5, 300)
        ],
        "sprites": [
            (10.5, 10.5, 1), (10.5, 20.5, 1), (12.5, 12.5, 1),
            (1.5, 10.5, 0), (1.5, 20.5, 0),
            (28.5, 28.5, 2), (28.5, 29.5, 2), (28.5, 27.5, 2)
        ],
        "exits": [
            (30.5, 30.5, "Level 3 Complete")
        ]
    }

    # --- Level 4 (Arena) Data ---
    level4_data = {
        "worldMap": [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,0,0,1],
            [1,0,0,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,0,0,1],
            [1,0,0,0,0,0,0,3,3,0,0,0,0,0,0,0,0,0,0,0,0,3,3,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,3,3,0,0,0,0,0,0,0,0,0,0,0,0,3,3,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,4,0,4,0,0,0,0,0,0,4,0,4,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,5,0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,5,0,0,5,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,4,0,4,0,0,0,0,0,0,4,0,4,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,4,4,4,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,3,3,0,0,0,0,0,0,0,0,0,0,0,0,3,3,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,3,3,0,0,0,0,0,0,0,0,0,0,0,0,3,3,0,0,0,0,0,0,1],
            [1,0,0,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,0,0,1],
            [1,0,0,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        ],
        "player_x": 15.0, "player_y": 15.0,
        "player_dirx": -1.0, "player_diry": 0.0,
        "player_planex": 0.0, "player_planey": 0.66,
        "enemies": [],
        "sprites": [],
        "exits": [],
        "spawn_points": [
            (2,2), (2,27), (27,2), (27,27),
            (5,5), (5,24), (24,5), (24,24),
            (15, 2), (15, 27), (2, 15), (27, 15),
            (12,12), (18,18), (12,18), (18,12)
        ]
    }

    def reset_stein_state(level=1, arena=False):
        """
        Initializes or resets the game state for a specific level.
        """
        if level == 2:
            level_data = level2_data
        elif level == 3:
            level_data = level3_data
        elif level == 4:
            level_data = level4_data
        else: # Default to level 1
            level_data = level1_data

        renpy.store.worldMap = level_data["worldMap"]
        renpy.store.exits = level_data["exits"]
        renpy.store.player_x = level_data["player_x"]
        renpy.store.player_y = level_data["player_y"]
        renpy.store.player_dirx = level_data["player_dirx"]
        renpy.store.player_diry = level_data["player_diry"]
        renpy.store.player_planex = level_data["player_planex"]
        renpy.store.player_planey = level_data["player_planey"]
        renpy.store.stein_player_health = 100
        renpy.store.stein_current_weapon = "fist"
        renpy.store.stein_enemies = list(level_data["enemies"])
        renpy.store.stein_session_coins = 0
        renpy.store.stein_current_round = 0
        renpy.store.stein_inter_round_timer = 0.0
        renpy.store.stein_sniper_count = 0
        
        # Initialize sprites list with defined sprites and add barrel for each exit
        temp_sprites = list(level_data["sprites"])
        for exit_coord in level_data["exits"]:
            temp_sprites.append((exit_coord[0], exit_coord[1], 0)) # 0 is the barrel sprite index
        renpy.store.stein_sprites = temp_sprites

        # Pass arena data to the store
        renpy.store.is_arena_mode = arena
        if arena:
            renpy.store.persistent.stein_kills = 0
            renpy.store.arena_spawn_points = level_data.get("spawn_points", [])
            renpy.store.stein_has_shotgun = persistent.stein_shotgun_unlocked
        else:
            renpy.store.arena_spawn_points = []
            renpy.store.stein_has_shotgun = True # Always have weapons in story mode (for now)


# The screen that displays the main game engine.
screen stein:
    key "s" action None
    key "mouseup_3" action None

    python:
        # Quality settings: 0=High, 1=Low, 2=Ultra Low
        if persistent.stein_quality_mode == 0: # High
            internal_width = 1280
            internal_height = 720
        elif persistent.stein_quality_mode == 1: # Low
            internal_width = 640
            internal_height = 360
        elif persistent.stein_quality_mode == 2: # Ultra Low
            internal_width = 426
            internal_height = 240
        elif persistent.stein_quality_mode == 3: # MS Paint is Better
            internal_width = 213
            internal_height = 120
        else: # Bro, can you see?
            internal_width = 142
            internal_height = 80

    add Renpystein(
        1280, 720,
        worldMap=worldMap,
        exits=exits,
        internal_width=internal_width,
        internal_height=internal_height
    )

label renpystein_game:
    hide black
    show screen stein_controls_overlay
    call screen stein
    
    if _return == 'game_over_arena':
        $ persistent.tradu_coins += stein_session_coins
        s "You survived [renpy.store.last_arena_round] rounds and collected [stein_session_coins] Coins."
        if persistent.stein_session_coins != 0:
            s "Now you have a total of [persistent.tradu_coins] Tradu-Coins."
        else:
            s "You have [persistent.tradu_coins] Tradu-Coins."

        if renpy.store.new_highscore:
            s "A new high score!"
        else:
            s "You have a high score of [persistent.sayoristein_arena_highscore]."
            s "Try next time!"
    elif _return == 'game_over':
        s "You died."
    else:
        if _return == "Exit 1" or _return == "Exit 2" or _return == "Exit 3" or _return == "Exit 4":
            $ persistent.stein_level1_cleared = True
        elif _return == "Exit":
            $ persistent.stein_level2_cleared = True
        elif _return == "Level 3 Complete":
            $ persistent.stein_level3_cleared = True
             
        s "You found exit [_return]!"
    hide screen stein_controls_overlay
    return

label start_level_1:
    $ reset_stein_state(level=1)
    jump renpystein_game

label start_level_2:
    $ reset_stein_state(level=2)
    jump renpystein_game

label start_level_3:
    $ reset_stein_state(level=3)
    jump renpystein_game

label start_level_4_arena:
    $ reset_stein_state(level=4, arena=True)
    jump renpystein_game

# This is for backwards compatibility / direct calls
label renpystein_demo:
    jump start_level_1

label sayoristein_main_menu(mg_obj=None):
    show black zorder 99 with dissolve
    show chibi_dvd zorder 100 at t_chibi_dvd
    with dissolve
    pause 1.5
    hide chibi_dvd with dissolve
    call screen sayoristein_menu with dissolve
    show black zorder 99 with dissolve
    show chibi_dvd zorder 100 at t_chibi_dvd
    with dissolve
    pause 1.0
    hide chibi_dvd with dissolve
    hide black with dissolve
    return