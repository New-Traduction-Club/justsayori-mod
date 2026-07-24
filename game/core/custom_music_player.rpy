default persistent.js_music_player_tutorial_seen = False

init python:
    renpy.music.register_channel("custom_music", mixer="music", loop=True)

init -1 python:
    import os

    def scan_for_music():
        """
        Scans the custom_bgm folder and populates the music list.
        """
        if not hasattr(persistent, 'music_playlist'):
            persistent.music_playlist = []
        if not hasattr(persistent, 'current_song_index') or persistent.current_song_index is None:
            persistent.current_song_index = 0
        if not hasattr(persistent, 'music_is_playing'):
            persistent.music_is_playing = False

        default_songs = [
            {"name": "Daijoubu!", "path": "mod_assets/bgm/Daijoubu.ogg", "author": "Dan Salvato"},
            {"name": "Okay everyone (Sayori)", "path": "mod_assets/bgm/Okay Everyone -Sayori- --- Dan Salvato.ogg", "author": "Dan Salvato"},
            {"name": "My Feelings", "path": "mod_assets/bgm/My Feelings.ogg", "author": "Dan Salvato"},
            {"name": "My Confession", "path": "mod_assets/bgm/My Confession.ogg", "author": "Dan Salvato"},
            {"name": "Ohayou Sayori", "path": "mod_assets/bgm/Ohayou Sayori.ogg", "author": "Dan Salvato"},
            {"name": "Play With Me", "path": "mod_assets/bgm/Play With Me.ogg", "author": "Dan Salvato"}
        ]
        
        all_songs = list(default_songs)
        known_paths = {song['path'] for song in all_songs}

        custom_folder = os.path.join(config.gamedir, 'custom_bgm')

        if os.path.isdir(custom_folder):
            supported_formats = ('.ogg', '.opus', '.mp3', '.wav', '.mp2', '.flac')
            for filename in os.listdir(custom_folder):
                if filename.lower().endswith(supported_formats):
                    song_name = os.path.splitext(filename)[0].replace('_', ' ').title()
                    song_path = "custom_bgm/" + filename

                    if song_path not in known_paths:
                        all_songs.append({"name": song_name, "path": song_path})
                        known_paths.add(song_path)
        
        persistent.music_playlist = all_songs

    def play_music_at_index(index):
        """
        Plays a song from the playlist by its index.

        IN:
            index - int: The position of the song in the playlist.
        """
        if 0 <= index < len(persistent.music_playlist):
            persistent.current_song_index = index
            song = persistent.music_playlist[index]
            renpy.music.play(song['path'], channel="custom_music", loop=True, fadein=1.0)
            persistent.music_is_playing = True

    def stop_custom_music():
        """
        Stops the current custom music playback with a fadeout.
        """
        renpy.music.stop(channel="custom_music", fadeout=1.0)
        persistent.music_is_playing = False

    def toggle_music_pause():
        """
        Pauses or resumes the currently playing song on the custom music channel.
        """
        if renpy.music.get_playing(channel="custom_music"):
            is_paused = renpy.music.get_pause(channel="custom_music")
            renpy.music.set_pause(not is_paused, channel="custom_music")
            persistent.music_is_playing = is_paused
        elif persistent.music_playlist:
            play_music_at_index(persistent.current_song_index)

    def next_song():
        """
        Skips to the next song in the playlist.
        """
        if persistent.music_playlist:
            next_index = (persistent.current_song_index + 1) % len(persistent.music_playlist)
            play_music_at_index(next_index)

    def prev_song():
        """
        Goes to the previous song in the playlist.
        """
        if persistent.music_playlist:
            prev_index = (persistent.current_song_index - 1) % len(persistent.music_playlist)
            play_music_at_index(prev_index)

init 5 python:
    def resume_music_on_start():
        """
        Resumes the last playing song when the game launches if it was playing previously.
        """
        scan_for_music()
        
        if getattr(persistent, 'music_is_playing', False) and persistent.music_playlist:
            index = getattr(persistent, 'current_song_index', 0)
            
            if 0 <= index < len(persistent.music_playlist):
                play_music_at_index(index)
            else:
                play_music_at_index(0)

    config.start_callbacks.append(resume_music_on_start)

## Music Player Screen #################################################
## Provides playing, pausing, and skipping music tracks.
screen modern_music_player():
    zorder 100
    tag menu
    modal True
    
    on "show":
        action Function(scan_for_music)

    default music_adjust = ui.adjustment()

    fixed at fade_in:
        area (980, 70, 250, 572)
        
        bar:
            adjustment music_adjust
            style "sayo_scroller"
            xalign -0.1
        
        vbox:
            ypos 0
            yanchor 0
            
            viewport:
                yadjustment music_adjust
                yfill False
                mousewheel True
                
                has vbox:
                    spacing 5
                
                if not persistent.music_playlist:
                    textbutton _("No songs found") style "t_m_button" action None
                else:
                    for i, song in enumerate(persistent.music_playlist):
                        textbutton song["name"]:
                            style "t_m_button"
                            action [Function(play_music_at_index, index=i), Return()]
                            hover_sound gui.hover_sound
                            activate_sound gui.activate_sound
                
                null height 10
                
                textbutton _("No music"):
                    style "t_m_button"
                    action [Function(stop_custom_music), Return()]
                    hover_sound gui.hover_sound
                    activate_sound gui.activate_sound
                    
                null height 10
                
                textbutton _("Close"):
                    style "t_m_button"
                    action Return()
                    hover_sound gui.hover_sound
                    activate_sound gui.activate_sound

style music_player_frame:
    background Solid("#1a1a1ae0")
    padding (30, 30)
    xsize 1100
    ysize 620

style music_player_vbox:
    spacing 15
    xsize 680

style music_player_title:
    size 36
    color "#ffffff"
    font "mod_assets/fonts/Fantasque/FantasqueSansMono-Bold.ttf"
    xalign 0.5
    bottom_margin 10

style music_list_viewport:
    xsize 680
    ysize 400

style music_list_vbox:
    spacing 8

style music_button is default:
    xsize 660
    background Solid("#00000040")
    hover_background Solid("#ffffff20")

style music_button_text is button_text:
    size 20
    color "#e0e0e0"
    hover_color "#ffbde1"
    font "mod_assets/fonts/Fantasque/FantasqueSansMono-Regular.ttf"

style music_button_text_playing is music_button_text:
    color "#f988c5"
    bold True

style music_controls_hbox:
    spacing 0
    xalign 0.5
    yalign 0.5
    top_margin 10

style music_control_button is button:
    background None
    hover_background None

style music_control_button_text is button_text:
    size 32
    color "#e0e0e0"
    hover_color "#f988c5"

style music_player_close_button:
    xalign 0.5
    top_margin 20
    background Solid("#00000040")
    hover_background Solid("#ffffff20")
    padding (14, 12)

style music_player_close_button_text is music_button_text:
    size 22

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
