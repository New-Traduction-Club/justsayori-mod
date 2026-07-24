# Start in the spaceroom (as usual)
default persistent._present_room = "spaceroom"

# Start in the spaceroom (as usual)
default persistent.fae_sunup = 6
default persistent.fae_sundown = 18
default persistent.fae_moonup = 21

init -1 python in fae_rooms:

    import store

    ROOM_DEFS = dict()

    def fae_decorationManager(event=None):
        """
        Add a way to decorate the spaceroom on the fly.
        """

        if event is None:
            return None
        
        if event == "o31":
            halloweenDecoration()
        
        elif event == "d25":

            christmasDecoration()
    

    def halloweenDecoration():
        return None

    def christmasDecoration():
        return None


init -20 python:

    import os
    
    # The zorder of the room. Behind Sayori, in front of sky.

    FAE_ROOM_ZORDER = 1

    class Rooms(object):

        """
        Props:
            id
            image_directory
            when_enter
            when_leave
            decoration_permitted
        """

        # Room file suffixes (not including extentions)


        DAY = "-day"
        NIGHT = "-night"

        IMG_EXTENSION = ".png"

        def __init__(
            self,
            id,
            display_name,
            image_directory,
            image_failsafe=None,
            decoration_permitted=None,
            when_enter=None,
            when_leave=None,
        ):

            """
            Constructor for Rooms object.

            IN:
                id - str: Unique identifier for the room.
                display_name - str: Translatable name shown in the UI.
                image_directory - str: Subdirectory for the images.
                image_failsafe - dict: Unused failsafe dictionary.
                decoration_permitted - list of str: Supported decoration categories.
                when_enter - function: Callback triggered when entering.
                when_leave - function: Callback triggered when leaving.
            """

            if id in store.fae_rooms.ROOM_DEFS:
                raise Exception("[ERROR]: A room with id '{0}' already exists.".format(id))
            
            ### android issues
            # if not os.path.isdir(renpy.config.gamedir + "/mod_assets/rooms/{0}".format(image_directory)):
            #     raise Exception(
            #         "[ERROR]: Image directory '{0}' is not a directory.".format(
            #             os.path.join(renpy.config.gamedir, "mod_assets", "rooms", image_directory)
            #         )
            #     )
            
            
            
            
            daytime_path = "mod_assets/rooms/{0}/{1}".format(image_directory, id + Rooms.DAY + Rooms.IMG_EXTENSION)
            night_path = "mod_assets/rooms/{0}/{1}".format(image_directory, id + Rooms.NIGHT + Rooms.IMG_EXTENSION)

            if not renpy.loadable(daytime_path):
                raise Exception("[ERROR]: Daytime image ('{0}') is not loadable.".format(daytime_path))
            if not renpy.loadable(night_path):
                raise Exception("[ERROR]: Nighttime image ('{0}') is not loadable.".format(night_path))

            self.id = id
            self.display_name = display_name

            self.daytime_tag = "{0}_day".format(id)
            self.nighttime_tag = "{0}_night".format(id)

            renpy.image(self.daytime_tag, daytime_path)
            renpy.image(self.nighttime_tag, night_path)

            if decoration_permitted is None:
                self.decoration_permitted = list()
            
            self.when_enter = when_enter
            self.when_leave = when_leave

            store.fae_rooms.ROOM_DEFS[self.id] = self

        def find_room_now(self):


            if store.main_background.is_daytime():

                return self.daytime_tag
            return self.nighttime_tag
    
    class FAERooms(object):

        """
        Main background room manager class.
        """

        def __init__(self, fae_sunup, fae_sundown):
            """
            Constructor for background manager.

            IN:
                fae_sunup - int: Hour representing sunrise.
                fae_sundown - int: Hour representing sunset.
            """

            self.room = None
            self.decoration = dict()

            self.fae_sunup = datetime.time(fae_sunup)
            self.fae_sundown = datetime.time(fae_sundown)

            self.__is_seeing_day = self.is_daytime()
            
            self.day_to_night_switch = FAEEvent()
            self.night_to_day_switch = FAEEvent()
        
        def select_room(self, new_room, **kwargs):
            """
            Sets the active room location without persistence.

            IN:
                new_room - Rooms: The new room object to select.
                **kwargs - Additional arguments passed to the enter callback.
            """

            if new_room.when_enter is not None:
                new_room.when_enter(self.room, **kwargs)

            self.room = new_room
        
        def room_switcher(self, new_room, **kwargs):
            """
            Changes location and triggers transition callbacks.

            IN:
                new_room - Rooms: The new room object to transition to.
                **kwargs - Additional arguments passed to callbacks.
            """

            if self.room.when_leave is not None:
                self.room.when_leave(new_room, **kwargs)
            
            self.select_room(new_room, **kwargs)
        

        def is_daytime(self):
            """
            Checks if it is currently daytime.

            OUT:
                bool: True if daytime, False otherwise.
            """

            return self.fae_sunup <= datetime.datetime.now().time() < self.fae_sundown
        
        def render(self, dissolve_all=False, complete_reset=False):
            """
            Renders the room background.

            IN:
                dissolve_all - bool: True to apply dissolve transitions.
                complete_reset - bool: True to re-render all elements.
            """

            renpy.with_statement(None)

            if complete_reset:
                renpy.scene()
                renpy.show("black")
            
            room = None

            if dissolve_all or complete_reset:
                room = self.room.find_room_now()
            
            if room is not None:
                renpy.show(room, tag="main_bg", zorder=FAE_ROOM_ZORDER)
            else:
                fae_utilities.log("Unable to draw room: no room image was found.")
            
            if dissolve_all or complete_reset:
                renpy.hide("black")
                renpy.with_statement(Dissolve(1.0))
            
            return
        
        def form(self):
            """
            Draws the location room background instantly without transitions.
            """

            room = self.room.find_room_now()
            if room is not None:
                renpy.show(room, tag="main_bg", zorder=FAE_ROOM_ZORDER)
            else:
                fae_utilities.log("Unable to show room: no room image was found.")
            
            return
        
        def is_seeing_day(self):
            """
            Checks if the manager is currently displaying the daytime room background.

            OUT:
                bool: True if seeing day, False otherwise.
            """

            return self.__is_seeing_day
        
        def reset_checker(self):
            """
            Checks if the active background needs to change due to day/night time cycles.
            """

            if self.is_daytime() and self.__is_seeing_day is False:
                self.__is_seeing_day = True
                self.render(dissolve_all=True)
                self.night_to_day_switch()
            
            elif not self.is_daytime() and self.__is_seeing_day is True:
                self.__is_seeing_day = False
                self.render(dissolve_all=True)
                self.day_to_night_switch()
        
        def save(self):
            """
            Saves the active room ID to persistent storage.
            """

            persistent._present_room = self.room.id

        def transition_to_room(self, trans=Dissolve(1.0)):
            """
            Shows the current room background with a specified transition.

            IN:
                trans - Transition: Ren'Py transition effect to apply.
            """
            current_room_tag = self.room.find_room_now()
            
            renpy.show(current_room_tag, tag="main_bg", zorder=FAE_ROOM_ZORDER)
            renpy.with_statement(trans)

