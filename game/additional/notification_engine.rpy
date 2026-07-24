default persistent._fae_notifs_enabled = False

default persistent._fae_notif_sounds = True

init python in fae_notifs:
    
    import os
    import store

    FAE_WINDOW = None

    from plyer import notification


    def notify(title, message):
        """
        Triggers a desktop notification with specified title and message.

        IN:
            title - str: The title text for notification.
            message - str: The body text of notification.

        OUT:
            bool/None: True/None representing the success of notification trigger.
        """
        title = title
        message = message
        
        if renpy.windows or renpy.linux:

            return (
                notification.notify(
                    title=title,
                    message=message,
                    app_icon=(renpy.config.gamedir + '/mod_assets/icon.ico'),
                    timeout=10
                )
            )
        else:
            return None


    if renpy.windows:

        try:

            from plyer import notification

            can_show_notifs = True
        
        except ImportError:
            can_show_notifs = False

            store.fae_utilities.log("Couldn't import plyer")

        #from plyer import notification
        if store.fae_notifs.can_show_notifs:
            
            def notifyWindows():
                """
                Sends a default notification on Windows systems.

                OUT:
                    bool/None: Success status of the Windows notification.
                """

                title = 'Sayori'
                message = _('I have something to tell you!')

                return (
                    notification.notify(
                        title=title,
                        message=message,
                        app_icon=(renpy.config.gamedir + '/mod_assets/icon.ico'),
                        timeout=10
                    )
                )
 
                
    elif renpy.linux:

        try:
            import plyer

            can_show_notifs = True
        
        except ImportError:
            can_show_notifs = False
        
        if store.fae_notifs.can_show_notifs:

            def notifyLinux():
                """
                Sends a default notification on Linux systems.

                OUT:
                    bool/None: Success status of the Linux notification.
                """

                title = 'Sayori'
                message = _('I have something to tell you!')

                return (
                    plyer.notification.notify(
                        title=title,
                        message=message,
                        app_icon=(renpy.config.gamedir + '/mod_assets/icon.ico'),
                        timeout=10
                    )
                )
                
            
    else:
        store.fae_notifs.can_show_notifs = False

        print("Cannot detect current session type, disabling notifications.")
    