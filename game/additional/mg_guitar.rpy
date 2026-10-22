init 5 python in js_guitar:
    import os
    import pygame
    import time
    import store

    try:
        for i in range(1, 7):
            renpy.music.register_channel("js_guitar_%d" % i, mixer="sfx", loop=False, stop_on_mute=False, tight=False)
    except Exception:
        pass

    FRET_KEYS = {
        pygame.K_q: 1,
        pygame.K_w: 2,
        pygame.K_e: 3,
        pygame.K_r: 4,
        pygame.K_a: 5,
        pygame.K_s: 6,
        pygame.K_d: 7,
        pygame.K_f: 8,
        pygame.K_z: 9,
        pygame.K_x: 10,
        pygame.K_c: 11,
        pygame.K_v: 12,
    }

    FRET_KEY_NAMES = {
        1: "Q",
        2: "W",
        3: "E",
        4: "R",
        5: "A",
        6: "S",
        7: "D",
        8: "F",
        9: "Z",
        10: "X",
        11: "C",
        12: "V",
    }

    STRING_KEYS = {
        pygame.K_o: 1,
        pygame.K_k: 2,
        pygame.K_m: 3,
        pygame.K_i: 4,
        pygame.K_j: 5,
        pygame.K_n: 6,
    }

    NOTES = {
        1: ["E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4", "C5", "C#5", "D5", "D#5", "E5"],
        2: ["B3", "C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4"],
        3: ["G3", "G#3", "A3", "A#3", "B3", "C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4"],
        4: ["D3", "D#3", "E3", "F3", "F#3", "G3", "G#3", "A3", "A#3", "B3", "C4", "C#4", "D4"],
        5: ["A2", "A#2", "B2", "C3", "C#3", "D3", "D#3", "E3", "F3", "F#3", "G3", "G#3", "A3"],
        6: ["E2", "F2", "F#2", "G2", "G#2", "A2", "A#2", "B2", "C3", "C#3", "D3", "D#3", "E3"],
    }

    STRING_NAMES = {
        1: ("String 1 (High E)", "O"),
        2: ("String 2 (B)", "K"),
        3: ("String 3 (G)", "M"),
        4: ("String 4 (D)", "I"),
        5: ("String 5 (A)", "J"),
        6: ("String 6 (Low E)", "N"),
    }

    def js_play_note(string_idx, fret_idx):
        """
        Plays the specified string and fret audio file on its dedicated channel.

        IN:
            string_idx - int: String index (1 to 6).
            fret_idx - int: Fret index (0 to 12).

        OUT:
            bool: True if playback started successfully, False otherwise.
        """
        channel = "js_guitar_%d" % string_idx
        filename = "mod_assets/games/guitar/audio/s%df%d.ogg" % (string_idx, fret_idx)
        if renpy.loadable(filename):
            renpy.music.play(filename, channel=channel, loop=False)
            return True
        return False

    def js_cleanup():
        """
        Stops audio playback across all 6 guitar channels.

        OUT:
            None
        """
        for i in range(1, 7):
            try:
                renpy.music.stop(channel="js_guitar_%d" % i)
            except Exception:
                pass

    class JSGuitarEngine(object):
        def __init__(self):
            """
            Initializes the guitar engine state.

            OUT:
                None
            """
            self.held_frets = []
            self.pending_strums = []
            self.string_active_until = {i: 0.0 for i in range(1, 7)}
            self.string_last_fret = {i: 0 for i in range(1, 7)}
            self.last_action_desc = "test"

        @property
        def active_fret(self):
            """
            Retrieves the currently active fret index.

            OUT:
                int: Active fret index (0 to 12).
            """
            return self.held_frets[-1] if self.held_frets else 0

        @property
        def active_fret_key_name(self):
            """
            Retrieves the keyboard key label for the active fret.

            OUT:
                str: Key label name, or '-' if open strings.
            """
            af = self.active_fret
            return FRET_KEY_NAMES.get(af, "-")

        def press_fret(self, fret):
            """
            Registers a fret key press into the held stack.

            IN:
                fret - int: Fret index pressed (1 to 12).

            OUT:
                None
            """
            if fret not in self.held_frets:
                self.held_frets.append(fret)

        def release_fret(self, fret):
            """
            Removes a fret key from the held stack upon release.

            IN:
                fret - int: Fret index released (1 to 12).

            OUT:
                None
            """
            if fret in self.held_frets:
                self.held_frets.remove(fret)

        def pluck_string(self, string_idx, fret_idx, now=None):
            """
            Plucks a single guitar string and updates vibration timing.

            IN:
                string_idx - int: String index (1 to 6).
                fret_idx - int: Fret index (0 to 12).
                now - float, optional: Current timestamp in seconds.

            OUT:
                None
            """
            if now is None:
                now = time.time()
            js_play_note(string_idx, fret_idx)
            self.string_active_until[string_idx] = now + 0.35
            self.string_last_fret[string_idx] = fret_idx

        def trigger_strum(self, string_order, now=None):
            """
            Enqueues a staggered multi-string strum.

            IN:
                string_order - list of int: Sequence of string indices to strum.
                now - float, optional: Current timestamp in seconds.

            OUT:
                None
            """
            if now is None:
                now = time.time()
            fret = self.active_fret
            delay = 0.028
            is_downstroke = (string_order[0] == 6)

            for idx, s_idx in enumerate(string_order):
                target_time = now + (idx * delay)
                self.pending_strums.append((target_time, s_idx, fret))

        def is_string_vibrating(self, string_idx, now=None):
            """
            Determines whether a string is currently vibrating.

            IN:
                string_idx - int: String index (1 to 6).
                now - float, optional: Current timestamp in seconds.

            OUT:
                bool: True if the string is vibrating, False otherwise.
            """
            if now is None:
                now = time.time()
            return now < self.string_active_until.get(string_idx, 0.0)

        def get_string_note(self, string_idx, fret_idx):
            """
            Retrieves the musical pitch name for a string and fret.

            IN:
                string_idx - int: String index (1 to 6).
                fret_idx - int: Fret index (0 to 12).

            OUT:
                str: Pitch note name.
            """
            notes = NOTES.get(string_idx, [])
            if 0 <= fret_idx < len(notes):
                return notes[fret_idx]
            return "???"

        def update(self):
            """
            Processes queued strum notes whose playback time has arrived.

            OUT:
                None
            """
            now = time.time()
            if not self.pending_strums:
                return

            remaining = []
            for t, s_idx, fret in self.pending_strums:
                if now >= t:
                    self.pluck_string(s_idx, fret, now)
                else:
                    remaining.append((t, s_idx, fret))
            self.pending_strums = remaining

        def reset(self):
            """
            Resets all active frets, vibration states, and queued strums.

            OUT:
                None
            """
            self.held_frets = []
            self.pending_strums = []
            self.string_active_until = {i: 0.0 for i in range(1, 7)}
            self.string_last_fret = {i: 0 for i in range(1, 7)}

    engine = JSGuitarEngine()

    class JSGuitarDisplayable(renpy.Displayable):
        def __init__(self, engine, **kwargs):
            """
            Initializes the raw keyboard input displayable.

            IN:
                engine - JSGuitarEngine: Guitar engine instance.

            OUT:
                None
            """
            super(JSGuitarDisplayable, self).__init__(**kwargs)
            self.engine = engine
            self.held_string_keys = set()
            self.held_strum_keys = set()

        def render(self, width, height, st, at):
            """
            Renders the displayable surface.

            IN:
                width - int: Allocated render width.
                height - int: Allocated render height.
                st - float: Show time in seconds.
                at - float: Animation time in seconds.

            OUT:
                renpy.Render: Render surface object.
            """
            return renpy.Render(0, 0)

        def event(self, ev, x, y, st):
            """
            Intercepts raw SDL keyboard events for frets, plucks, and strums.

            IN:
                ev - pygame.event.Event: Pygame event object.
                x - int: Mouse X coordinate.
                y - int: Mouse Y coordinate.
                st - float: Show time in seconds.

            OUT:
                str or None: Return value to exit the screen, or None.
            """
            now = time.time()

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return "quit"

                if ev.key in FRET_KEYS:
                    fret = FRET_KEYS[ev.key]
                    self.engine.press_fret(fret)
                    raise renpy.IgnoreEvent()

                if ev.key in STRING_KEYS:
                    if ev.key not in self.held_string_keys:
                        self.held_string_keys.add(ev.key)
                        s_idx = STRING_KEYS[ev.key]
                        self.engine.pluck_string(s_idx, self.engine.active_fret, now)
                    raise renpy.IgnoreEvent()

                if ev.key == pygame.K_h:
                    if ev.key not in self.held_strum_keys:
                        self.held_strum_keys.add(ev.key)
                        self.engine.trigger_strum([6, 5, 4, 3, 2, 1], now)
                    raise renpy.IgnoreEvent()

                if ev.key == pygame.K_u:
                    if ev.key not in self.held_strum_keys:
                        self.held_strum_keys.add(ev.key)
                        self.engine.trigger_strum([1, 2, 3, 4, 5, 6], now)
                    raise renpy.IgnoreEvent()

            elif ev.type == pygame.KEYUP:
                if ev.key in FRET_KEYS:
                    fret = FRET_KEYS[ev.key]
                    self.engine.release_fret(fret)
                    raise renpy.IgnoreEvent()

                if ev.key in STRING_KEYS:
                    self.held_string_keys.discard(ev.key)
                    raise renpy.IgnoreEvent()

                if ev.key in (pygame.K_h, pygame.K_u):
                    self.held_strum_keys.discard(ev.key)
                    raise renpy.IgnoreEvent()

            return None

    def get_songs_dir():
        """
        Retrieves the directory path for custom guitar songs.

        OUT:
            str: Absolute path to guitar songs directory.
        """
        songs_dir = os.path.join(renpy.config.basedir, "guitar_songs")
        if not os.path.exists(songs_dir):
            try:
                os.makedirs(songs_dir)
            except Exception:
                pass
        return songs_dir

    def parse_song_header(filepath):
        """
        Reads metadata headers from a song text file.

        IN:
            filepath - str: Path to the song file.

        OUT:
            dict: Song metadata dictionary containing title, author, and block_time.
        """
        info = {
            "title": os.path.splitext(os.path.basename(filepath))[0],
            "author": store._("Unknown"),
            "block_time": 0.1
        }
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("["):
                        if line.lower() == "[notes]":
                            break
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip().lower()
                        v = v.strip()
                        if k == "title":
                            info["title"] = v
                        elif k == "author":
                            info["author"] = v
                        elif k == "block_time":
                            try:
                                info["block_time"] = max(0.01, float(v))
                            except ValueError:
                                pass
        except Exception:
            pass
        return info

    def scan_available_songs():
        """
        Scans the guitar songs directory for valid song files.

        OUT:
            list of dict: List of discovered song metadata dictionaries.
        """
        songs_dir = get_songs_dir()
        songs = []
        if not os.path.isdir(songs_dir):
            return songs
        for fname in os.listdir(songs_dir):
            if fname.lower().endswith(".txt"):
                fpath = os.path.join(songs_dir, fname)
                if os.path.isfile(fpath):
                    hdr = parse_song_header(fpath)
                    songs.append({
                        "filename": fname,
                        "filepath": fpath,
                        "title": hdr.get("title", fname),
                        "author": hdr.get("author", store._("Unknown")),
                        "block_time": hdr.get("block_time", 0.1)
                    })
        songs.sort(key=lambda item: item["title"].lower())
        return songs

    def get_song_menu_options():
        """
        Builds the formatted option tuples for the neat_menu_scroll song selector.

        OUT:
            list of tuple: List of (caption, song_dict) entries.
        """
        avail_songs = scan_available_songs()
        options = []
        for song_item in avail_songs:
            if song_item.get("author") and song_item["author"] != store._("Unknown"):
                caption = "%s - %s" % (song_item["title"], song_item["author"])
            else:
                caption = song_item["title"]
            options.append((caption, song_item))
        if not options:
            options = [(store._("No songs found"), False)]
        return options

    def restore_sayori_guitar():
        """
        Restores Sayori character object if accidentally overwritten by a dict.
        Fuck you Ren'Py.
        """
        if isinstance(getattr(store, "s", None), dict) or not callable(getattr(store, "s", None)):
            store.s = store.DynamicCharacter('s_name', image='sayori', what_prefix='', what_suffix='', ctc="ctc", ctc_position="fixed")

    def parse_song_file(filepath):
        """
        Parses a complete song file into playback events.

        IN:
            filepath - str: Path to the song file.

        OUT:
            tuple: (header, events, total_duration) where events is a list of (timestamp, string_idx, fret_idx).
        """
        header = {
            "title": os.path.splitext(os.path.basename(filepath))[0],
            "author": store._("Unknown"),
            "block_time": 0.1
        }
        events = []
        in_notes = False
        current_time = 0.0
        strum_delay = 0.028

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception:
            return header, events, 0.0

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("["):
                in_notes = (line.lower() == "[notes]")
                continue
            if not in_notes:
                if "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip().lower()
                    v = v.strip()
                    if k == "title":
                        header["title"] = v
                    elif k == "author":
                        header["author"] = v
                    elif k == "block_time":
                        try:
                            header["block_time"] = max(0.01, float(v))
                        except ValueError:
                            pass
                continue

            btime = header["block_time"]
            parts = line.split()
            cmd = parts[0].lower()

            if cmd in ("wait", "pause", "rest", "_"):
                if len(parts) > 1:
                    try:
                        blocks = float(parts[1])
                        current_time += blocks * btime
                    except ValueError:
                        pass
                else:
                    current_time += btime
                continue

            action = "auto"
            note_tokens = line
            if cmd in ("strum", "upstrum", "pluck"):
                action = cmd
                note_tokens = line[len(cmd):].strip()

            raw_notes = [t.strip() for t in note_tokens.split(",") if t.strip()]
            parsed_notes = []
            for token in raw_notes:
                if ":" in token:
                    sp = token.split(":", 1)
                    try:
                        s_idx = int(sp[0].strip())
                        f_idx = int(sp[1].strip())
                        if 1 <= s_idx <= 6 and 0 <= f_idx <= 12:
                            parsed_notes.append((s_idx, f_idx))
                    except ValueError:
                        pass

            if not parsed_notes:
                continue

            if action == "pluck" or (action == "auto" and len(parsed_notes) <= 2):
                for s_idx, f_idx in parsed_notes:
                    events.append((current_time, s_idx, f_idx))
            elif action == "upstrum":
                sorted_notes = sorted(parsed_notes, key=lambda x: x[0])
                for idx, (s_idx, f_idx) in enumerate(sorted_notes):
                    events.append((current_time + (idx * strum_delay), s_idx, f_idx))
            else:
                sorted_notes = sorted(parsed_notes, key=lambda x: x[0], reverse=True)
                for idx, (s_idx, f_idx) in enumerate(sorted_notes):
                    events.append((current_time + (idx * strum_delay), s_idx, f_idx))

        events.sort(key=lambda x: x[0])
        max_ev_time = max((ev[0] for ev in events), default=0.0)
        total_duration = max(current_time, max_ev_time) + 0.6
        return header, events, total_duration

    class JSGuitarSongPlayer(object):
        def __init__(self, engine):
            """
            Initializes the song player controller.

            IN:
                engine - JSGuitarEngine: Guitar engine instance.
            """
            self.engine = engine
            self.events = []
            self.event_idx = 0
            self.start_time = 0.0
            self.is_playing = False
            self.finished = False
            self.end_time = 0.0

        def load_song(self, filepath):
            """
            Loads and parses a song file for playback.

            IN:
                filepath - str: Path to the song file.

            OUT:
                dict: Song metadata header.
            """
            header, events, duration = parse_song_file(filepath)
            self.events = events
            self.event_idx = 0
            self.finished = False
            self.is_playing = False
            self.end_time = duration
            return header

        def start(self):
            """
            Begins song playback.
            """
            self.start_time = time.time()
            self.event_idx = 0
            self.is_playing = True
            self.finished = False

        def stop(self):
            """
            Stops song playback and cleans up audio channels.
            """
            self.is_playing = False
            self.finished = True
            js_cleanup()
            self.engine.reset()

        def update(self):
            """
            Updates playback timing and triggers due note events.
            """
            if not self.is_playing or self.finished:
                return
            now = time.time()
            elapsed = now - self.start_time
            while self.event_idx < len(self.events):
                ev_time, s_idx, f_idx = self.events[self.event_idx]
                if elapsed >= ev_time:
                    self.engine.pluck_string(s_idx, f_idx, now)
                    self.event_idx += 1
                else:
                    break
            if self.event_idx >= len(self.events) and elapsed >= self.end_time:
                self.finished = True
                self.is_playing = False

    class JSGuitarPlaybackDisplayable(renpy.Displayable):
        def __init__(self, player, **kwargs):
            """
            Initializes the playback event listener displayable.

            IN:
                player - JSGuitarSongPlayer: Song player instance.
            """
            super(JSGuitarPlaybackDisplayable, self).__init__(**kwargs)
            self.player = player

        def render(self, width, height, st, at):
            """
            Renders the displayable surface.

            IN:
                width - int: Allocated render width.
                height - int: Allocated render height.
                st - float: Show time in seconds.
                at - float: Animation time in seconds.

            OUT:
                renpy.Render: Render surface object.
            """
            return renpy.Render(0, 0)

        def event(self, ev, x, y, st):
            """
            Intercepts Escape key to stop song playback.

            IN:
                ev - pygame.event.Event: Pygame event object.
                x - int: Mouse X coordinate.
                y - int: Mouse Y coordinate.
                st - float: Show time in seconds.

            OUT:
                str or None: Return value to exit the screen, or None.
            """
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                self.player.stop()
                return "stop"
            return None


