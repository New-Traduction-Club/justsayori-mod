# RenPyStein - In-Game UI Overlay

# This screen displays on top of the main game screen (stein).
screen stein_controls_overlay():
    style_prefix "stein_controls_overlay"
    # zorder 100 ensures this UI is always drawn on top of the 3D game world.
    zorder 100

    # A horizontal box (hbox) to arrange the buttons.
    hbox:
        xalign 0.01  # Align to the top-left corner
        yalign 0.01
        spacing 10   # Space between buttons

        # Button to switch to Keyboard mode.
        if not renpy.android:
            textbutton _("Keyboard & Gamepad") action SetVariable("simulate_touch", False)
        
        # Button to switch to Touch/Mouse mode.
        if renpy.android:
            textbutton _("Touch & Gamepad") action SetVariable("simulate_touch", True)

    if persistent.stein_show_fps:
        text "FPS: [stein_current_fps]":
            xalign 0.98
            yalign 0.02
            size 30
            color "#607567"
            outlines [(2, "#000000", 0, 0)]
            font "mod_assets/fonts/BebasNeue-Regular.ttf"

# Style for the text inside the buttons on this screen.
style stein_controls_overlay_textbutton_text:
    size 20
    idle_color "#ffffff"  # White text
    hover_color "#00ff00" # Green text on hover

style sayoristein_menu_button_text is button_text:
    xalign 0.5
    yalign 0.5
    font "mod_assets/fonts/BebasNeue-Regular.ttf"

style sayoristein_menu_button is default:
    background Frame("pics/gui/button_bg.png")
    xalign 0.5
    yalign 0.5
    xsize 250
    ysize 75

style stein_settings_header:
    font "mod_assets/fonts/BebasNeue-Regular.ttf"
    size 32
    color "#AAAAAA"
    xalign 0.5
    text_align 0.5

style stein_settings_label:
    font "mod_assets/fonts/BebasNeue-Regular.ttf"
    size 26
    color "#FFFFFF"
    xalign 0.5
    text_align 0.5

style stein_tab_button is sayoristein_menu_button:
    xsize 200
    ysize 60

screen sayoristein_menu():
    tag menu

    add "pics/gui/main_menu.png"

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 15

        textbutton _("Play") action ShowMenu("sayoristein_level_select") style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"
        textbutton _("Settings") action ShowMenu("sayoristein_settings_menu") style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"
        textbutton _("Exit") action Return() style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"

