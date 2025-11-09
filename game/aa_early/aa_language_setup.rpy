init -999 python:
    import os
    if renpy.android:

        spanish_lang_file = os.path.join(config.gamedir, "language_spanish.txt")
        english_lang_file = os.path.join(config.gamedir, "language_english.txt")

        language = None
        if os.path.exists(spanish_lang_file):
            language = "spanish"
        elif os.path.exists(english_lang_file):
            language = "english"
        else:
            language = "english"

        if language:
            persistent.language = language
        print("Debug")