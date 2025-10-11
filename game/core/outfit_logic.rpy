init -1 python in fae_outfit_logic:
    import store
    import store.fae_outfits as fae_outfits
    import store.fae_sprites as fae_sprites

    def get_categorized_wearables():
        """
        Parses all registered wearables and organizes them by category
        """
        categorized_wearables = {category: [] for category in fae_outfits.WEARABLE_CATEGORIES}
        optional_categories = ["eyewear", "accessory", "headgear", "necklace"]
        all_wearables = fae_outfits.get_all_wearables()

        # Prepare the None item data
        none_wearable_obj = fae_outfits.get_wearable("fae_none")
        if none_wearable_obj:
            none_wearable_data = {
                "display_name": none_wearable_obj.display_name,
                "reference_name": none_wearable_obj.reference_name,
                "author": none_wearable_obj.author
            }
            # Add the None option to the start of each optional category
            for category in optional_categories:
                item_data = none_wearable_data.copy()
                item_data["category"] = category
                categorized_wearables[category].insert(0, item_data)

        for wearable in all_wearables:
            if wearable.reference_name in ["fae_none", "base"]:
                continue

            wearable_data = {
                "display_name": wearable.display_name,
                "reference_name": wearable.reference_name,
                "author": wearable.author
            }

            category = None
            if isinstance(wearable, fae_outfits.FAEHairstyle): category = "hairstyle"
            elif isinstance(wearable, fae_outfits.FAEClothes): category = "clothes"
            elif isinstance(wearable, fae_outfits.FAEEyewear): category = "eyewear"
            elif isinstance(wearable, fae_outfits.FAEAccessory): category = "accessory"
            elif isinstance(wearable, fae_outfits.FAEHeadgear): category = "headgear"
            elif isinstance(wearable, fae_outfits.FAENecklace): category = "necklace"

            if category:
                wearable_data["category"] = category
                categorized_wearables[category].append(wearable_data)

        return categorized_wearables

    def generate_preview_for_wearable(wearable_data):
        """
        Generates a LiveComposite preview for a given wearable, layered on the current outfit
        """
        preview_outfit = store.fae_outfits.FAEOutfit(
            reference_name="preview",
            display_name="preview",
            unlocked=True,
            is_fae_outfit=False,
            clothes=store.Sayori._outfit.clothes,
            hairstyle=store.Sayori._outfit.hairstyle,
            accessory=store.Sayori._outfit.accessory,
            eyewear=store.Sayori._outfit.eyewear,
            headgear=store.Sayori._outfit.headgear,
            necklace=store.Sayori._outfit.necklace
        )

        # Get the full wearable object and apply it to the preview outfit
        wearable_obj = fae_outfits.get_wearable(wearable_data['reference_name'])
        if wearable_obj:
            setattr(preview_outfit, wearable_data['category'], wearable_obj)

        # Use the expression renderer to get all parts for a static pose
        exp_parts = fae_sprites._exp_renderer("abegaa")

        # Build the list of sprite parts
        sprite_parts = [
            (0, 0), "mod_assets/sayori/table/chair.png",
            (0, 0), "mod_assets/sayori/sitting/backarms/{}/{}.png".format(preview_outfit.clothes.reference_name, exp_parts["backarm"]),
            (0, 0), "mod_assets/sayori/sitting/body/{}/1.png".format(preview_outfit.clothes.reference_name),
            (0, 0), "mod_assets/sayori/table/desk_sh.png",
            (0, 0), "mod_assets/sayori/table/desk.png",
            (0, 0), "mod_assets/sayori/sitting/arms/{}/{}.png".format(preview_outfit.clothes.reference_name, exp_parts["arms"]),
            (0, 0), "mod_assets/sayori/sitting/arms/{}/{}.png".format(preview_outfit.clothes.reference_name, exp_parts["arms2"]),

            (0, 0), "mod_assets/sayori/sitting/hair/{}/a.png".format(preview_outfit.hairstyle.reference_name),
            (0, 0), "mod_assets/sayori/sitting/eyes/{}.png".format(exp_parts["eyes"]),
            (0, 0), "mod_assets/sayori/sitting/mouth/{}.png".format(exp_parts["mouth"]),
        ]

        # Add optional parts
        if preview_outfit.necklace and preview_outfit.necklace.reference_name != "fae_none":
            sprite_parts.extend([(0, 0), "mod_assets/sayori/sitting/necklace/{}/sitting.png".format(preview_outfit.necklace.reference_name)])
        if preview_outfit.accessory and preview_outfit.accessory.reference_name != "fae_none":
            sprite_parts.extend([(0, 0), "mod_assets/sayori/sitting/accessory/{}/sitting.png".format(preview_outfit.accessory.reference_name)])

        # Add eyebrows and headgear
        sprite_parts.extend([(0, 0), "mod_assets/sayori/sitting/eyebrows/{}.png".format(exp_parts["eyebrows"])])

        if preview_outfit.headgear and preview_outfit.headgear.reference_name != "fae_none":
            sprite_parts.extend([(0, 0), "mod_assets/sayori/sitting/headgear/{}/sitting.png".format(preview_outfit.headgear.reference_name)])
        if preview_outfit.eyewear and preview_outfit.eyewear.reference_name != "fae_none":
            sprite_parts.extend([(0, 0), "mod_assets/sayori/sitting/eyewear/{}/sitting.png".format(preview_outfit.eyewear.reference_name)])

        return renpy.display.layout.LiveComposite((1280, 720), *sprite_parts)

    def evaluate_outfit_reactions(changed_items):
        """
        Checks for reaction labels for a list of changed wearables and calls them
        Only reacts to the last applied item for each category
        """
        if not changed_items:
            return

        # Use a dictionary to get the last applied item for each category
        last_changes = {}
        for item in changed_items:
            last_changes[item['category']] = item

        for category, item_data in last_changes.items():
            # Construct the label name, example: "reaction_hairstyle_fae_bowless"
            reaction_label = "reaction_{0}_{1}".format(category, item_data['reference_name'])

            if renpy.has_label(reaction_label):
                renpy.call_in_new_context(reaction_label)