screen sayoristein_settings_menu():
    tag menu
    modal True
    
    default current_tab = "graphics"

    add "pics/gui/main_menu_bg.png"

    text "SETTINGS":
        font "mod_assets/fonts/BebasNeue-Regular.ttf"
        size 70
        color "#ffffff"
        xalign 0.5
        yalign 0.03
        outlines [(4, "#000", 0, 0)]

    hbox:
        xalign 0.5
        yalign 0.14 
        spacing 15
        
        textbutton _("Graphics"):
            action SetScreenVariable("current_tab", "graphics")
            style "stein_tab_button"
            text_color ("#00FF00" if current_tab == "graphics" else "#FFFFFF")
            text_style "sayoristein_menu_button_text"

        textbutton _("Controls"):
            action SetScreenVariable("current_tab", "controls")
            style "stein_tab_button"
            text_color ("#00FF00" if current_tab == "controls" else "#FFFFFF")
            text_style "sayoristein_menu_button_text"

        textbutton _("Gameplay"):
            action SetScreenVariable("current_tab", "gameplay")
            style "stein_tab_button"
            text_color ("#00FF00" if current_tab == "gameplay" else "#FFFFFF")
            text_style "sayoristein_menu_button_text"

    frame:
        background None
        xalign 0.5
        yalign 0.8
        xsize 1100
        ysize 500
        
        viewport id "settings_vp":
            scrollbars "vertical"
            mousewheel True
            draggable True
            pagekeys True
            yinitial 0.0
            
            vbox:
                xalign 0.5
                spacing 25
                xsize 1080

                if current_tab == "graphics":
                    vbox:
                        spacing 10
                        xalign 0.5
                        text _("Resolution") style "stein_settings_header"
                        
                        hbox:
                            spacing 15
                            xalign 0.5
                            textbutton _("High") action SetVariable("persistent.stein_quality_mode", 0) style "sayoristein_menu_button" text_style "sayoristein_menu_button_text" text_size 22
                            textbutton _("Low") action SetVariable("persistent.stein_quality_mode", 1) style "sayoristein_menu_button" text_style "sayoristein_menu_button_text" text_size 22
                            textbutton _("Ultra Low") action SetVariable("persistent.stein_quality_mode", 2) style "sayoristein_menu_button" text_style "sayoristein_menu_button_text" text_size 22
                        hbox:
                            spacing 15
                            xalign 0.5
                            textbutton _("MS Paint is Better") action SetVariable("persistent.stein_quality_mode", 3) style "sayoristein_menu_button" text_style "sayoristein_menu_button_text" text_size 22
                            textbutton _("Bro, can you see?") action SetVariable("persistent.stein_quality_mode", 4) style "sayoristein_menu_button" text_style "sayoristein_menu_button_text" text_size 22

                    null height 10
                    
                    vbox:
                        spacing 10
                        xalign 0.5
                        text _("Post-Processing") style "stein_settings_header"
                        
                        textbutton ("Bloom Effect: " + ("ON" if persistent.stein_enable_bloom else "OFF")):
                            action ToggleVariable("persistent.stein_enable_bloom")
                            style "sayoristein_menu_button"
                            text_style "sayoristein_menu_button_text"

                        textbutton ("Soft Shadows: " + ("ON" if persistent.stein_soft_shadows else "OFF")):
                            action ToggleVariable("persistent.stein_soft_shadows")
                            style "sayoristein_menu_button"
                            text_style "sayoristein_menu_button_text"

                        # textbutton ("Heat Distortion: " + ("ON" if persistent.stein_heat_distortion else "OFF")):
                        #     action ToggleVariable("persistent.stein_heat_distortion")
                        #     style "sayoristein_menu_button"
                        #     text_style "sayoristein_menu_button_text"

                    null height 10

                    vbox:
                        spacing 5
                        xalign 0.5
                        text _("Motion Blur Strength: [int(persistent.stein_motion_blur_strength * 100)]%") style "stein_settings_label"
                        bar value FieldValue(persistent, "stein_motion_blur_strength", range=1.0, step=0.05):
                            xalign 0.5
                            xsize 600
                            ysize 45
                            left_bar Frame("pics/gui/button_bg.png", 10, 10)
                            right_bar Frame("pics/gui/button_bg.png", 10, 10)
                            thumb Frame("pics/gui/bar_thumb.png", 10, 10)
                    
                    null height 50

                elif current_tab == "controls":
                    hbox:
                        spacing 80
                        xalign 0.5
                        vbox:
                            spacing 15
                            xsize 400
                            text _("Mouse & Keyboard") style "stein_settings_header"
                            text _("Sensitivity: [persistent.stein_mouse_sens:.2f]") style "stein_settings_label"
                            bar value FieldValue(persistent, "stein_mouse_sens", range=3.0, step=0.1):
                                xalign 0.5
                                xsize 350
                                ysize 35
                                left_bar Frame("pics/gui/button_bg.png", 10, 10)
                                right_bar Frame("pics/gui/button_bg.png", 10, 10)
                                thumb Frame("pics/gui/bar_thumb.png", 10, 10)

                        vbox:
                            spacing 15
                            xsize 400
                            text _("Gamepad (Controller)") style "stein_settings_header"
                            text _("Horiz. Sensitivity: [persistent.stein_gamepad_sens_x:.2f]") style "stein_settings_label"
                            bar value FieldValue(persistent, "stein_gamepad_sens_x", range=3.0, step=0.1):
                                xalign 0.5
                                xsize 350
                                ysize 35
                                left_bar Frame("pics/gui/button_bg.png", 10, 10)
                                right_bar Frame("pics/gui/button_bg.png", 10, 10)
                                thumb Frame("pics/gui/bar_thumb.png", 10, 10)

                            text _("Vert. Sensitivity: [persistent.stein_gamepad_sens_y:.2f]") style "stein_settings_label"
                            bar value FieldValue(persistent, "stein_gamepad_sens_y", range=3.0, step=0.1):
                                xalign 0.5
                                xsize 350
                                ysize 35
                                left_bar Frame("pics/gui/button_bg.png", 10, 10)
                                right_bar Frame("pics/gui/button_bg.png", 10, 10)
                                thumb Frame("pics/gui/bar_thumb.png", 10, 10)

                    null height 50

                elif current_tab == "gameplay":
                    vbox:
                        xalign 0.5
                        spacing 30
                        
                        vbox:
                            spacing 5
                            xalign 0.5
                            text _("Music Volume: [int(persistent.stein_music_volume * 100)]%") style "stein_settings_label"
                            bar value FieldValue(persistent, "stein_music_volume", range=1.0, step=0.05, action=Function(js_stein_audio.update_volume)):
                                xalign 0.5
                                xsize 600
                                ysize 45
                                left_bar Frame("pics/gui/button_bg.png", 10, 10)
                                right_bar Frame("pics/gui/button_bg.png", 10, 10)
                                thumb Frame("pics/gui/bar_thumb.png", 10, 10)

                        vbox:
                            spacing 5
                            xalign 0.5
                            textbutton ("Show FPS Counter: [persistent.stein_show_fps]"):
                                action ToggleVariable("persistent.stein_show_fps")
                                style "sayoristein_menu_button"
                                text_style "sayoristein_menu_button_text"
                                xalign 0.5
                            
                            text _("Shows frames per second in top-right corner") font "mod_assets/fonts/BebasNeue-Regular.ttf" size 18 color "#888" xalign 0.5
                    
                    null height 50

    textbutton _("Back") action ShowMenu("sayoristein_menu") style "sayoristein_menu_button" text_style "sayoristein_menu_button_text":
        xalign 0.5
        yalign 0.96


