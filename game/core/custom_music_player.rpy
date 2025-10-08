default persistent.js_music_player_tutorial_seen = False

# Defines a dedicated audio channel for the music player to avoid conflicts
init python:
    renpy.music.register_channel("custom_music", mixer="music", loop=True)

init -1 python:
    import os

    # Function to scan and load songs
    def scan_for_music():
        # Ensures that persistent variables exist
        if not hasattr(persistent, 'music_playlist'):
            persistent.music_playlist = []
        if not hasattr(persistent, 'current_song_index') or persistent.current_song_index is None:
            persistent.current_song_index = 0
        if not hasattr(persistent, 'music_is_playing'):
            persistent.music_is_playing = False

        ##### Default Songs
        # These are the songs that will be included in the mod
        default_songs = [
            {"name": "Daijoubu!", "path": "mod_assets/bgm/Daijoubu.ogg", "author": "Dan Salvato"},
            {"name": "Okay everyone (Sayori)", "path": "mod_assets/bgm/Okay Everyone -Sayori- --- Dan Salvato.ogg", "author": "Dan Salvato"},
            {"name": "My Feelings", "path": "mod_assets/bgm/My Feelings.ogg", "author": "Dan Salvato"},
            {"name": "My Confession", "path": "mod_assets/bgm/My Confession.ogg", "author": "Dan Salvato"},
            {"name": "Ohayou Sayori", "path": "mod_assets/bgm/Ohayou Sayori.ogg", "author": "Dan Salvato"},
            {"name": "Play With Me", "path": "mod_assets/bgm/Play With Me.ogg", "author": "Dan Salvato"},
            {"name": "For my Rush", "path": "mod_assets/bgm/For my Rush.ogg", "author": "just6889"},
            {"name": "Luna de miel", "path": "mod_assets/bgm/Luna de miel.ogg", "author": "just6889"},
            {"name": "My new start", "path": "mod_assets/bgm/My new start.ogg", "author": "just6889"},
            {"name": "Our Future", "path": "mod_assets/bgm/Our Future.ogg", "author": "just6889"}
        ]
        
        all_songs = list(default_songs)
        known_paths = {song['path'] for song in all_songs}

        # Search in the custom folder
        # only in /game/custom_bgm
        custom_folder = os.path.join(config.gamedir, 'custom_bgm')

        if os.path.isdir(custom_folder):
            # Ren'Py supports .ogg, .opus, .mp3, and .wav for music channels
            supported_formats = ('.ogg', '.opus', '.mp3', '.wav', '.mp2', '.flac')
            for filename in os.listdir(custom_folder):
                if filename.lower().endswith(supported_formats):
                    # Generates a readable song name from the filename
                    song_name = os.path.splitext(filename)[0].replace('_', ' ').title()
                    
                    # Builds the relative path that Renpy can use
                    song_path = "custom_bgm/" + filename

                    if song_path not in known_paths:
                        # Custom songs wontt have an author key, it will be handled in the screen
                        all_songs.append({"name": song_name, "path": song_path})
                        known_paths.add(song_path)
        
        persistent.music_playlist = all_songs

    # Music Control Functions (Now using the 'custom_music' channel)
    def play_music_at_index(index):
        """Plays a song from the list by its index."""
        if 0 <= index < len(persistent.music_playlist):
            persistent.current_song_index = index
            song = persistent.music_playlist[index]
            renpy.music.play(song['path'], channel="custom_music", loop=True, fadein=1.0)
            persistent.music_is_playing = True

    def stop_custom_music():
        """Stops the music with a fadeout."""
        renpy.music.stop(channel="custom_music", fadeout=1.0)
        persistent.music_is_playing = False

    def toggle_music_pause():
        """Pauses or resumes the current song."""
        if renpy.music.get_playing(channel="custom_music"):
            is_paused = renpy.music.get_pause(channel="custom_music")
            renpy.music.set_pause(not is_paused, channel="custom_music")
            persistent.music_is_playing = is_paused
        elif persistent.music_playlist:
            play_music_at_index(persistent.current_song_index)

    def next_song():
        """Skips to the next song in the list."""
        if persistent.music_playlist:
            next_index = (persistent.current_song_index + 1) % len(persistent.music_playlist)
            play_music_at_index(next_index)

    def prev_song():
        """Goes to the previous song in the list."""
        if persistent.music_playlist:
            prev_index = (persistent.current_song_index - 1) % len(persistent.music_playlist)
            play_music_at_index(prev_index)

