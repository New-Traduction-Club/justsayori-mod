init -1 python in fae_outfit_screen:
    import store.fae_outfit_logic as fae_outfit_logic
    import store.fae_outfits as fae_outfits

transform outfit_preview_thumb(w, h):
    crop (450, 50, 500, 500)
    xysize (w, h)

init -1 python:
    import store

    def js_apply_wearable_preview(wearable_ref, category):
        """
        Applies a wearable to the current outfit without saving to persistent.

        IN:
            wearable_ref - str: The reference name of the wearable to apply.
            category - str: The category of the wearable (e.g. 'clothes', 'hairstyle').
        """
        wearable_obj = store.fae_outfits.get_wearable(wearable_ref)
        if wearable_obj:
            setattr(store.Sayori._outfit, category, wearable_obj)

    def js_reset_outfit_preview(original_refs):
        """
        Resets the outfit to the provided original references.

        IN:
            original_refs - dict: A dictionary of category to reference_name.
        """
        for category, ref in original_refs.items():
            wearable_obj = store.fae_outfits.get_wearable(ref) if ref else None
            setattr(store.Sayori._outfit, category, wearable_obj)


    def exec_outfit_change_persistent(wearable_ref, category):
        """
        Finds a wearable, applies it to the current outfit, and saves it to persistent data.

        IN:
            wearable_ref - str: The reference name of the wearable to apply.
            category - str: The category of the wearable (e.g. 'clothes', 'hairstyle').
        """
        wearable_obj = fae_outfits.get_wearable(wearable_ref)
        if wearable_obj:
            setattr(store.Sayori._outfit, category, wearable_obj)

            if store.Sayori._outfit:
                persistent.sayo_hairstyle = store.Sayori._outfit.hairstyle.reference_name if store.Sayori._outfit.hairstyle else None
                persistent.sayo_clothes = store.Sayori._outfit.clothes.reference_name if store.Sayori._outfit.clothes else None
                persistent.sayo_accessory = store.Sayori._outfit.accessory.reference_name if store.Sayori._outfit.accessory else None
                persistent.sayo_eyewear = store.Sayori._outfit.eyewear.reference_name if store.Sayori._outfit.eyewear else None
                persistent.sayo_headgear = store.Sayori._outfit.headgear.reference_name if store.Sayori._outfit.headgear else None
                persistent.sayo_necklace = store.Sayori._outfit.necklace.reference_name if store.Sayori._outfit.necklace else None
                renpy.save_persistent()

