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

    add "pics/gui/main_menu_bg.png"

    viewport id "stein_settings_vp":
        xalign 0.5
        yalign 0.5
        xsize 1200
        ysize 600
        scrollbars "vertical"
        mousewheel True
        draggable True
        pagekeys True

        hbox:
            xalign 0.5
            spacing 50

            vbox:
                spacing 15
                xalign 0.5

                label _("Graphics Quality") style "sayoristein_menu_button_text" text_style "sayoristein_menu_button_text":
                    xalign 0.5
                    yalign 0.5

                textbutton _("High") action SetVariable("persistent.stein_quality_mode", 0) style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"
                textbutton _("Low") action SetVariable("persistent.stein_quality_mode", 1) style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"
                textbutton _("Ultra Low") action SetVariable("persistent.stein_quality_mode", 2) style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"
                textbutton _("MS Paint is Better") action SetVariable("persistent.stein_quality_mode", 3) style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"
                textbutton _("Bro, can you see?") action SetVariable("persistent.stein_quality_mode", 4) style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"

    textbutton _("Back") action ShowMenu("sayoristein_menu") style "sayoristein_menu_button" text_style "sayoristein_menu_button_text":
        xalign 0.5
        yalign 0.95


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
            textbutton _("Arena Mode") action Jump("start_level_4_arena") style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"
        else:
            textbutton _("Arena Mode (Locked)") action Show("stein_locked_message", msg=__("Complete Level 3 to unlock Arena!")) style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"

        textbutton _("Back") action ShowMenu("sayoristein_menu") style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"

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
