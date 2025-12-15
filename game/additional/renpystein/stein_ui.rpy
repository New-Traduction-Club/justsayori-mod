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
        textbutton "Keyboard" action SetVariable("simulate_touch", False)
        
        # Button to switch to Touch/Mouse mode.
        textbutton "Touch" action SetVariable("simulate_touch", True)
        
        # This button toggles the performance mode and updates its own text.
        if persistent.performance_mode:
            # If in low quality mode, show a button to switch to High.
            textbutton "Quality: Low" action SetVariable("persistent.performance_mode", False)
        else:
            # If in high quality mode, show a button to switch to Low.
            textbutton "Quality: High" action SetVariable("persistent.performance_mode", True)

# Style for the text inside the buttons on this screen.
style stein_controls_overlay_textbutton_text:
    size 20
    idle_color "#ffffff"  # White text
    hover_color "#00ff00" # Green text on hover

style sayoristein_menu_button_text is button_text:
    xalign 0.5
    yalign 0.5

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
        textbutton _("Exit") action Return() style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"

screen sayoristein_level_select():
    tag menu

    add "pics/gui/main_menu.png"

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 15

        textbutton _("Level 1") action Jump("start_level_1") style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"
        textbutton _("Level 2") action Jump("start_level_2") style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"
        textbutton _("Level 3") action Jump("start_level_3") style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"
        textbutton _("Back") action ShowMenu("sayoristein_menu") style "sayoristein_menu_button" text_style "sayoristein_menu_button_text"
