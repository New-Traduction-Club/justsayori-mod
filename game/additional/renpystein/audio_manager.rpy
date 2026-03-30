init python:
    renpy.music.register_channel("stein_music", mixer="music", loop=True)

    class js_SteinAudioManager:
        """
        Dedicated audio manager for the Sayoristein minigame.
        Handles the transition between main game music and minigame music,
        and allows independent volume control.
        """
        def __init__(self):
            self.was_main_music_playing = False
            
            self.tracks = {
                "menu": "sounds/music/main-menu.ogg",
                "level_1": "", # TODO: Add other music for levels
                "level_2": "",
                "level_3": "",
                "arena": "sounds/music/arena.ogg",
            }

        def enter_minigame(self):
            if renpy.music.get_playing(channel="custom_music") or getattr(persistent, "music_is_playing", False):
                self.was_main_music_playing = True
                
                if hasattr(store, 'stop_custom_music'):
                    stop_custom_music()
                else:
                    renpy.music.stop(channel="custom_music", fadeout=1.0)
            else:
                self.was_main_music_playing = False
            
            self.update_volume()

        def exit_minigame(self):
            renpy.music.stop(channel="stein_music", fadeout=1.0)
            
            if self.was_main_music_playing:
                if hasattr(store, 'play_music_at_index') and hasattr(persistent, 'current_song_index'):
                    renpy.music.queue(
                        store.persistent.music_playlist[store.persistent.current_song_index]['path'], 
                        channel="custom_music", 
                        loop=True, 
                        fadein=2.0
                    )
                    store.persistent.music_is_playing = True

        def play(self, track_key, fadein=1.0, fadeout=1.0):
            file_path = self.tracks.get(track_key)
            
            if file_path and file_path != "mod_assets/bgm/..." and renpy.loadable(file_path):
                renpy.music.play(file_path, channel="stein_music", loop=True, fadein=fadein, fadeout=fadeout)
                self.update_volume()
            else:
                pass 

        def stop(self, fadeout=1.0):
            renpy.music.stop(channel="stein_music", fadeout=fadeout)

        def update_volume(self):
            vol = getattr(persistent, "stein_music_volume", 0.7)
            renpy.music.set_volume(vol, channel="stein_music")

default js_stein_audio = js_SteinAudioManager()

init python:
    if getattr(persistent, "stein_music_volume", None) is None:
        persistent.stein_music_volume = 0.7 
