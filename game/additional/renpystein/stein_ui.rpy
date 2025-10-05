# RenPyStein - In-Game UI Overlay

# This screen displays on top of the main game screen (stein).
screen stein_controls_overlay():
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