screen sayoristein_level_select():
    tag menu

    add "pics/gui/main_menu_bg.png"

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 15

        textbutton _("Level 1") action Jump("start_level_1") style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"
        
        if persistent.stein_level1_cleared:
            textbutton _("Level 2") action Jump("start_level_2") style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"
        else:
            textbutton _("Level 2 (Locked)") action Show("stein_locked_message", msg=__("Complete Level 1 first!")) style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"
        
        if persistent.stein_level2_cleared:
            textbutton _("Level 3") action Jump("start_level_3") style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"
        else:
            textbutton _("Level 3 (Locked)") action Show("stein_locked_message", msg=__("Complete Level 2 first!")) style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"
        
        if persistent.stein_level3_cleared:
            textbutton _("Arena Mode") action ShowMenu("sayoristein_arena_hub") style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"
        else:
            textbutton _("Arena Mode (Locked)") action Show("stein_locked_message", msg=__("Complete Level 3 to unlock Arena!")) style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"

        textbutton _("Back") action ShowMenu("sayoristein_menu") style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"

screen sayoristein_arena_hub():
    tag menu
    add "pics/gui/main_menu_bg.png"

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 15

        label _("ARENA MODE") style "sayoristein_menu_button_text" text_style "sayoristein_menu_button_text":
            xalign 0.5

        textbutton _("Start Arena") action Jump("start_level_4_arena") style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"
        textbutton _("Upgrades") action ShowMenu("sayoristein_upgrades") style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"
        textbutton _("Back") action ShowMenu("sayoristein_level_select") style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"

init python:
    if getattr(persistent, "stein_motion_blur_strength", None) is None:
        persistent.stein_motion_blur_strength = 0.0
    
    if getattr(persistent, "stein_soft_shadows", None) is None:
        persistent.stein_soft_shadows = True

    if getattr(persistent, "stein_flashlight_shadows", None) is None:
        persistent.stein_flashlight_shadows = False

    if getattr(persistent, "stein_heat_distortion", None) is None:
        persistent.stein_heat_distortion = True

    def buy_stein_upgrade(upgrade_type):
        if upgrade_type == "pistol":
            cost = 1000 + (persistent.stein_pistol_level * 100)
            if persistent.tradu_coins >= cost:
                persistent.tradu_coins -= cost
                persistent.stein_pistol_level += 1
                renpy.restart_interaction()
            else:
                renpy.show_screen("stein_locked_message", msg=__("Not enough Tradu-Coins!"))

        elif upgrade_type == "shotgun":
            cost = 1000 + (persistent.stein_shotgun_level * 100)
            if persistent.tradu_coins >= cost:
                persistent.tradu_coins -= cost
                persistent.stein_shotgun_level += 1
                renpy.restart_interaction()
            else:
                renpy.show_screen("stein_locked_message", msg=__("Not enough Tradu-Coins!"))
        
        elif upgrade_type == "unlock_shotgun":
            cost = 25000
            if persistent.tradu_coins >= cost:
                persistent.tradu_coins -= cost
                persistent.stein_shotgun_unlocked = True
                renpy.restart_interaction()
            else:
                renpy.show_screen("stein_locked_message", msg=__("Not enough Tradu-Coins!"))

        elif upgrade_type == "minigun":
            cost = 50 + (persistent.stein_minigun_level * 15)
            if persistent.tradu_coins >= cost:
                persistent.tradu_coins -= cost
                persistent.stein_minigun_level += 1
                renpy.restart_interaction()
            else:
                renpy.show_screen("stein_locked_message", msg=__("Not enough Tradu-Coins!"))

        elif upgrade_type == "unlock_minigun":
            cost = 50000
            if persistent.tradu_coins >= cost:
                persistent.tradu_coins -= cost
                persistent.stein_minigun_unlocked = True
                renpy.restart_interaction()
            else:
                renpy.show_screen("stein_locked_message", msg=__("Not enough Tradu-Coins!"))