init -5 python in fae_rooms:
    import store

    def register_room(id, image_directory, **kwargs):
        """
        Registers a custom room background.

        IN:
            id - str: Unique identifier for the room.
            image_directory - str: Subdirectory for the images.
            **kwargs - Optional keyword arguments passed to the Rooms constructor.

        OUT:
            Rooms: The registered room object.
        """
        if id in ROOM_DEFS:
            return ROOM_DEFS[id]
        room = store.Rooms(id=id, image_directory=image_directory, **kwargs)
        ROOM_DEFS[id] = room
        return room

init 100 python:

    main_background = FAERooms(
        fae_sunup=int(store.persistent.fae_sunup),
        fae_sundown=int(store.persistent.fae_sundown)
    )

    spaceroom = Rooms(
        id="spaceroom",
        image_directory="spaceroom",
        display_name=__("Spaceroom")
    )

    bedroom = Rooms(
        id="bedroom",
        image_directory="bedroom",
        display_name=__("Bedroom")
    )

    # d25room = Rooms(
    #     id="d25room",
    #     image_directory="d25room"
    # )


    
    
    initial_room_id = persistent._present_room
    if not initial_room_id or initial_room_id not in fae_rooms.ROOM_DEFS:
        initial_room_id = "spaceroom"
        persistent._present_room = "spaceroom"
        
    initial_room_obj = fae_rooms.ROOM_DEFS[initial_room_id]
    
    main_background.room = initial_room_obj

    # Run the appropriate eventhandler
    # If it's day, we need to run the switch and vice versa
    if main_background.is_daytime():
        main_background.night_to_day_switch()
    
    else:
        main_background.day_to_night_switch()

default bg_selected_index = 0

init -1 python:
    def _bg_get_rooms():
        """
        Retrieves all registered room background objects, sorted by ID.

        OUT:
            list of Rooms: Sorted list of Rooms objects.
        """
        import store
        return sorted(store.fae_rooms.ROOM_DEFS.values(), key=lambda r: r.id)

    def _bg_apply(room_obj):
        """
        Switches the active room background and saves it to persistent storage.

        IN:
            room_obj - Rooms: The new room object to apply.
        """
        import store
        store.main_background.room_switcher(room_obj)
        store.main_background.save()
        persistent._present_room = room_obj.id
        renpy.hide_screen("bg_hub")