## Outfit screen #######################################################
screen outfit_changer():
    tag menu

    style_prefix "outfit"

    default categorized_wearables = fae_outfit_logic.get_categorized_wearables()
    default first_category_with_items = next((cat for cat, items in sorted(categorized_wearables.items()) if items), None)
    default current_category = first_category_with_items
    default search_text = ""
    default show_categories = False

    default initial_outfit_refs = {
        'hairstyle': store.Sayori._outfit.hairstyle.reference_name if store.Sayori._outfit.hairstyle else None,
        'clothes': store.Sayori._outfit.clothes.reference_name if store.Sayori._outfit.clothes else None,
        'accessory': store.Sayori._outfit.accessory.reference_name if store.Sayori._outfit.accessory else None,
        'eyewear': store.Sayori._outfit.eyewear.reference_name if store.Sayori._outfit.eyewear else None,
        'headgear': store.Sayori._outfit.headgear.reference_name if store.Sayori._outfit.headgear else None,
        'necklace': store.Sayori._outfit.necklace.reference_name if store.Sayori._outfit.necklace else None
    }

    frame at fade_in:
        xpos 980
        yfill True
        xsize 300
        background Solid("#0032d2cc") 

        vbox:
            xalign 0.5
            yalign 0.0
            ypos 10
            spacing 10
            xsize 280

            frame:
                background Solid("#4e78ff66")
                xsize 270
                ysize 36
                xalign 0.5
                
                hbox:
                    yalign 0.5
                    xpos 10
                    text _("Search: ") style "outfit_detail_desc"
                    input value ScreenVariableInputValue("search_text") length 30 style "outfit_detail_desc"

            $ display_name = fae_outfits.WEARABLE_CATEGORY_NAMES.get(current_category, current_category.capitalize()) if current_category else "Category"
            textbutton _("Category: [display_name]") action ToggleScreenVariable("show_categories") style "outfit_nav_button" xfill True xalign 0.5

            viewport:
                xsize 280
                ysize 420
                xalign 0.5
                scrollbars "vertical"
                mousewheel True

                vbox:
                    spacing 10
                    xalign 0.5
                    xfill True
                    
                    if current_category and categorized_wearables[current_category]:
                        $ found_items = False
                        for wearable_data in categorized_wearables[current_category]:
                            if search_text.lower() in wearable_data["display_name"].lower():
                                $ found_items = True
                                $ current_ref = getattr(store.Sayori._outfit, current_category).reference_name if getattr(store.Sayori._outfit, current_category) else None
                                $ is_selected = (current_ref == wearable_data['reference_name'])
                                
                                button:
                                    style "outfit_list_button"
                                    action [
                                        Function(js_apply_wearable_preview, wearable_ref=wearable_data['reference_name'], category=current_category),
                                        renpy.restart_interaction
                                    ]
                                    selected is_selected
                                    
                                    vbox:
                                        spacing 5
                                        xalign 0.5
                                        add fae_outfit_logic.generate_preview_for_wearable(wearable_data) at outfit_preview_thumb(130, 130):
                                            xalign 0.5
                                        
                                        text wearable_data["display_name"] style "outfit_list_button_text" xalign 0.5 text_align 0.5
                        
                        if not found_items:
                            text _("Nothing here.") style "outfit_detail_desc" xalign 0.5
                    else:
                        text _("No items in this category.") style "outfit_detail_desc" xalign 0.5

            null yfill True

            vbox:
                xalign 0.5
                spacing 5
                
                textbutton _("Confirm") style "outfit_action_button" text_style "outfit_action_button_text" action [
                    Function(Sayori.save_outfit_to_persistent),
                    Return([])
                ] xfill True xalign 0.5

                textbutton _("Restore") style "outfit_action_button" text_style "outfit_action_button_text" action [
                    Function(js_reset_outfit_preview, original_refs=initial_outfit_refs),
                    renpy.restart_interaction
                ] xfill True xalign 0.5

                textbutton _("Cancel") style "outfit_action_button" text_style "outfit_action_button_text" action [
                    Function(js_reset_outfit_preview, original_refs=initial_outfit_refs),
                    Return([])
                ] xfill True xalign 0.5
                
                null height 10

    if show_categories:
        frame:
            xpos 720
            ypos 100
            xsize 250
            background Solid("#0032d2cc")
            padding (15, 15)
            
            vbox:
                xalign 0.5
                yalign 0.0
                spacing 10
                
                label _("Categories") style "outfit_detail_title" xalign 0.5
                
                for category_name in sorted(categorized_wearables.keys()):
                    $ cat_display_name = fae_outfits.WEARABLE_CATEGORY_NAMES.get(category_name, category_name.capitalize())
                    if categorized_wearables[category_name]:
                        textbutton cat_display_name action [SetScreenVariable("current_category", category_name), SetScreenVariable("show_categories", False)] style "outfit_nav_button" text_style "outfit_nav_button_text" selected (current_category == category_name) xfill True xalign 0.5

style outfit_detail_desc is song_info_author
style outfit_detail_title is song_info_title

style outfit_nav_button is button:
    properties gui.button_properties("navigation_button")
    background Solid("#ffffff11")
    hover_background Solid("#ffffff33")
    selected_background Solid("#ffffff22")
    selected_hover_background Solid("#ffffff44")
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

style outfit_list_button:
    xfill True
    ysize None
    xalign 0.5
    padding (10, 10, 10, 10)
    background Solid("#ffffff11")
    hover_background Solid("#ffffff33")
    selected_background Solid("#ffffff22")
    selected_hover_background Solid("#ffffff44")

style outfit_list_button_text is button_text:
    font "gui/font/Aller_Rg.ttf"
    xalign 0.5
    text_align 0.5
    size 20

style outfit_action_button is button:
    xfill True
    background Frame("mod_assets/buttons/idle_bg2.png", gui.choice_button_borders, tile=True)
    hover_background Frame("mod_assets/buttons/selected_bg2.png", gui.choice_button_borders, tile=True)
    padding (10, 8)

style outfit_action_button_text is button_text:
    xalign 0.5
    size 20
    color "#ffffff"
    outlines [(2, "#0032d2", 0, 0)]
