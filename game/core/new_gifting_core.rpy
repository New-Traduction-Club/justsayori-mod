init -1 python:
    import os
    import store
    from store import fae_utilities

    class GiftManager(object):
        """
        Manages the receiving, logging, and processing of custom gifts.

        This system handles:
        - Scanning for `.gift` files in the 'gifts' folder.
        - Calling the corresponding reaction label when found.
        - Deleting the gift file after receipt (configurable).
        - Persistently tracking how many times a gift has been received.
        - Gating unlock states via persistent variables.
        """
        def __init__(self):
            """
            Initializes the gift manager.
            """
            self.registered_gifts = {}

            if not hasattr(persistent, 'js_gift_log') or persistent.js_gift_log is None:
                persistent.js_gift_log = {}

            self.gifts_directory = self._find_gifts_directory()

        def _find_gifts_directory(self):
            """
            Searches for the 'gifts' directory in standard paths.

            OUT:
                str/None: Absolute path to the gifts directory if found, otherwise None.
            """
            game_gifts_path = os.path.join(config.gamedir, 'gifts')
            if os.path.isdir(game_gifts_path):
                return game_gifts_path

            base_gifts_path = os.path.join(config.basedir, 'gifts')
            if os.path.isdir(base_gifts_path):
                return base_gifts_path

            return None

        def register_gift(self, filename, reaction_label, delete_after=True, unlock_var=None):
            """
            Registers a gift file and its associated reaction label.

            IN:
                filename - str: The name of the gift file (e.g., "my_gift.gift").
                reaction_label - str: The Ren'Py label to call when the gift is received.
                delete_after - bool: If True, deletes the gift file from disk after receipt.
                unlock_var - str, optional: Name of a persistent variable to set to True upon receipt.
            """
            if not isinstance(filename, str) or not isinstance(reaction_label, str):
                fae_utilities.log("Gift filename and reaction_label must be strings.", fae_utilities.SEVERITY_ERR)
                return

            if renpy.has_label(reaction_label):
                self.registered_gifts[filename] = {
                    'reaction_label': reaction_label,
                    'delete_after': delete_after,
                    'unlock_var': unlock_var
                }
                fae_utilities.log("Gift '{}' registered successfully.".format(filename), fae_utilities.SEVERITY_INFO)
            else:
                fae_utilities.log("Could not register gift '{}'. The label '{}' does not exist.".format(filename, reaction_label), fae_utilities.SEVERITY_ERR)

        def check_for_gifts(self):
            """
            Scans the gifts folder for registered files and triggers their reactions.
            """
            if persistent.js_gift_log is None:
                persistent.js_gift_log = {}
                
            if not self.gifts_directory:
                renpy.call("js_no_gifts_folder_error")
                return

            try:
                gift_files = os.listdir(self.gifts_directory)

                if not gift_files:
                    renpy.call("js_no_gift_found")
                    return

                for filename in gift_files:
                    if filename in self.registered_gifts:
                        gift_data = self.registered_gifts[filename]
                        filepath = os.path.join(self.gifts_directory, filename)

                        fae_utilities.log("Found gift '{}'.".format(filename), fae_utilities.SEVERITY_INFO)

                        if filename not in persistent.js_gift_log:
                            persistent.js_gift_log[filename] = 0
                        persistent.js_gift_log[filename] += 1
                        
                        if gift_data['unlock_var']:
                            setattr(persistent, gift_data['unlock_var'], True)
                            fae_utilities.log("Unlocked persistent variable '{}'.".format(gift_data['unlock_var']), fae_utilities.SEVERITY_INFO)

                        if gift_data.get('delete_after', True):
                            try:
                                os.remove(filepath)
                                fae_utilities.log("Gift file '{}' deleted.".format(filename), fae_utilities.SEVERITY_INFO)
                            except Exception as e:
                                fae_utilities.log("Could not delete gift file '{}': {}".format(filename, e), fae_utilities.SEVERITY_ERR)

                        renpy.call(gift_data['reaction_label'])

                        return

            except OSError as e:
                fae_utilities.log("Could not access the gifts folder: {}".format(e), fae_utilities.SEVERITY_ERR)
                renpy.call("js_no_gifts_folder_error")
                return

            renpy.call("js_no_gift_found")
            return

        def get_gift_count(self, filename):
            """
            Retrieves the receipt count for a specific gift.

            IN:
                filename - str: The name of the gift file.

            OUT:
                int: The number of times the gift has been received.
            """
            if persistent.js_gift_log is None:
                persistent.js_gift_log = {}
            return persistent.js_gift_log.get(filename, 0)

    store.js_gift_manager = GiftManager()
