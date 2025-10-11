init -1 python in fae_outfit_screen:
    import store.fae_outfit_logic as fae_outfit_logic
    import store.fae_outfits as fae_outfits

transform outfit_preview_thumb(w, h):
    crop (160, 0, 960, 720)
    size (w, h)
    fit "contain"
    truecenter
    zoom 0.8

transform outfit_preview_thumb_small(w, h):
    crop (320, 60, 640, 640)
    size (w, h)
    fit "contain"
    truecenter
    zoom 0.8

screen outfit_changer():
    tag menu

    style_prefix "outfit"

    # Get all wearable data and set the initial category when the screen starts
    default categorized_wearables = fae_outfit_logic.get_categorized_wearables()
    default first_category_with_items = next((cat for cat, items in sorted(categorized_wearables.items()) if items), None)
    default current_category = first_category_with_items

    # This will hold the data of the item the user clicks on
    default selected_wearable = None

    # This will track all items applied during the session
    default changed_items_list = []

    add Solid("#000000cc")

    frame style "outfit_hub_frame" xalign 0.5 yalign 0.5 at music_ui_pop:
        hbox:
            spacing 30

            # Column 1: Outfit cards
            vbox:
                xsize 700
                label _("Select an item") style "outfit_hub_title"
                viewport:
                    style "outfit_cards_viewport"
                    scrollbars "vertical"
                    mousewheel True

                    grid 3 4:
                        style "outfit_cards_grid"

                        if current_category and categorized_wearables[current_category]:
                            for wearable_data in categorized_wearables[current_category]:
                                $ is_selected = (selected_wearable and selected_wearable['reference_name'] == wearable_data['reference_name'])
                                button:
                                    style "outfit_card_button_selected"
                                    action SetScreenVariable("selected_wearable", wearable_data)
                                    at mg_card_hover

                                    vbox:
                                        spacing 8
                                        # Use the dynamic preview generator
                                        add fae_outfit_logic.generate_preview_for_wearable(wearable_data) at outfit_preview_thumb(180, 180):
                                            xalign 0.5

                                        text wearable_data["display_name"] style "outfit_card_title"
                                        text "by [wearable_data['author']]" style "outfit_card_author"
                        else:
                            text _("No items in this category.") style "outfit_detail_desc" xalign 0.5

            # Column 2: Details and preview
            vbox:
                style "outfit_details_vbox"
                if selected_wearable:
                    # Display details of the selected item
                    text selected_wearable["display_name"] style "outfit_detail_title"

                    # Big preview
                    frame style "outfit_detail_preview_frame":
                        add fae_outfit_logic.generate_preview_for_wearable(selected_wearable) at outfit_preview_thumb_small(226, 226):
                            zoom 1.0

                    text "by [selected_wearable['author']]" style "outfit_detail_desc"

                    null height 15
                    # Button to apply the option
                    textbutton _("Apply") style "big_play_button" text_style "big_play_button_text" action [
                        Function(exec_outfit_change_persistent, wearable_ref=selected_wearable['reference_name'], category=current_category),
                        Function(Sayori.save_outfit_to_persistent),
                        Function(changed_items_list.append, selected_wearable),
                        renpy.restart_interaction
                    ]
                else:
                    frame style "outfit_detail_preview_frame"
                    text _("Select an item") style "outfit_detail_title"

                null yfill True

                textbutton _("Close") style "mg_close_button" text_style "mg_close_button_text" action [
                    Function(fae_outfit_logic.evaluate_outfit_reactions, changed_items=changed_items_list),
                    Return()
                ]

            # Column 3: Navigation menu
            vbox:
                style "outfit_nav_vbox"
                label _("Categories") style "outfit_hub_title"
                for category_name in sorted(categorized_wearables.keys()):
                    if categorized_wearables[category_name]:
                        textbutton category_name.capitalize() action [SetScreenVariable("current_category", category_name), SetScreenVariable("selected_wearable", None)] style "outfit_nav_button" text_style "outfit_nav_button_text" selected (current_category == category_name)

init -1 python:
    import store

    def exec_outfit_change_persistent(wearable_ref, category):
        """
        Finds the wearable object, applies it to the current outfit, and saves the entire outfit to persistent data
        """
        wearable_obj = fae_outfits.get_wearable(wearable_ref)
        if wearable_obj:
            # Apply to the current outfit for immediate visual change
            setattr(store.Sayori._outfit, category, wearable_obj)

            # Directly update all persistent variables based on the now-current outfit
            if store.Sayori._outfit:
                persistent.sayo_hairstyle = store.Sayori._outfit.hairstyle.reference_name if store.Sayori._outfit.hairstyle else None
                persistent.sayo_clothes = store.Sayori._outfit.clothes.reference_name if store.Sayori._outfit.clothes else None
                persistent.sayo_accessory = store.Sayori._outfit.accessory.reference_name if store.Sayori._outfit.accessory else None
                persistent.sayo_eyewear = store.Sayori._outfit.eyewear.reference_name if store.Sayori._outfit.eyewear else None
                persistent.sayo_headgear = store.Sayori._outfit.headgear.reference_name if store.Sayori._outfit.headgear else None
                persistent.sayo_necklace = store.Sayori._outfit.necklace.reference_name if store.Sayori._outfit.necklace else None
                renpy.save_persistent()

style outfit_hub_frame is mg_hub_frame:
    xsize 1240
    ysize 680

style outfit_hub_title is music_player_title:
    xalign 0.0
    bottom_margin 5

style outfit_cards_viewport is music_list_viewport:
    xsize 700
    ysize 520

style outfit_cards_grid is mg_cards_grid

style outfit_card_button is mg_card_button:
    ysize 260

style outfit_card_button_selected:
    background Solid("#ffffff00")
    ysize 260

style outfit_card_title is mg_card_title

style outfit_card_author is music_button_text:
    size 14
    color "#aaaaaa"
    xalign 0.5

style outfit_details_vbox is song_info_vbox:
    xsize 256

style outfit_detail_preview_frame is song_image_placeholder:
    xsize 226
    ysize 226

style outfit_detail_title is song_info_title

style outfit_detail_desc is song_info_author

style outfit_nav_vbox:
    xsize 200
    spacing 10

style outfit_nav_button is button:
    properties gui.button_properties("navigation_button")
    background Frame("gui/button/choice_idle_background.png", gui.choice_button_borders, tile=True)
    hover_background Frame("gui/button/choice_hover_background.png", gui.choice_button_borders, tile=True)
    selected_background Frame("gui/button/slot_hover_background.png", gui.choice_button_borders, tile=True)
    selected_hover_background Frame("gui/button/slot_hover_background.png", gui.choice_button_borders, tile=True)
    # xfill True
    xsize 125
    padding (10, 8)

style outfit_nav_button_text is button_text:
    properties gui.button_text_properties("navigation_button")
    font gui.interface_font
    size 20
    color gui.idle_color
    hover_color gui.hover_color
    selected_color gui.accent_color
    selected_hover_color gui.accent_color
    xalign 0.5