init python:
    def js_dev_restore_time():
        import datetime
        import store
        
        def real_fae_is_day():
            import datetime
            import store
            try:
                return datetime.time(store.persistent.fae_sunup) <= datetime.datetime.now().time() < datetime.time(store.persistent.fae_sundown)
            except Exception:
                return True
        
        def real_fae_is_evening():
            import datetime
            import store
            try:
                return datetime.time(store.persistent.fae_sundown) <= datetime.datetime.now().time() < datetime.time(store.persistent.fae_moonup)
            except Exception:
                return False

        store.fae_is_day = real_fae_is_day
        store.fae_is_evening = real_fae_is_evening

init 5 python:
    chatReg(
        Chat(
            persistent._chat_db,
            label="js_dev_test_weather",
            unlocked=True,
            prompt=__("Test Weather"),
            random=False,
            category=[__("DEV")]
        ),
        chat_group=CHAT_GROUP_NORMAL
    )

label js_dev_test_weather:
    python:
        js_dev_restore_time()
        if "is_daytime" in store.main_background.__dict__:
            del store.main_background.is_daytime

    jump js_dev_test_weather_menu

label js_dev_test_weather_menu:
    python:
        if fae_is_day():
            time_status = "DAY"
        elif fae_is_evening():
            time_status = "EVENING"
        else:
            time_status = "NIGHT"

        weather_status = "None"
        if fae_atmosphere.current_weather:
            weather_status = str(fae_atmosphere.current_weather.weather_type)

    "Current time evaluated as [time_status]. Current weather is [weather_status]."

    menu:
        "Select Weather Preset":
            jump js_dev_test_weather_preset_menu
        "Select Time of Day":
            jump js_dev_test_weather_time_menu
        "Reload Sky":
            $ fae_atmosphere.reload_sky()
            $ store.main_background.form()
            "Sky and room background reloaded."
            jump js_dev_test_weather_menu
        "Exit":
            python:
                js_dev_restore_time()
                if "is_daytime" in store.main_background.__dict__:
                    del store.main_background.is_daytime
            $ fae_atmosphere.reload_sky()
            $ store.main_background.form()
            return

label js_dev_test_weather_preset_menu:
    python:
        preset_items = [
            ("WEATHER_SUNNY", "sunny"),
            ("WEATHER_OVERCAST", "overcast"),
            ("WEATHER_RAIN", "rain"),
            ("WEATHER_THUNDER", "thunder"),
            ("WEATHER_SNOW", "snow"),
            # ("WEATHER_GLITCH (Fuzzy noise)", "glitch"),
            ("WEATHER_SPACE (Scrolling mask)", "space"),
            ("Random Weather", "random")
        ]

    call screen neat_menu_scroll(preset_items, ("Back", "back"))

    if _return == "sunny":
        $ fae_atmosphere.showSky(fae_atmosphere.WEATHER_SUNNY)
        "Set to SUNNY."
    elif _return == "overcast":
        $ fae_atmosphere.showSky(fae_atmosphere.WEATHER_OVERCAST)
        "Set to OVERCAST."
    elif _return == "rain":
        $ fae_atmosphere.showSky(fae_atmosphere.WEATHER_RAIN)
        "Set to RAIN."
    elif _return == "thunder":
        $ fae_atmosphere.showSky(fae_atmosphere.WEATHER_THUNDER)
        "Set to THUNDER."
    elif _return == "snow":
        $ fae_atmosphere.showSky(fae_atmosphere.WEATHER_SNOW)
        "Set to SNOW."
    # elif _return == "glitch":
    #     $ fae_atmosphere.showSky(fae_atmosphere.WEATHER_GLITCH)
    #     "Set to GLITCH (Fuzzy)."
    elif _return == "space":
        $ fae_atmosphere.showSky(fae_atmosphere.WEATHER_SPACE)
        "Set to SPACE."
    elif _return == "random":
        $ fae_atmosphere.updateSky()
        "Triggered random weather."

    jump js_dev_test_weather_menu

label js_dev_test_weather_time_menu:
    menu:
        "Override to DAY":
            python:
                store.fae_is_day = lambda: True
                store.fae_is_evening = lambda: False
                store.main_background.is_daytime = lambda *args: True
            $ fae_atmosphere.reload_sky()
            $ store.main_background.form()
        "Override to EVENING":
            python:
                store.fae_is_day = lambda: False
                store.fae_is_evening = lambda: True
                store.main_background.is_daytime = lambda *args: False
            $ fae_atmosphere.reload_sky()
            $ store.main_background.form()
        "Override to NIGHT":
            python:
                store.fae_is_day = lambda: False
                store.fae_is_evening = lambda: False
                store.main_background.is_daytime = lambda *args: False
            $ fae_atmosphere.reload_sky()
            $ store.main_background.form()
        "Restore OS Time":
            python:
                js_dev_restore_time()
                if "is_daytime" in store.main_background.__dict__:
                    del store.main_background.is_daytime
            $ fae_atmosphere.reload_sky()
            $ store.main_background.form()
        "Reset Save Data Time Defaults":
            python:
                persistent.fae_sunup = 6
                persistent.fae_sundown = 18
                persistent.fae_moonup = 21
                js_dev_restore_time()
                if "is_daytime" in store.main_background.__dict__:
                    del store.main_background.is_daytime
            $ fae_atmosphere.reload_sky()
            $ store.main_background.form()
        "Back":
            jump js_dev_test_weather_menu
    jump js_dev_test_weather_menu
