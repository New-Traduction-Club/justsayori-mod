init python:
    import store.fae_outfits as fae_outfits


    class Sayori(object):
        
        _m1_sayori__pic = False
        
        _m1_sayori__iig = False
        
        _outfit = None
        
        @staticmethod
        def findOutfitName():
            
            return Sayori._outfit.reference_name
        
        
        @staticmethod
        def setOutfit(outfit):
            
            Sayori._outfit = outfit
            store.persistent.fae_outfit_quit = Sayori._outfit.reference_name
        
        @staticmethod
        def isWearingOutfit(reference_name):
            
            return Sayori._outfit.reference_name == reference_name
        
        
        @staticmethod
        def isWearingClothes(reference_name):
            
            return Sayori._outfit.clothes.reference_name == reference_name
        
        
        @staticmethod
        def isWearingHairstyle(reference_name):
            
            return Sayori._outfit.hairstyle.reference_name == reference_name
        
        
        @staticmethod
        def isWearingAccessory(reference_name):
            
            return Sayori._outfit.accessory.reference_name == reference_name
        
        
        @staticmethod
        def isWearingEyewear(reference_name):
            
            return Sayori._outfit.eyewear.reference_name == reference_name
        
        
        @staticmethod
        def isWearingHeadgear(reference_name):
            
            return Sayori._outfit.headgear.reference_name == reference_name
        
        @staticmethod
        def setInChat(p_i_c):
            """
            Sets Sayori state as in action with player.
            Disables hotkeys
            FEED:
                p_i_c = boolean value set to True
            """
            
            if not isinstance(p_i_c, bool):
                raise TypeError("p_i_c must be boolean")
            
            Sayori._m1_sayori__pic = p_i_c
        
        @staticmethod
        def setInGame(i_i_g):
            """
            Same as setInChat, but with games instead

            FEED:
                i_i_g = boolean value set to True
            """
            
            if not isinstance(i_i_g, bool):
                raise TypeError("i_i_g must be boolean")
            
            Sayori._m1_sayori__iig = i_i_g
        
        @staticmethod
        def isInChat():
            """
            Checks whether Sayori is in a topic, or interaction
            Hotkeys disabled

            RESULT:
                If in action, True, else False
            """
            return Sayori._m1_sayori__pic
        
        @staticmethod
        def isInGame():
            """
            Same as isInChat, but for games

            RESULT:
                If in game: True, False if now
            """
            return Sayori._m1_sayori__iig
        
        @staticmethod
        def add_new_regret_awaiting(regret_type):
            
            if not isinstance(regret_type, int) and not isinstance(regret_type, fae_regrets.RegretTypes):
                raise TypeError("regret_type must be of types int of fae_regrets.RegretTypes")
            
            if not int(regret_type) in store.persistent._fae_player_awaiting_apologies:
                store.persistent._fae_player_awaiting_apologies.append(int(regret_type))
        
        @staticmethod
        def add_regret_quit(regret_type):
            
            if not isinstance(regret_type, int) and not isinstance(regret_type, fae_regrets.RegretTypes):
                raise TypeError("regret_type must be of types int or fae_regrets.RegretTypes")
            
            store.persistent._fae_player_apology_type_on_quit = int(regret_type)
        
        @staticmethod
        def deleteRegret(regret_type):
            
            if not isinstance(regret_type, int) and not isinstance(regret_type, fae_regrets.RegretTypes):
                raise TypeError("regret_type must be of types int or fae_regrets.RegretTypes")
            
            if int(regret_type) in store.persistent._fae_player_awaiting_apologies:
                store.persistent._fae_player_awaiting_apologies.remove(int(regret_type))

        @staticmethod
        def save_outfit_to_persistent():
            """Saves the current outfit's components to persistent data"""
            if Sayori._outfit:
                persistent.sayo_hairstyle = Sayori._outfit.hairstyle.reference_name if Sayori._outfit.hairstyle else None
                persistent.sayo_clothes = Sayori._outfit.clothes.reference_name if Sayori._outfit.clothes else None
                persistent.sayo_accessory = Sayori._outfit.accessory.reference_name if Sayori._outfit.accessory else None
                persistent.sayo_eyewear = Sayori._outfit.eyewear.reference_name if Sayori._outfit.eyewear else None
                persistent.sayo_headgear = Sayori._outfit.headgear.reference_name if Sayori._outfit.headgear else None
                persistent.sayo_necklace = Sayori._outfit.necklace.reference_name if Sayori._outfit.necklace else None
                renpy.save_persistent()

        @staticmethod
        def load_persistent_outfit():
            """
            Loads the player's custom outfit from persistent variables
            If no custom outfit is set, defaults to the uniform
            """
            if persistent.sayo_clothes and persistent.sayo_hairstyle:
                # Get the wearable objects from their reference names
                clothes = fae_outfits.get_wearable(persistent.sayo_clothes)
                hairstyle = fae_outfits.get_wearable(persistent.sayo_hairstyle)
                accessory = fae_outfits.get_wearable(persistent.sayo_accessory) if persistent.sayo_accessory else None
                eyewear = fae_outfits.get_wearable(persistent.sayo_eyewear) if persistent.sayo_eyewear else None
                headgear = fae_outfits.get_wearable(persistent.sayo_headgear) if persistent.sayo_headgear else None
                necklace = fae_outfits.get_wearable(persistent.sayo_necklace) if persistent.sayo_necklace else None
                
                # If the essential parts don't exist, change to a default instead
                if not clothes or not hairstyle:
                    Sayori.setOutfit(fae_outfits.get_outfit("fae_uniform"))
                else:
                    # Create a new FAEOutfit object with the persistent wearables
                    custom_outfit = fae_outfits.FAEOutfit(
                        reference_name="persistent_custom",
                        display_name="Custom Outfit",
                        unlocked=True,
                        is_fae_outfit=False,
                        clothes=clothes,
                        hairstyle=hairstyle,
                        accessory=accessory,
                        eyewear=eyewear,
                        headgear=headgear,
                        necklace=necklace
                    )
                    Sayori.setOutfit(custom_outfit)
            else:
                Sayori.setOutfit(fae_outfits.get_outfit("fae_uniform"))

# Maybe...?
init python:
    config.after_load_callbacks.append(Sayori.load_persistent_outfit)