init 5 python:
    def resume_music_on_start():
        """
        Scans for music and resumes the last played song if music was playing
        when the game was last closed.
        """
        # Eensure the playlist is loaded from files
        scan_for_music()
        
        # Check if music was playing and if theres a playlist
        if getattr(persistent, 'music_is_playing', False) and persistent.music_playlist:
            index = getattr(persistent, 'current_song_index', 0)
            
            # Check if the saved index is valid for the current playlist
            if 0 <= index < len(persistent.music_playlist):
                play_music_at_index(index)
            # If the index is invalid (e.g., songs were removed), just play the first song
            else:
                play_music_at_index(0)

    # Register the function to be called when the game starts
    config.start_callbacks.append(resume_music_on_start)

##### Styles for the Modern UI

# The main container
style music_player_frame:
    background Solid("#1a1a1ae0")
    padding (30, 30)
    xsize 1100
    ysize 620

# VBox for the left column (playlist)
style music_player_vbox:
    spacing 15
    xsize 680 # Width for the left column

# The title "Music Player"
style music_player_title:
    size 36
    color "#ffffff"
    font "mod_assets/fonts/Fantasque/FantasqueSansMono-Bold.ttf"
    xalign 0.5
    bottom_margin 10

# The song list viewport
style music_list_viewport:
    xsize 680
    ysize 400

style music_list_vbox:
    spacing 8

# Styles for the song buttons
style music_button is default:
    xsize 660 # Adjusted for new viewport width
    background Solid("#00000040")
    hover_background Solid("#ffffff20")

style music_button_text is button_text:
    size 20
    color "#e0e0e0"
    hover_color "#ffbde1"
    font "mod_assets/fonts/Fantasque/FantasqueSansMono-Regular.ttf"

# Special style for the currently playing song
style music_button_text_playing is music_button_text:
    color "#f988c5"
    bold True

# Container for the control buttons
style music_controls_hbox:
    spacing 0
    xalign 0.5
    yalign 0.5
    top_margin 10

# Styles for the control buttons
style music_control_button is button:
    background None
    hover_background None

style music_control_button_text is button_text:
    size 32
    color "#e0e0e0"
    hover_color "#f988c5"

# Style for the close button
style music_player_close_button:
    xalign 0.5
    top_margin 20
    background Solid("#00000040")
    hover_background Solid("#ffffff20")
    padding (14, 12)

style music_player_close_button_text is music_button_text:
    size 22

# For the Right Column
style song_info_vbox:
    xalign 0.5
    yalign 0.5
    spacing 10
    xfill True

style song_image_placeholder:
    background Solid("#00000080")
    xsize 300
    ysize 300
    xalign 0.5
    bottom_margin 20

style song_info_title:
    size 28
    color "#ffffff"
    font "mod_assets/fonts/Fantasque/FantasqueSansMono-Bold.ttf"
    text_align 0.5
    xalign 0.5

style song_info_author:
    size 22
    color "#e0e0e0"
    font "mod_assets/fonts/Fantasque/FantasqueSansMono-Regular.ttf"
    text_align 0.5
    xalign 0.5

##### Animations and Transforms
transform music_button_hover:
    on hover:
        ease 0.15 xoffset 5
    on idle:
        ease 0.2 xoffset 0

transform music_ui_pop:
    on show:
        alpha 0.0
        yoffset 50
        easein 0.5 alpha 1.0 yoffset 0
    on hide:
        easeout 0.3 alpha 0.0 yoffset 50

