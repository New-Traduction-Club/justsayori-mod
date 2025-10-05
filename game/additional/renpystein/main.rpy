# RenPyStein - Main Script and Data File

# --- Persistent Data ---
# 'persistent' variables keep their value even when the game is closed and reopened.
# We use it to remember the player's preferred quality setting.
default persistent.performance_mode = False

# --- Save-Specific Data ---
# 'default' variables are part of Ren'Py's save system. They are reset when a new game starts.
# We use them to store the state of the game world and the player's position.
default player_x = 22.0
default player_y = 11.5
default player_dirx = -1.0
default player_diry = 0.0
default player_planex = 0.0
default player_planey = 0.66
default stein_enemies = []
default stein_sprites = []


init python:
    # The world map and level exits are static and can be defined once at startup.
    # --- World Map Legend ---
    # 0: Empty space
    # 1-8: Different wall textures
    worldMap = [
        [8,8,8,8,8,8,8,8,8,8,8,4,4,6,4,4,6,4,6,4,4,4,6,4],#0
        [8,0,0,0,0,0,0,0,0,0,8,4,0,0,0,0,0,0,0,0,0,0,0,4],
        [8,0,3,3,0,0,0,0,0,8,8,4,0,0,0,0,0,0,0,0,0,0,0,6],
        [8,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,6],
        [8,0,3,3,0,0,0,0,0,8,8,4,0,0,0,0,0,0,0,0,0,0,0,4],
        [8,0,0,0,0,0,0,0,0,0,8,4,0,0,0,0,0,6,6,6,0,6,4,6],#5
        [8,8,8,8,0,8,8,8,8,8,8,4,4,4,4,4,4,6,0,0,0,0,0,6],
        [7,7,7,7,0,7,7,7,7,0,8,0,8,0,8,0,8,4,0,4,0,6,0,6],
        [7,7,0,0,0,0,0,0,7,8,0,8,0,8,0,8,8,6,0,0,0,0,0,6],
        [7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8,6,0,0,0,0,0,4],
        [7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8,6,0,6,0,6,0,6],#10
        [7,7,0,0,0,0,0,0,7,8,0,8,0,8,0,8,8,6,4,6,0,6,6,6],
        [7,7,7,7,0,7,7,7,7,8,8,4,0,6,8,4,8,3,3,3,0,3,3,3],
        [2,2,2,2,0,2,2,2,2,4,6,4,0,0,6,0,6,3,0,0,0,0,0,3],
        [2,2,0,0,0,0,0,2,2,4,0,0,0,0,0,0,4,3,0,0,0,0,0,3],
        [2,0,0,0,0,0,0,0,2,4,0,0,0,0,0,0,4,3,0,0,0,0,0,3],#15
        [1,0,0,0,0,0,0,0,1,4,4,4,4,4,6,0,6,3,3,0,0,0,3,3],
        [2,0,0,0,0,0,0,0,2,2,2,1,2,2,2,6,6,0,0,5,0,5,0,5],
        [2,2,0,0,0,0,0,2,2,2,0,0,0,2,2,0,5,0,5,0,0,0,5,5],
        [2,0,0,0,0,0,0,0,2,0,0,0,0,0,2,5,0,5,0,5,0,5,0,5],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5],#20
        [2,0,0,0,0,0,0,0,2,0,0,0,0,0,2,5,0,5,0,5,0,5,0,5],
        [2,2,0,0,0,0,0,2,2,2,0,0,0,2,2,0,5,0,5,0,0,0,5,5],
        [2,2,2,2,1,2,2,2,2,2,2,1,2,2,2,5,5,5,5,5,5,5,5,5]
    ]

    def reset_stein_state():
        """
        Initializes or resets the game state. This is called at the start of a new game
        to ensure all variables are set to their default values.
        """
        # Make the global variables available to modify
        global player_x, player_y, player_dirx, player_diry, player_planex, player_planey
        global stein_enemies, stein_sprites

        # Player's starting position and orientation
        player_x = 22.0
        player_y = 11.5
        player_dirx = -1.0
        player_diry = 0.0
        player_planex = 0.0
        player_planey = 0.66

        # Enemy data format: (x, y, sprite_index, destroyed_sprite_index)
        stein_enemies = [
            (18.5, 10.5, 1, 3),
            (5.5, 16.5, 1, 3)
        ]
        # Sprite data format: (x, y, sprite_index)
        stein_sprites = [
            (20.5, 11.5, 2), #green light in front of playerstart
            (18.5,4.5, 2),
            (10.0,4.5, 2),
            (10.0,12.5,2),
            (3.5, 6.5, 2),
            (3.5, 20.5,2),
            (3.5, 14.5,2),
            (14.5,20.5,2),
            (1.5,1.5,0),
            (1.5,22.5,0),
            (21.5,1.5,0),
            (21.5,22.5,0),
        ]

    # Exit data format: (x, y, return_value)
    exits = [
        (1.5, 1.5, "Exit 1"),
        (1.5, 22.5, "Exit 2"),
        (21.5, 1.5, "Exit 3"),
        (21.5, 22.5, "Exit 4")
    ]

# The screen that displays the main game engine.
screen stein:
    # This python block runs every time the screen is shown.
    python:
        # Check the persistent quality setting to determine the internal rendering resolution.
        if persistent.performance_mode:
            # Low quality = half resolution (4x faster)
            internal_width = 640
            internal_height = 360
        else:
            # High quality = full resolution
            internal_width = 1280
            internal_height = 720
    
    # Add the Renpystein displayable to the screen.
    # It will read the player and world state from the `default` variables.
    add Renpystein(
        1280, 720,
        worldMap=worldMap,
        exits=exits,
        internal_width=internal_width, 
        internal_height=internal_height
    ):
        xalign 0.5
        yalign 0.3

# The main game label.
# label start:
#     # When a new game starts, reset the game state.
#     python:
#         reset_stein_state()
    
#     "This is a test of Ren'PyStein."
    
#     "Using concepts from the Python code Gh0stenstein, with many thanks to gh0st."
    
#     # Show the UI overlay with controls.
#     show screen stein_controls_overlay
    
#     # Call the game screen. This will display the game until it returns a value (e.g., from an exit).
#     call screen stein

#     "You found exit [_return]!"

#     return