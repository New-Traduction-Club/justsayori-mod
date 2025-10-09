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
            image_directory,
            image_failsafe=None,
            decoration_permitted=None,
            when_enter=None,
            when_leave=None,
        ):

            """
            Constructor
            
            Feed:
                id - a unique id for this background. Will raise exceptions if a Location with a duplicate initialized
                image_directory - Path to images
                image_failsafe - a dict of image tags with the following keys:
                    "DAY", "NIGHT", these will have image tags as their values, which should be used to display
                decoration_permitted - List of strings representing categories for decorations which are supported for this Location
                    If None, this is set to an empty list. Empty lists mean no decorations are supported
                    (Default: None)
                when_enter - Function to run when changing into this Location. If None, nothing is done.
                    (Default: None)
                when_leave - Function to run when leaving this Location. If None, nothing is done.
                    (Default: None)
            """

            # Check it can be loaded.

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

            # Check if loadable

            if not renpy.loadable(daytime_path):
                raise Exception("[ERROR]: Daytime image ('{0}') is not loadable.".format(daytime_path))
            # And night
            if not renpy.loadable(night_path):
                raise Exception("[ERROR]: Nighttime image ('{0}') is not loadable.".format(night_path))

            # Create object
            self.id = id

            # Make Daytime tag
            self.daytime_tag = "{0}_day".format(id)
            # Nighttime tag
            self.nighttime_tag = "{0}_night".format(id)

            # CORRECCIÓN: Registrar imágenes usando la función estándar renpy.image.
            # Esto es más robusto y soluciona el problema de las vistas previas.
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
        Main class
        """

        def __init__(self, fae_sunup, fae_sundown):

            """
            Constructor

            Object managing everything.
            """

            self.room = None
            self.decoration = dict()

            self.fae_sunup = datetime.time(fae_sunup)
            self.fae_sundown = datetime.time(fae_sundown)

            # State
            self.__is_seeing_day = self.is_daytime()
            
            # Event Handlers
            self.day_to_night_switch = FAEEvent()

            self.night_to_day_switch = FAEEvent()
        
        def select_room(self, new_room, **kwargs):

            """
            Sets the location.

            Doesn't persist

            FEED:
                new_location = new location
            
            """


            if new_room.when_enter is not None:

                new_room.when_enter(self.room, **kwargs)

            self.room = new_room
        
        def room_switcher(self, new_room, **kwargs):

            """
            Changer for location

            FEED:
                new_location = new location
            
            """

            if self.room.when_leave is not None:

                self.room.when_leave(new_room, **kwargs)
            
            self.select_room(new_room, **kwargs)
        

        def is_daytime(self):

            """
            Checks if it's day at the moment

            RESULT 
                True if day
                Otherwise False

            """

            return self.fae_sunup <= datetime.datetime.now().time() < self.fae_sundown
        
        def render(self, dissolve_all=False, complete_reset=False):
            """
            Creates the location

            FEED:
                dissolve_all = dissolve everything
                complete_reset = Do we want to re-render everything?
            """

            renpy.with_statement(None)

            if complete_reset:
                renpy.scene()
                renpy.show("black")
            
            room = None

            if dissolve_all or complete_reset:
                room = self.room.find_room_now()
            
            # Draw the room if it's not being shown
            if room is not None:
                renpy.show(room, tag="main_bg", zorder=FAE_ROOM_ZORDER)
            
            else:
                fae_utilities.log("Unable to draw room: no room image was found.")
            
            # Dissolving everything

            if dissolve_all or complete_reset:
                renpy.hide("black")
                renpy.with_statement(Dissolve(1.0))
            
            return
        
        def form(self):
            """
            Draws the location without flashy-washy
            """

            room = self.room.find_room_now()
            if room is not None:
                renpy.show(room, tag="main_bg", zorder=FAE_ROOM_ZORDER)
            
            else:
                fae_utilities.log("Unable to show room: no room image was found.")
            
            return
        
        def is_seeing_day(self):
            """
            Check if we're showing the day room
            """

            return self.__is_seeing_day
        
        def reset_checker(self):
            """
            Check if we need to reset for time change.
            """

            # If it's day and we're showing the night room, we need to reset
            if self.is_daytime() and self.__is_seeing_day is False:
                self.__is_seeing_day = True
                # self.form(dissolve_all=True)
                self.render(dissolve_all=True)

                # Run events
                self.night_to_day_switch()
            
            # If it's night and we're showing the day room we should reset
            elif not self.is_daytime() and self.__is_seeing_day is True:
                self.__is_seeing_day = False
                # self.form(dissolve_all=True)
                self.render(dissolve_all=True)

                # Run event
                self.day_to_night_switch()
        
        def save(self):
            """
            Saves room related into persistent
            """

            persistent._present_room = self.room.id

        def transition_to_room(self, trans=Dissolve(1.0)):
            """
            Shows the current room with a transition, correctly replacing the old one.
            """
            current_room_tag = self.room.find_room_now()
            
            renpy.show(current_room_tag, tag="main_bg", zorder=FAE_ROOM_ZORDER)
            renpy.with_statement(trans)

init -5 python in fae_rooms:
    import store

    def register_room(id, image_directory, **kwargs):
        """
        Public helper so submods can add rooms safely...
        Usage (in any submod .rpy):
            init 5 python:
                import store.fae_rooms as fr
                fr.register_room("forest", "forest")
        Expects files:
            mod_assets/rooms/{image_directory}/{id}-day.png
            mod_assets/rooms/{image_directory}/{id}-night.png
        Real Example:
            mod_assets/rooms/forest/forest-night.png
            mod_assets/rooms/forest/forest-night.png
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
        image_directory="spaceroom"
    )

    bedroom = Rooms(
        id="bedroom",
        image_directory="bedroom"
    )

    d25room = Rooms(
        id="d25room",
        image_directory="d25room"
    )


    
    
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

##### BGs selector
default bg_selected_index = 0

init -1 python:
    def _bg_get_rooms():
        import store
        return sorted(store.fae_rooms.ROOM_DEFS.values(), key=lambda r: r.id)

    def _bg_apply(room_obj):
        """
        Safe apply from a screen action:
        - No with_statement / transition (evita 'Cannot start an interaction...')
        - Actualiza room y lo muestra directamente.
        - Guarda selección en persistent.
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
                                
                                text r.id style "mg_card_title" size 14

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
                        
                    text _current.id style "mg_detail_title"
                    text _("Ready to change!") style "mg_detail_desc"
                    
                    textbutton _("Change") style "big_play_button" text_style "big_play_button_text" action [
                        Function(_bg_apply, _current),
                        Return(True)
                    ]
                else:
                    frame style "song_image_placeholder" xsize DETAIL_W ysize DETAIL_H
                    text _("Select a background") style "mg_detail_title"

                textbutton _("Close") style "mg_close_button" text_style "mg_close_button_text" action [
                    Hide("bg_hub"),
                    Return(False)
                ]