# Main screen
screen modern_music_player():
    zorder 100
    tag menu
    modal True
    
    # Scans for music every time the screen is opened
    on "show":
        action Function(scan_for_music)

    add Solid("#000000cc")
    
    # Define current song variable for easier access
    $ current_song = persistent.music_playlist[persistent.current_song_index] if persistent.music_playlist and 0 <= persistent.current_song_index < len(persistent.music_playlist) else None

    # Main frame with the enter/leave animation
    frame style "music_player_frame" xalign 0.5 yalign 0.5 at music_ui_pop:
        
        # Hbox for the two-column layout
        hbox:
            ##### Left Column: Playlist and Controls
            vbox style "music_player_vbox":
                
                text _("Music Player") style "music_player_title"

                # Scrollable song list
                viewport style "music_list_viewport" scrollbars "vertical" mousewheel True:
                    vbox style "music_list_vbox":
                        if not persistent.music_playlist:
                            text "No songs found.\nAdd .ogg, .opus, .mp3, .wav, or .flac files\nto the 'game/custom_bgm' folder." style "music_button_text" xalign 0.5
                        else:
                            for i, song in enumerate(persistent.music_playlist):
                                # Determines if this is the currently playing song on our custom channel
                                $ is_playing = renpy.music.get_playing(channel="custom_music") and persistent.current_song_index == i
                                
                                # Construct the button text with a prefix if it's the current song
                                $ button_text = song["name"]

                                # Creates the button for the song
                                textbutton button_text action Function(play_music_at_index, index=i) style "music_button":
                                    if is_playing:
                                        text_style "music_button_text_playing"
                                    else:
                                        text_style "music_button_text"
                                    at music_button_hover

                # Playback Controls
                hbox style "music_controls_hbox":
                    textbutton "⏮" action Function(prev_song) style "music_control_button" text_style "music_control_button_text"
                    
                    if renpy.music.get_playing(channel="custom_music") and not renpy.music.get_pause(channel="custom_music"):
                        textbutton "⏸︎" action Function(toggle_music_pause) style "music_control_button" text_style "music_control_button_text" xpos 14
                    else:
                        textbutton "▶︎" action Function(toggle_music_pause) style "music_control_button" text_style "music_control_button_text" xpos 14

                    textbutton "■" action Function(stop_custom_music) style "music_control_button" text_style "music_control_button_text"
                    textbutton "⏭" action Function(next_song) style "music_control_button" text_style "music_control_button_text"

                # Button to close the screen
                textbutton _("Close") action Hide("modern_music_player") style "music_player_close_button" text_style "music_player_close_button_text"

            ##### Right Column: Song Art and Info
            vbox style "song_info_vbox":
                if current_song:
                    add "pedro"

                    # Current song title
                    text current_song["name"] style "song_info_title"
                    
                    # Current song author, with a fallback for custom songs
                    text "by [current_song.get('author', 'Unknown Artist')]" style "song_info_author"
                else:
                    # Displayed when the playlist is empty
                    frame style "song_image_placeholder"
                    text "Select a song" style "song_info_title"

image pedro:
    Animation(
        "mod_assets/videos/pedro/ezgif-frame-001.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-002.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-003.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-004.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-005.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-006.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-007.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-008.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-009.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-010.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-011.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-012.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-013.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-014.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-015.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-016.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-017.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-018.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-019.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-020.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-021.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-022.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-023.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-024.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-025.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-026.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-027.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-028.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-029.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-030.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-031.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-032.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-033.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-034.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-035.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-036.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-037.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-038.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-039.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-040.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-041.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-042.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-043.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-044.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-045.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-046.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-047.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-048.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-049.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-050.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-051.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-052.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-053.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-054.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-055.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-056.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-057.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-058.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-059.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-060.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-061.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-062.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-063.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-064.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-065.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-066.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-067.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-068.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-069.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-070.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-071.png", 0.09,
        "mod_assets/videos/pedro/ezgif-frame-072.png", 0.09,
    )