
label start:

    # scene black
    # with dissolve_scene_full


    $ anticheat = persistent.anticheat


    $ chapter = 0


    $ _dismiss_pause = config.developer






    $ m_name = "Girl 3"
    $ n_name = "Girl 2"
    $ y_name = "Girl 1"


    $ quick_menu = True



    $ style.say_dialogue = style.normal



    $ in_sayori_kill = None


    $ allow_skipping = True
    $ config.allow_skipping = True



    if persistent.autoload:
        stop music
        jump ch30_setup

    jump ch30_main

label endgame(pause_length=4.0):
    $ quick_menu = False
    stop music fadeout 2.0
    scene black
    show end
    with dissolve_scene_full
    pause pause_length
    $ quick_menu = True
    return
