init -999 python:
    import renpy.store as store
    import renpy.exports as renpy
    import os
    import pickle
    import zlib

    def _migrate_persistent_data_v8():
        """
        Migrates Ren'Py 7 (Python 2) persistent data to Ren'Py 8 (Python 3) format.

        NOTE:
            Uses zlib decompression and python 2 pickle reading with 'latin1' encoding.
            Excludes certain built-in and platform-specific Ren'Py attributes.
        """
        EXCLUDED_ATTRIBUTES = {
            '_version',
            '_renpy_version',
            '_save_game_slots',
            '_location',
            '_game_menu_screen',
            '_main_menu_screen',
            'windows',
            'macintosh',
            'linux',
            'android',
            'ios'
        }

        old_persistent_path = os.path.join(renpy.config.savedir, "persistent")
        migrated_marker_path = os.path.join(renpy.config.savedir, "persistent.migrated")

        if not os.path.exists(old_persistent_path) or os.path.exists(migrated_marker_path):
            if not os.path.exists(old_persistent_path) and not renpy.config.developer:
                print("No 'persistent' file found to migrate. Skipping.")
            return

        print("Old 'persistent' file detected. Attempting migration to Ren'Py 8 format.")

        old_persistent = None
        try:
            with open(old_persistent_path, 'rb') as f:
                data = f.read()
                data = zlib.decompress(data)
                old_persistent = pickle.loads(data, encoding='latin1')

        except (pickle.UnpicklingError, zlib.error, EOFError, ImportError, AttributeError) as e:
            print("Error loading old 'persistent' file. It may be corrupt or incompatible. Error: %s", e)
            try:
                os.rename(old_persistent_path, old_persistent_path + ".corrupt")
                print("Old 'persistent' file has been renamed to 'persistent.corrupt'.")
            except OSError as rename_error:
                print("Could not rename corrupt 'persistent' file: %s", rename_error)
            return

        if old_persistent is None:
            print("Loading old 'persistent' produced no data. Aborting migration.")
            return

        migrated_count = 0
        for attr in dir(old_persistent):
            if not attr.startswith('__') and not callable(getattr(old_persistent, attr)) and attr not in EXCLUDED_ATTRIBUTES:
                try:
                    value = getattr(old_persistent, attr)
                    setattr(store.persistent, attr, value)
                    migrated_count += 1
                except Exception as e:
                    print("Could not migrate attribute '%s': %s", attr, e)

        print("Migration completed. %d attributes transferred.", migrated_count)

        try:
            renpy.save_persistent()
            print("New 'persistent' has been saved.")

            os.rename(old_persistent_path, migrated_marker_path)
            print("Old 'persistent' file has been renamed to 'persistent.migrated'.")

        except Exception as e:
            print("An error occurred while saving the new persistent or renaming the old one: %s", e)


    _migrate_persistent_data_v8()
