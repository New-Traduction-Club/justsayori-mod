init -999 python:

    renpy.config.allow_skipping = True














define config.name = "Just Sayori"



define gui.show_name = True


define config.version = "1.0.1"



define gui.about = _("")






define build.name = "JustSayori"


define config.has_sound = True


define config.has_music = True


define config.has_voice = False

define config.rollback_enabled = False



define config.main_menu_music = audio.s1






define config.enter_transition = Dissolve(.2)
define config.exit_transition = Dissolve(.2)


define config.after_load_transition = None


define config.end_game_transition = Dissolve(.5)





define config.window = "auto"





define config.window_show_transition = Dissolve(.2)
define config.window_hide_transition = Dissolve(.2)


default preferences.text_cps = 50


default preferences.afm_time = 15


default preferences.music_volume = 0.75
default preferences.sfx_volume = 0.75






define config.save_directory = "JustSayori"



define config.window_icon = "gui/window_icon.png"



define config.has_autosave = False


define config.autosave_on_quit = False


define config.autosave_slots = 0


define config.rollback_enabled = config.developer



define config.layers = [ 'master', 'transient', 'screens', 'overlay', 'front' ]
define config.image_cache_size = 64
define config.predict_statements = 50
define config.menu_clear_layers = ["front"]
define config.gl_test_image = "white"

init python:
    if len(renpy.loadsave.location.locations) > 1: del(renpy.loadsave.location.locations[1])
    renpy.game.preferences.pad_enabled = False
    def replace_text(s):
        s = s.replace('--', u'\u2014') 
        s = s.replace(' - ', u'\u2014') 
        return s
    config.replace_text = replace_text

    def game_menu_check():
        if quick_menu: renpy.call_in_new_context('_game_menu')

    config.game_menu_action = game_menu_check

    def force_integer_multiplier(width, height):
        if float(width) / float(height) < float(config.screen_width) / float(config.screen_height):
            return (width, float(width) / (float(config.screen_width) / float(config.screen_height)))
        else:
            return (float(height) * (float(config.screen_width) / float(config.screen_height)), height)



    def saveIco(filepath):
        import pygame_sdl2
        
        bmp = os.path.join(renpy.config.basedir, "icon.bmp").replace("\\", "/")
        ico = os.path.join(renpy.config.basedir, "icon.ico").replace("\\", "/")
        
        surf = pygame_sdl2.image.load(os.path.join(
                renpy.config.gamedir, filepath
                ).replace("\\", "/")
            )
        trans = pygame_sdl2.transform.scale(surf, (64, 64))
        pygame_sdl2.image.save(trans, bmp)
        
        if os.path.exists(ico):
            os.remove(ico)
        
        os.rename(os.path.join(renpy.config.basedir, "icon.bmp").replace("\\", "/"), 
            os.path.join(renpy.config.basedir, "icon.ico").replace("\\", "/"))
        
        renpy.show_screen("dialog", message="Exported your mod logo as a icon successfully.", ok_action=Hide("dialog"))





init python:

    # check this













    build.classify('**.bak', None)
    build.classify('**/thumbs.db', None)
    build.classify('**.rpy', None)
    build.classify('**~', None)
    build.classify('**/.**', None)
    build.classify('**/#**', None)    
    build.classify('**.psd', None)
    build.classify('**.sublime-project', None)
    build.classify('**.sublime-workspace', None)
    build.classify('script-regex.txt', None)
    build.classify('/game/10', None)
    build.classify('/game/cache/*.*', None)
    build.classify('**.rpa', None)
    build.classify("game/dev/**", None)
    build.classify('gifts/*', None)
    build.classify('game/submods/*', None)
    build.classify("log/**", None)
    build.classify("*.log", None)
    build.classify("errors.txt", None)
    build.classify("log.txt", None)
    build.classify("game/dev.txt", None)

    build.classify("game/bgm/**", None)
    build.classify('/music/*.*', None)
    build.classify("game/bgm/**", None)

    # this
    build.include_update = False

    # this
    build.classify("game/mod_assets/**", "all")
    build.classify("game/**.rpyc", "all")
    build.classify("game/gui/**", "all")
    build.classify("game/python-packages/**", "all")
    build.classify('README.html', "all")
    build.classify("game/RPASongMetadata.json", "all")
    build.classify("renpy/**", "all")
    build.classify("lib/**", "all")







    build.package(build.directory_name + "Mod", 'zip', "all", description="Ren'Py 8 DDLC Compliant Mod")


































    build.include_old_themes = False