screen mg_guitar_playback_scr(player):
    modal True
    zorder 50

    if renpy.loadable("mod_assets/games/guitar/guitar_test.png"):
        add "mod_assets/games/guitar/guitar_test.png"
    else:
        add Solid("#121620")

    add js_guitar.JSGuitarPlaybackDisplayable(player)

    timer 0.02 repeat True action [Function(player.update), If(player.finished, Return("finished"))]


screen mg_guitar_scr(engine):
    modal True
    zorder 50

    if renpy.loadable("mod_assets/games/guitar/guitar_test.png"):
        add "mod_assets/games/guitar/guitar_test.png"
    else:
        add Solid("#121620")

    add js_guitar.JSGuitarDisplayable(engine)

    timer 0.03 repeat True action Function(engine.update)


label mg_guitar(mg_obj=None):
    $ Sayori.setInGame(True)
    $ js_update_rpc(state="Playing Guitar")
    $ js_guitar.engine.reset()
    $ js_guitar.restore_sayori_guitar()

    $ _guitar_running = True
    while _guitar_running:
        $ _mode_options = [
            (_("Play a Song"), "play_song"),
            (_("Free Play"), "free_play")
        ]
        call screen neat_menu_scroll(_mode_options, (_("Nevermind."), "exit"))
        $ _guitar_mode = _return

        if _guitar_mode == "free_play":
            $ js_guitar.engine.reset()
            call screen mg_guitar_scr(js_guitar.engine)
            $ js_guitar.js_cleanup()

        elif _guitar_mode == "play_song":
            $ _song_select_running = True
            while _song_select_running:
                $ _song_options = js_guitar.get_song_menu_options()

                call screen neat_menu_scroll(_song_options, (_("Back"), False))
                $ _selected_song = _return

                if not _selected_song:
                    $ _song_select_running = False
                else:
                    $ _song_player = js_guitar.JSGuitarSongPlayer(js_guitar.engine)
                    $ _song_player.load_song(_selected_song["filepath"])
                    $ js_guitar.engine.reset()
                    $ _song_player.start()

                    call screen mg_guitar_playback_scr(_song_player)

                    $ _song_player.stop()

        else:
            $ _guitar_running = False


    $ js_guitar.js_cleanup()
    $ js_guitar.restore_sayori_guitar()
    $ Sayori.setInGame(False)
    $ js_update_rpc(state="In the spaceroom")
    return


init 10 python in js_guitar:
    restore_sayori_guitar()
    if not any(g.label == "mg_guitar" for g in store._MG_OBJECTS):
        store.register_minigame(
            label="mg_guitar",
            name=store._("Guitar"),
            image="mod_assets/images/minigames/covers/ttt_cover.png",
            unlocked=True,
            description=store._("Play the guitar!")
        )
