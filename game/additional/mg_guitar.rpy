init 5 python in js_guitar:
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

    call screen mg_guitar_scr(js_guitar.engine)

    $ js_guitar.js_cleanup()
    $ Sayori.setInGame(False)
    $ js_update_rpc(state="In the spaceroom")
    return


init 10 python in js_guitar:
    if not any(g.label == "mg_guitar" for g in store._MG_OBJECTS):
        store.register_minigame(
            label="mg_guitar",
            name=store._("Guitar"),
            image="mod_assets/images/minigames/covers/ttt_cover.png",
            unlocked=True,
            description=store._("Play the guitar!")
        )
