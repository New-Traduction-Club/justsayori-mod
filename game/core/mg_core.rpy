##### MiniGame Registry Core (and a Hub)

default persistent.mg_registry = []
default mg_selected_index = 0

init -2 python:
    if not hasattr(store, "_MG_OBJECTS"):
        store._MG_OBJECTS = []

    class MiniGame(object):
        """
        Represents a mini game entry shown in the modern minigame hub.
        - label: Ren'Py label to call
        - name: Display name
        - image: Path to cover image (string) or None
        - unlocked: Bool or callable -> bool (re-evaluated when drawing)
        - condition: Optional callable/string for extra gating (returns bool)
        - description: Optional short text (future use)
        - prep: Optional callable executed before launching
        """
        def __init__(self, label, name, image, unlocked=True,
                     condition=None, description=None, prep=None, pid=None):
            self.label = label
            self.name = name
            self.image = image
            self._unlocked = unlocked
            self.condition = condition
            self.description = description
            self.prep = prep
            self.pid = pid or label

        @property
        def unlocked(self):
            base = self._unlocked() if callable(self._unlocked) else self._unlocked
            cond = True
            if self.condition:
                try:
                    cond = self.condition() if callable(self.condition) else renpy.python.py_eval(self.condition)
                except Exception:
                    cond = False
            return base and cond

        def launch(self):
            # Optional pre-exec
            if self.prep:
                try:
                    self.prep(self)
                except Exception:
                    pass
            renpy.call_in_new_context(self.label)

    def _sync_persistent_entry(mg):
        """Ensure a dict form of the MiniGame exists in persistent for simple state"""
        for entry in persistent.mg_registry:
            if entry.get("pid") == mg.pid:
                return
        persistent.mg_registry.append({
            "pid": mg.pid,
            "label": mg.label,
            "name": mg.name,
            "image": mg.image,
            "unlocked": True
        })

    def register_minigame(label, name, image, unlocked=True,
                          condition=None, description=None, prep=None, pid=None):
        """
        Public API to register a minigame
        Call this at init time (after the game's own label exists)
        Avoid duplicates via pid/label
        """
        # Prevent duplicates
        ident = pid or label
        for g in store._MG_OBJECTS:
            if g.pid == ident:
                return g
        mg = MiniGame(label, name, image, unlocked, condition, description, prep, ident)
        store._MG_OBJECTS.append(mg)
        _sync_persistent_entry(mg)
        return mg

    def get_registered_minigames(only_unlocked=True):
        """Return list of MiniGame objects, optionally filtering by unlocked"""
        if only_unlocked:
            return [g for g in store._MG_OBJECTS if g.unlocked]
        return list(store._MG_OBJECTS)

    # Optional helper to mirror already created FaE minigames (from games_reset_redo)
    def import_legacy_minigames(as_cover="mod_assets/images/minigames/default_cover.png"):
        """
        If you want to auto-wrap existing 'minigame' objects (from persistent.games_reset_redo),
        call this once after they are populated. Provide a fallback cover.
        """
        if hasattr(persistent, "games_reset_redo"):
            for legacy in persistent.games_reset_redo:
                register_minigame(
                    label=legacy.label,
                    name=legacy.name,
                    image=as_cover
                )

# styles

style mg_hub_frame is music_player_frame
style mg_cards_viewport is music_list_viewport
style mg_cards_grid:
    spacing 18

style mg_card_button is button:
    background Solid("#00000040")
    hover_background Solid("#ffffff20")
    padding (10, 10, 10, 10)
    xsize 200
    ysize 250

style mg_card_button_selected is mg_card_button:
    background Solid("#2e8bff60")

style mg_card_cover:
    xalign 0.5
    yalign 0.0

style mg_card_title is music_button_text:
    size 18
    xalign 0.5
    text_align 0.5

style mg_detail_title is song_info_title
style mg_detail_desc is song_info_author

style big_play_button is button:
    background Solid("#2ecc71")
    hover_background Solid("#3ee982")
    padding (18, 40)
    xalign 0.5
    yalign 0.0

style big_play_button_text is button_text:
    size 32
    color "#ffffff"
    bold True

style mg_close_button is music_player_close_button
style mg_close_button_text is music_player_close_button_text

transform mg_card_hover:
    on hover:
        ease 0.15 zoom 1.03
    on idle:
        ease 0.2 zoom 1.0

# the big boy of the screen >:)
screen modern_minigame_player():
    zorder 100
    tag menu
    modal True

    add Solid("#000000cc")

    $ _games = get_registered_minigames(True)
    $ mg_selected_index = 0 if not _games else min(mg_selected_index, len(_games)-1)
    $ _current = _games[mg_selected_index] if _games else None

    frame style "mg_hub_frame" xalign 0.5 yalign 0.5 at music_ui_pop:

        hbox:
            spacing 40

            viewport style "mg_cards_viewport" scrollbars "vertical" mousewheel True:
                has vbox
                python:
                    cols = 3
                    rows = []
                    for i, g in enumerate(_games):
                        if i % cols == 0:
                            rows.append([])
                        rows[-1].append((i, g))
                if _games:
                    for row in rows:
                        hbox:
                            spacing 18
                            for idx, g in row:
                                $ selected = (idx == mg_selected_index)
                                $ _mg_style = "mg_card_button_selected" if selected else "mg_card_button"
                                button style _mg_style:
                                    action SetVariable("mg_selected_index", idx)
                                    at mg_card_hover
                                    vbox:
                                        spacing 8
                                        if g.image:
                                            add g.image xalign 0.5 yalign 0.0
                                        else:
                                            frame:
                                                background Solid("#44444480")
                                                xsize 180
                                                ysize 180
                                        text g.name style "mg_card_title"
                else:
                    text _("No minigames registered.") style "music_button_text"

            vbox style "song_info_vbox":
                if _current:
                    if _current.image:
                        add _current.image xalign 0.5 yalign 0.0
                    else:
                        frame style "song_image_placeholder"

                    text _current.name style "mg_detail_title"
                    if _current.description:
                        text _current.description style "mg_detail_desc"
                    else:
                        text _("Ready to play!") style "mg_detail_desc"

                    textbutton _("Play") style "big_play_button" text_style "big_play_button_text" action Function(_current.launch)
                else:
                    frame style "song_image_placeholder"
                    text _("Select a game") style "mg_detail_title"

                textbutton _("Close") style "mg_close_button" text_style "mg_close_button_text" action Hide("modern_minigame_player")

# The transition handler
label mg_launcher_label(mg_label):
    call expression mg_label
    with Fade(2.0, 2.0, 2.0, color="#000")
    return

# The Main Label
label mg_hub:
    call screen modern_minigame_player
    return

##### Example registration (and a real registration)
init 10 python:
    # Example placeholders (ensure images exist or replace with valid paths)
    # Safe-guard not to duplicate on reload
    if not any(g.label == "mg_ttt" for g in _MG_OBJECTS):
        register_minigame(
            label="mg_ttt",
            name=_("Tic Tac Toe"),
            image="mod_assets/images/minigames/ttt_cover.png",
            unlocked=True
        )
    # if not any(g.label == "mg_reversi" for g in _MG_OBJECTS):
    #     register_minigame(
    #         label="mg_reversi",
    #         name=_("Reversi"),
    #         image="mod_assets/images/minigames/reversi_cover.png",
    #         unlocked=lambda: hasattr(persistent, "fae_reversi_unlocked_redux") and persistent.fae_reversi_unlocked_redux
    #     )
    # import_legacy_minigames()