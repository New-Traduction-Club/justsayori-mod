init -2:
    default persistent.fae_sayori_auto_outfit_change_enabled = True
    default persistent.fae_custom_outfits = False
    default persistent.fae_outfit_quit = "fae_uniform"
    default persistent.fae_outfit_list = {}
    default persistent.fae_wearable_list = {}

    # Persistent variables for the current custom outfit
    default persistent.sayo_hairstyle = None
    default persistent.sayo_clothes = None
    default persistent.sayo_accessory = None
    default persistent.sayo_eyewear = None
    default persistent.sayo_headgear = None
    default persistent.sayo_necklace = None

init -1 python in fae_outfits:
    from enum import Enum
    import json
    import os
    import random
    import re
    import store
    import store.fae_affection as fae_affection
    import store.fae_utilities as fae_utilities
    import store.fae_sprites as fae_sprites
    import time


    _PREVIEW_OUTFIT = None
    _LAST_OUTFIT = None
    _changes_made = False

    WEARABLE_CATEGORIES = [
        "hairstyle",
        "eyewear",
        "accessory",
        "clothes",
        "headgear",
        "necklace"
    ]

    # Translatable names for the categories
    WEARABLE_CATEGORY_NAMES = {
        "hairstyle": __("Hairstyle"),
        "eyewear": __("Eyewear"),
        "accessory": __("Accessory"),
        "clothes": __("Clothes"),
        "headgear": __("Headgear"),
        "necklace": __("Necklace")
    }

    # FAEWearable and FAEOutfit classes remain mostly the same, but will be used by the manager
    class FAEWearable():
        """
        Base class representing a wearable item for Sayori.
        """
        def __init__(
            self,
            reference_name,
            display_name,
            unlocked,
            is_fae_wearable,
            author="Unknown"
        ):
            """
            Initializes a new FAEWearable item.

            IN:
                reference_name - str: Unique reference name for the item.
                display_name - str: User-facing display name.
                unlocked - bool: Whether the item starts unlocked.
                is_fae_wearable - bool: True if this is a default built-in item.
                author - str, optional: The author of the item asset.
            """
            self.reference_name = reference_name
            self.display_name = display_name
            self.unlocked = unlocked
            self.is_fae_wearable = is_fae_wearable
            self.author = author

        def as_dict(self):
            """
            Returns a dictionary representation of the wearable status.

            OUT:
                dict: Dictionary containing the unlock status.
            """
            return {"unlocked": self.unlocked}

        def unlock(self):
            """
            Unlocks the wearable item and saves state.
            """
            self.unlocked = True
            store.fae_outfit_manager.save_wearable_data(self)

        def lock(self):
            """
            Locks the wearable item and saves state.
            """
            self.unlocked = False
            store.fae_outfit_manager.save_wearable_data(self)


    class FAEHairstyle(FAEWearable):
        """
        Represents a hairstyle wearable.
        """
        def getFolderName(self):
            """
            OUT:
                str: Folder name for hairstyle assets.
            """
            return "hair"

    class FAEEyewear(FAEWearable):
        """
        Represents eyewear.
        """
        def getFolderName(self):
            """
            OUT:
                str: Folder name for eyewear assets.
            """
            return "eyewear"

    class FAEAccessory(FAEWearable):
        """
        Represents an accessory.
        """
        def getFolderName(self):
            """
            OUT:
                str: Folder name for accessory assets.
            """
            return "accessory"

    class FAEClothes(FAEWearable):
        """
        Represents clothes.
        """
        def getFolderName(self):
            """
            OUT:
                str: Folder name for clothing assets.
            """
            return "clothes"

    class FAEHeadgear(FAEWearable):
        """
        Represents headgear.
        """
        def getFolderName(self):
            """
            OUT:
                str: Folder name for headgear assets.
            """
            return "headgear"

    class FAENecklace(FAEWearable):
        """
        Represents a necklace.
        """
        def getFolderName(self):
            """
            OUT:
                str: Folder name for necklace assets.
            """
            return "necklace"

    class FAEOutfit():
        """
        Represents a full outfit configuration composed of individual wearables.
        """
        def __init__(
            self,
            reference_name,
            display_name,
            unlocked,
            is_fae_outfit,
            clothes,
            hairstyle,
            accessory=None,
            eyewear=None,
            headgear=None,
            necklace=None,
        ):
            """
            Initializes a new FAEOutfit configuration.

            IN:
                reference_name - str: Unique reference name for the outfit.
                display_name - str: User-facing display name.
                unlocked - bool: Whether the outfit starts unlocked.
                is_fae_outfit - bool: True if this is a default built-in outfit.
                clothes - FAEClothes: The clothes component of the outfit.
                hairstyle - FAEHairstyle: The hairstyle component of the outfit.
                accessory - FAEAccessory, optional: The accessory component.
                eyewear - FAEEyewear, optional: The eyewear component.
                headgear - FAEHeadgear, optional: The headgear component.
                necklace - FAENecklace, optional: The necklace component.
            """
            if clothes is None:
                raise TypeError("Outfit clothing cannot be None")
            if hairstyle is None:
                raise TypeError("Outfit hairstyle cannot be None")

            self.reference_name = reference_name
            self.display_name = display_name
            self.unlocked = unlocked
            self.is_fae_outfit = is_fae_outfit
            self.clothes = clothes
            self.hairstyle = hairstyle
            self.accessory = accessory
            self.eyewear = eyewear
            self.headgear = headgear
            self.necklace = necklace

        def as_dict(self):
            """
            Returns a dictionary representation of the outfit status.

            OUT:
                dict: Dictionary containing the unlock status.
            """
            return {"unlocked": self.unlocked}

        def unlock(self):
            """
            Unlocks the outfit and all its component wearables.
            """
            self.unlocked = True
            store.fae_outfit_manager.save_outfit_data(self)
            if not self.clothes.unlocked: self.clothes.unlock()
            if not self.hairstyle.unlocked: self.hairstyle.unlock()
            if self.accessory and not self.accessory.unlocked: self.accessory.unlock()
            if self.eyewear and not self.eyewear.unlocked: self.eyewear.unlock()
            if self.headgear and not self.headgear.unlocked: self.headgear.unlock()
            if self.necklace and not self.necklace.unlocked: self.necklace.unlock()

        def lock(self):
            """
            Locks the outfit.
            """
            self.unlocked = False
            store.fae_outfit_manager.save_outfit_data(self)


    class OutfitManager(object):
        """
        Manages registration, storage, loading, and saving of outfits and wearables.
        """
        def __init__(self):
            """
            Initializes the OutfitManager.
            """
            self.JSON_DIRECTORY = os.path.join(renpy.config.gamedir, "mod_assets/sayori/sitting/jsons/").replace("\\", "/")
            self.WEARABLE_BASE_PATH = os.path.join(renpy.config.gamedir, "mod_assets", "sayori", "sitting")
            self.RESTRICTED_CHARACTERS_REGEX = "((\.)|(\[)|(\])|(\})|(\{)|(,)|(\!))"

            self.all_wearables = {}
            self.all_outfits = {}
            self.session_new_unlocks = []

        def register_wearable(self, wearable):
            """
            Registers a wearable item.

            IN:
                wearable - FAEWearable: The wearable item to register.
            """
            if wearable.reference_name in self.all_wearables:
                fae_utilities.log("Cannot register wearable name: {0}, as a wearable with that name already exists.".format(wearable.reference_name), fae_utilities.SEVERITY_WARN)
                return

            self.all_wearables[wearable.reference_name] = wearable
            if wearable.reference_name not in store.persistent.fae_wearable_list:
                self.save_wearable_data(wearable)
                if not wearable.is_fae_wearable:
                    self.session_new_unlocks.append(wearable)
            else:
                self.load_wearable_data(wearable)

        def register_outfit(self, outfit, player_created=False):
            """
            Registers a full outfit configuration.

            IN:
                outfit - FAEOutfit: The outfit configuration to register.
                player_created - bool: True if the outfit was created by the player.
            """
            if outfit.reference_name in self.all_outfits:
                fae_utilities.log("Cannot register outfit name: {0}, as an outfit with that name already exists.".format(outfit.reference_name), fae_utilities.SEVERITY_WARN)
                return

            if not outfit.accessory: outfit.accessory = self.get_wearable("fae_none")
            if not outfit.eyewear: outfit.eyewear = self.get_wearable("fae_none")
            if not outfit.headgear: outfit.headgear = self.get_wearable("fae_none")
            if not outfit.necklace: outfit.necklace = self.get_wearable("fae_none")

            self.all_outfits[outfit.reference_name] = outfit
            if outfit.reference_name not in store.persistent.fae_outfit_list:
                self.save_outfit_data(outfit)
                if not outfit.is_fae_outfit and not player_created:
                    self.session_new_unlocks.append(outfit)

        def load_wearable_data(self, wearable):
            """
            Loads unlock status for a wearable item from persistent storage.

            IN:
                wearable - FAEWearable: The wearable item.
            """
            if wearable.reference_name in store.persistent.fae_wearable_list:
                wearable.unlocked = store.persistent.fae_wearable_list[wearable.reference_name].get("unlocked", wearable.unlocked)

        def save_wearable_data(self, wearable):
            """
            Saves unlock status for a wearable item to persistent storage.

            IN:
                wearable - FAEWearable: The wearable item.
            """
            store.persistent.fae_wearable_list[wearable.reference_name] = wearable.as_dict()

        def load_outfit_data(self, outfit):
            """
            Loads unlock status for an outfit configuration from persistent storage.

            IN:
                outfit - FAEOutfit: The outfit configuration.
            """
            if outfit.reference_name in store.persistent.fae_outfit_list:
                outfit.unlocked = store.persistent.fae_outfit_list[outfit.reference_name].get("unlocked", outfit.unlocked)

        def save_outfit_data(self, outfit):
            """
            Saves unlock status for an outfit configuration to persistent storage.

            IN:
                outfit - FAEOutfit: The outfit configuration.
            """
            store.persistent.fae_outfit_list[outfit.reference_name] = outfit.as_dict()

        def get_wearable(self, wearable_name):
            """
            Retrieves a registered wearable item by name.

            IN:
                wearable_name - str: Reference name of the wearable.

            OUT:
                FAEWearable/None: The wearable item if found, otherwise None.
            """
            return self.all_wearables.get(wearable_name)

        def get_outfit(self, outfit_name):
            """
            Retrieves a registered outfit configuration by name.

            IN:
                outfit_name - str: Reference name of the outfit.

            OUT:
                FAEOutfit/None: The outfit configuration if found, otherwise None.
            """
            return self.all_outfits.get(outfit_name)

        def get_all_wearables(self):
            """
            Retrieves all registered wearable items.

            OUT:
                iterable of FAEWearable: Collection of registered wearables.
            """
            return self.all_wearables.values()

        def get_all_outfits(self):
            """
            Retrieves all registered outfit configurations.

            OUT:
                iterable of FAEOutfit: Collection of registered outfits.
            """
            return self.all_outfits.values()

        def load_all_data(self):
            """
            Loads all registered outfit and wearable persistent states.
            """
            for outfit in self.all_outfits.values():
                self.load_outfit_data(outfit)
            for wearable in self.all_wearables.values():
                self.load_wearable_data(wearable)

        def save_all_data(self):
            """
            Ensures all currently registered outfits and wearables save their state to persistent data.
            """
            for outfit in self.all_outfits.values():
                self.save_outfit_data(outfit)
            for wearable in self.all_wearables.values():
                self.save_wearable_data(wearable)

        def load_definitions_from_json(self):
            """
            Loads custom wearable and outfit definitions from JSON configuration files.
            """
            if fae_utilities.makedirifnot(self.JSON_DIRECTORY):
                fae_utilities.log("Unable to load custom outfits/wearables as the directory does not exist, and had to be created.", fae_utilities.SEVERITY_INFO)
                return

            json_files = fae_utilities.getDirFile(self.JSON_DIRECTORY, ["json"])
            wearable_jsons = []
            outfit_jsons = []

            for file_name, file_path in json_files:
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        if "category" in data:
                            wearable_jsons.append(data)
                        else:
                            outfit_jsons.append(data)
                except Exception as e:
                    fae_utilities.log("Failed to read or parse JSON file {}: {}".format(file_name, e), fae_utilities.SEVERITY_ERR)

            for data in wearable_jsons:
                self._load_wearable_from_json(data)

            for data in outfit_jsons:
                self._load_outfit_from_json(data)

        def _load_wearable_from_json(self, data):
            """
            Parses and registers a wearable definition from JSON data.

            IN:
                data - dict: The parsed JSON definition.
            """
            required_keys = ["reference_name", "display_name", "unlocked", "category"]
            if not all(key in data for key in required_keys):
                fae_utilities.log("Cannot load wearable from JSON, missing keys. Data: {}".format(data), fae_utilities.SEVERITY_WARN)
                return

            ref_name = data["reference_name"]
            if not isinstance(ref_name, str) or re.search(self.RESTRICTED_CHARACTERS_REGEX, ref_name):
                fae_utilities.log("Invalid reference_name for wearable: {}".format(ref_name), fae_utilities.SEVERITY_WARN)
                return

            if re.search("^fae_", ref_name.lower()):
                fae_utilities.log("Cannot load wearable {} as it uses a reserved namespace.".format(ref_name), fae_utilities.SEVERITY_WARN)
                return

            category = data["category"]
            wearable_class_map = {
                "hairstyle": FAEHairstyle, "eyewear": FAEEyewear, "accessory": FAEAccessory,
                "clothes": FAEClothes, "headgear": FAEHeadgear, "necklace": FAENecklace
            }
            if category not in wearable_class_map:
                fae_utilities.log("Invalid category '{}' for wearable {}.".format(category, ref_name), fae_utilities.SEVERITY_WARN)
                return

            wearable = wearable_class_map[category](
                reference_name=ref_name,
                display_name=data["display_name"],
                unlocked=data["unlocked"],
                is_fae_wearable=False,
                author=data.get("author", "Unknown")
            )
            self.register_wearable(wearable)

        def _load_outfit_from_json(self, data):
            """
            Parses and registers an outfit definition from JSON data.

            IN:
                data - dict: The parsed JSON definition.
            """
            required_keys = ["reference_name", "display_name", "unlocked", "clothes", "hairstyle"]
            if not all(key in data for key in required_keys):
                fae_utilities.log("Cannot load outfit from JSON, missing keys. Data: {}".format(data), fae_utilities.SEVERITY_WARN)
                return

            ref_name = data["reference_name"]
            if not isinstance(ref_name, str) or re.search(self.RESTRICTED_CHARACTERS_REGEX, ref_name):
                fae_utilities.log("Invalid reference_name for outfit: {}".format(ref_name), fae_utilities.SEVERITY_WARN)
                return

            for key in ["clothes", "hairstyle", "accessory", "eyewear", "headgear", "necklace"]:
                if key in data and not self.get_wearable(data[key]):
                    fae_utilities.log("Outfit '{}' references non-existent wearable '{}' for slot '{}'.".format(ref_name, data[key], key), fae_utilities.SEVERITY_WARN)
                    return

            outfit = FAEOutfit(
                reference_name=ref_name,
                display_name=data["display_name"],
                unlocked=data["unlocked"],
                is_fae_outfit=False,
                clothes=self.get_wearable(data["clothes"]),
                hairstyle=self.get_wearable(data["hairstyle"]),
                accessory=self.get_wearable(data.get("accessory")),
                eyewear=self.get_wearable(data.get("eyewear")),
                headgear=self.get_wearable(data.get("headgear")),
                necklace=self.get_wearable(data.get("necklace"))
            )
            self.register_outfit(outfit)


    # Create the global manager instance
    store.fae_outfit_manager = OutfitManager()

    def _m1_new_outfits__register_wearable(wearable):
        """
        Legacy registration wrapper for submods to register a wearable.

        IN:
            wearable - FAEWearable: The wearable to register.
        """
        store.fae_outfit_manager.register_wearable(wearable)

    def _m1_new_outfits__register_outfit(outfit, player_created=False):
        """
        Legacy registration wrapper for submods to register an outfit.

        IN:
            outfit - FAEOutfit: The outfit to register.
            player_created - bool: True if player created.
        """
        store.fae_outfit_manager.register_outfit(outfit, player_created)

    def get_wearable(wearable_name):
        """
        Public wrapper to retrieve a wearable by name.

        IN:
            wearable_name - str: Reference name of the wearable.

        OUT:
            FAEWearable/None: The wearable item.
        """
        return store.fae_outfit_manager.get_wearable(wearable_name)

    def get_outfit(outfit_name):
        """
        Public wrapper to retrieve an outfit by name.

        IN:
            outfit_name - str: Reference name of the outfit.

        OUT:
            FAEOutfit/None: The outfit configuration.
        """
        return store.fae_outfit_manager.get_outfit(outfit_name)

    def get_all_wearables():
        """
        Public wrapper to retrieve all wearables.

        OUT:
            iterable of FAEWearable: Collection of registered wearables.
        """
        return store.fae_outfit_manager.get_all_wearables()

    def get_all_outfits():
        """
        Public wrapper to retrieve all outfits.

        OUT:
            iterable of FAEOutfit: Collection of registered outfits.
        """
        return store.fae_outfit_manager.get_all_outfits()

    # --- INITIAL BUILT-IN OUTFITS ---
    # Register a "none" wearable for empty slots
    _m1_new_outfits__register_wearable(FAEWearable(
        "fae_none", "Nothing", False, True, "Forever & Ever Team"
    ))

    # Register default built-in wearables and outfits
    _m1_new_outfits__register_wearable(FAEHairstyle("fae_bow", "Bow", True, True, "Forever & Ever Team"))
    _m1_new_outfits__register_wearable(FAEHairstyle("fae_bowless", "Bowless", True, True, "Forever & Ever Team"))
    _m1_new_outfits__register_wearable(FAEClothes("fae_uniform", "School Uniform", True, True, "Forever & Ever Team"))
    _m1_new_outfits__register_wearable(FAEClothes("base", "Base", True, True, "Forever & Ever Team"))
    _m1_new_outfits__register_wearable(FAEClothes("fae_hoodie", "Black Hoodie", True, True, "Forever & Ever Team"))
    _m1_new_outfits__register_wearable(FAENecklace("fae_scarf", "Scarf", False, True, "Forever & Ever Team"))

    _m1_new_outfits__register_outfit(FAEOutfit(
        "fae_uniform", "School Uniform", True, True,
        get_wearable("fae_uniform"), get_wearable("fae_bow")
    ))
    _m1_new_outfits__register_outfit(FAEOutfit(
        "fae_hoodie", "Black Hoodie", True, True,
        get_wearable("fae_hoodie"), get_wearable("fae_bow")
    ))
    _m1_new_outfits__register_outfit(FAEOutfit(
        "fae_christmas", "Christmas Outfit", False, True,
        get_wearable("fae_hoodie"), get_wearable("fae_bow"), necklace=get_wearable("fae_scarf")
    ))

    # Load all saved data from persistent store
    store.fae_outfit_manager.load_all_data()

    # Load all custom definitions from JSON files
    store.fae_outfit_manager.load_definitions_from_json()