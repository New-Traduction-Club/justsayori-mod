init -1 python:
    import os
    import store
    from store import fae_utilities

    """
    GiftManager (maybe an API???)

    This system allows to dynamically register gifts
    The system handles:
    - Scanning for .gift files in the 'gifts' folder (either in the game's root or /game)
    - Calling the corresponding reaction label
    - Deleting the gift file after its received (configurable)
    - Persistently saving how many times a gift has been received
    - Setting a persistent "unlock" variable (optional)
    """

    class GiftManager(object):
        """
        This class handles all the logic for receiving and processing gifts
        """
        def __init__(self):
            """
            Initializes the gift manager
            """
            # Dictionary to keep a record of all available gifts
            self.registered_gifts = {}

            # Initialize persistent data for gift tracking if it doesnt exist
            if not hasattr(persistent, 'js_gift_log') or persistent.js_gift_log is None:
                persistent.js_gift_log = {}

            # Robustly find the gifts directory
            self.gifts_directory = self._find_gifts_directory()

        def _find_gifts_directory(self):
            """
            Searches for the 'gifts' folder in common locations
            """
            # Check the 'game/gifts/' directory
            game_gifts_path = os.path.join(config.gamedir, 'gifts')
            if os.path.isdir(game_gifts_path):
                return game_gifts_path

            # Check the root directory (where JustSayori.exe is located) 'gifts/'
            base_gifts_path = os.path.join(config.basedir, 'gifts')
            if os.path.isdir(base_gifts_path):
                return base_gifts_path

            # If neither is found, return None
            return None

        def register_gift(self, filename, reaction_label, delete_after=True, unlock_var=None):
            """
            Allows to register their gifts with the system

            :param filename: (str) The name of the gift file (e.g., "my_gift.gift")
            :param reaction_label: (str) The label to call when the gift is found
            :param delete_after: (bool) If True, the gift file will be deleted after being received
            :param unlock_var: (str, optional) A persistent variable to be set to True after receiving the gift
            """
            if not isinstance(filename, basestring) or not isinstance(reaction_label, basestring):
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
            Scans the 'gifts' folder for registered gift files and processes them
            """
            # Add a safety check to ensure js_gift_log is a dictionary
            if persistent.js_gift_log is None:
                persistent.js_gift_log = {}
                
            if not self.gifts_directory:
                # This will be triggered if the 'gifts' folder was not found at all
                renpy.call("js_no_gifts_folder_error")
                return

            try:
                # Get all files in the gifts directory
                gift_files = os.listdir(self.gifts_directory)

                if not gift_files:
                    renpy.call("js_no_gift_found")
                    return

                for filename in gift_files:
                    # Check if the file is a registered gift
                    if filename in self.registered_gifts:
                        gift_data = self.registered_gifts[filename]
                        filepath = os.path.join(self.gifts_directory, filename)

                        fae_utilities.log("Found gift '{}'.".format(filename), fae_utilities.SEVERITY_INFO)

                        # Update the persistent gift log
                        if filename not in persistent.js_gift_log:
                            persistent.js_gift_log[filename] = 0
                        persistent.js_gift_log[filename] += 1
                        
                        # Set an unlock variable if one is defined
                        if gift_data['unlock_var']:
                            setattr(persistent, gift_data['unlock_var'], True)
                            fae_utilities.log("Unlocked persistent variable '{}'.".format(gift_data['unlock_var']), fae_utilities.SEVERITY_INFO)

                        # Delete the file if configured to do so
                        if gift_data.get('delete_after', True):
                            try:
                                os.remove(filepath)
                                fae_utilities.log("Gift file '{}' deleted.".format(filename), fae_utilities.SEVERITY_INFO)
                            except Exception as e:
                                fae_utilities.log("Could not delete gift file '{}': {}".format(filename, e), fae_utilities.SEVERITY_ERR)

                        # Call the reaction label
                        renpy.call(gift_data['reaction_label'])

                        return

            except OSError as e:
                fae_utilities.log("Could not access the gifts folder: {}".format(e), fae_utilities.SEVERITY_ERR)
                renpy.call("js_no_gifts_folder_error")
                return

            # If no registered gift was found
            renpy.call("js_no_gift_found")
            return

        def get_gift_count(self, filename):
            """
            Returns how many times a specific gift has been received

            :param filename: (str) The name of the gift file
            :return: (int) The number of times the gift has been received
            """
            # Add a safety check here as well for good measure
            if persistent.js_gift_log is None:
                persistent.js_gift_log = {}
            return persistent.js_gift_log.get(filename, 0)

    # Create a global instance of the manager to make it accessible from anywhere in the mod
    store.js_gift_manager = GiftManager()