screen bg_hub():
    zorder 100
    tag menu
    modal True

    default bg_has_changed = False

    add Solid("#000000cc")

    $ _rooms = _bg_get_rooms()
    $ bg_selected_index = 0 if not _rooms else min(bg_selected_index, len(_rooms)-1)
    $ _current = _rooms[bg_selected_index] if _rooms else None

    $ THUMB_W = 180
    $ THUMB_H = 102
    $ DETAIL_W = 406
    $ DETAIL_H = 228
    $ BASE_H = 720.0

    frame style "mg_hub_frame" xalign 0.5 yalign 0.5 xsize 1180 ysize 620:
        hbox:
            spacing 40

            viewport style "mg_cards_viewport" xsize 620 yfill True scrollbars "vertical" mousewheel True:
                grid 3 18:
                    for idx, r in enumerate(_rooms):
                        $ selected = (idx == bg_selected_index)
                        $ _btn_style = "mg_card_button_selected" if selected else "mg_card_button"
                        
                        button style _btn_style:
                            action [SetVariable("bg_selected_index", idx), Hide("bg_hub"), Show("bg_hub")]
                            at mg_card_hover
                            ysize THUMB_H + 30
                            
                            vbox:
                                spacing 4
                                frame:
                                    background Solid("#000")
                                    xsize THUMB_W
                                    ysize THUMB_H
                                    clipping True
                                    
                                    add r.daytime_tag:
                                        zoom THUMB_H / BASE_H
                                        xalign 0.5
                                        yalign 0.5
                                
                                text r.display_name style "mg_card_title" size 14

            vbox style "song_info_vbox" xsize DETAIL_W:
                if _current:
                    frame:
                        background Solid("#000")
                        xsize DETAIL_W
                        ysize DETAIL_H
                        clipping True
                        
                        add _current.daytime_tag:
                            zoom DETAIL_H / BASE_H
                            xalign 0.5
                            yalign 0.5
                        
                    text _current.display_name style "mg_detail_title"
                    # text _("Ready to change!") style "mg_detail_desc"
                    
                    textbutton _("Change") style "big_play_button" text_style "big_play_button_text" action [
                        Function(_bg_apply, _current),
                        Return(True),
                        SetScreenVariable("bg_has_changed", True)
                    ] sensitive (_current.id != persistent._present_room)
                else:
                    frame style "song_image_placeholder" xsize DETAIL_W ysize DETAIL_H
                    text _("Select a background") style "mg_detail_title"

                textbutton _("Close") style "mg_close_button" text_style "mg_close_button_text" action [
                    Hide("bg_hub"),
                    If(bg_has_changed, Return(True), Jump("bg_hub_no_change"))
                ]

label bg_hub_no_change:

    if Affection.isLove(higher=True):
        $ chosen_line = renpy.random.choice([
            __("any place is perfect as long as I'm with you."),
            __("I honestly love this spot when I'm with you."),
            __("it doesn't matter where we are, as long as we're together."),
            __("I'm happy just being here, right by your side.")
        ])
        s abfccaa "Oh, decided to keep it as is? That's fine, "
        extend abfcaaa "[chosen_line]"

    elif Affection.isEnamoured(higher=True):
        $ chosen_line = renpy.random.choice([
            __("I was actually getting really comfortable in this room."),
            __("so I don't have to get used to a new environment all of a sudden."),
            __("this room has its own charm, doesn't it?"),
            __("I've grown quite fond of being here, to be honest.")
        ])
        s abgbcaa "Changed your mind? Ehehe. I don't blame you, "
        extend abgbaaa "[chosen_line]"

    elif Affection.isAffectionate(higher=True):
        $ chosen_line = renpy.random.choice([
            __("this place already feels like our little corner!"),
            __("I like staying in this room a little longer."),
            __("we can just keep chatting right here."),
            __("it's actually pretty cozy in here.")
        ])
        s abhfaoa "Not feeling it? Well, no problem, "
        extend abbcaoa "[chosen_line]"

    elif Affection.isHappy(higher=True):
        $ chosen_line = renpy.random.choice([
            __("the important thing is that we keep talking!"),
            __("we'll just stay put then."),
            __("let's just enjoy the atmosphere here!"),
            __("let's just get back to our topic!")
        ])
        s abgbaoa "Did you change your mind? No worries! "
        extend abbbaoa "[chosen_line]"

    else:
        s abgbaoa "Oh, decided not to go anywhere?"
        s abagaoa "That's okay, we are fine here for now."

    return