screen sayoristein_upgrades():
    tag menu
    add "pics/gui/main_menu_bg.png"

    # Header
    hbox:
        xalign 0.5
        yalign 0.05
        spacing 50
        text _("Sayo-Forge") size 60 color "#ffffff" font "mod_assets/fonts/BebasNeue-Regular.ttf"
        text _("Coins: [persistent.tradu_coins]") size 40 color "#ffff00" font "mod_assets/fonts/BebasNeue-Regular.ttf" yalign 0.5

    viewport id "stein_upgrades_vp":
        xalign 0.5
        yalign 0.5
        xsize 1200
        ysize 500
        scrollbars "vertical"
        mousewheel True
        draggable True
        pagekeys True

        hbox:
            xalign 0.5
            spacing 50

            vbox:
                spacing 10
                xalign 0.5
                xsize 365
                
                add "pics/items/bullet.png":
                    xalign 0.5
                    zoom 2.0
                
                text _("Pistol") xalign 0.5 size 30 color "#ffffff" font "mod_assets/fonts/BebasNeue-Regular.ttf"
                
                $ p_dmg_bonus = persistent.stein_pistol_level * 1
                text _("Level: [persistent.stein_pistol_level]") xalign 0.5 size 24 color "#aaaaaa" font "mod_assets/fonts/BebasNeue-Regular.ttf"
                text _("Bonus: +[p_dmg_bonus]% Dmg") xalign 0.5 size 24 color "#00ff00" font "mod_assets/fonts/BebasNeue-Regular.ttf"
                
                $ p_cost = 1000 + (persistent.stein_pistol_level * 100)
                textbutton _("Upgrade ([p_cost])") action Function(buy_stein_upgrade, "pistol") style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"

            vbox:
                spacing 10
                xalign 0.5
                xsize 365
                
                add "pics/items/bullet.png":
                    xalign 0.5
                    zoom 2.0
                
                text _("Shotgun") xalign 0.5 size 30 color "#ffffff" font "mod_assets/fonts/BebasNeue-Regular.ttf"
                
                $ s_dmg_bonus = persistent.stein_shotgun_level * 1
                text _("Level: [persistent.stein_shotgun_level]") xalign 0.5 size 24 color "#aaaaaa" font "mod_assets/fonts/BebasNeue-Regular.ttf"
                text _("Bonus: +[s_dmg_bonus]% Dmg") xalign 0.5 size 24 color "#00ff00" font "mod_assets/fonts/BebasNeue-Regular.ttf"
                
                $ s_cost = 1000 + (persistent.stein_shotgun_level * 100)
                textbutton _("Upgrade ([s_cost])") action Function(buy_stein_upgrade, "shotgun") style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"

                if not persistent.stein_shotgun_unlocked:
                    text _("NOT OWNED") xalign 0.5 size 20 color "#ff0000" font "mod_assets/fonts/BebasNeue-Regular.ttf"
                    textbutton _("Unlock (25000)") action Function(buy_stein_upgrade, "unlock_shotgun") style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"

            vbox:
                spacing 10
                xalign 0.5
                xsize 365
                
                add "pics/items/bullet.png":
                    xalign 0.5
                    zoom 2.0
                
                text _("Minigun") xalign 0.5 size 30 color "#ffffff" font "mod_assets/fonts/BebasNeue-Regular.ttf"
                
                $ m_dmg_bonus = persistent.stein_minigun_level * 10
                text _("Level: [persistent.stein_minigun_level]") xalign 0.5 size 24 color "#aaaaaa" font "mod_assets/fonts/BebasNeue-Regular.ttf"
                text _("Bonus: +[m_dmg_bonus]% Dmg") xalign 0.5 size 24 color "#00ff00" font "mod_assets/fonts/BebasNeue-Regular.ttf"
                
                $ m_cost = 50 + (persistent.stein_minigun_level * 15)
                textbutton _("Upgrade ([m_cost])") action Function(buy_stein_upgrade, "minigun") style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"

                if not persistent.stein_minigun_unlocked:
                    text _("NOT OWNED") xalign 0.5 size 20 color "#ff0000" font "mod_assets/fonts/BebasNeue-Regular.ttf"
                    textbutton _("Unlock (50000)") action Function(buy_stein_upgrade, "unlock_minigun") style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"

    textbutton _("Back") action ShowMenu("sayoristein_arena_hub") style "sayoristein_menu_button" text_style "sayoristein_menu_button_text":
        xalign 0.5
        yalign 0.95

screen stein_locked_message(msg):
    modal True
    
    frame:
        xalign 0.5
        yalign 0.5
        padding (40, 40)
        background Frame("pics/gui/button_bg.png")
        
        vbox:
            spacing 20
            xalign 0.5
            
            text "[msg]" xalign 0.5 size 30 color "#ffffff" font "mod_assets/fonts/BebasNeue-Regular.ttf"
            
            textbutton _("OK") action Hide("stein_locked_message") xalign 0.5 style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"
