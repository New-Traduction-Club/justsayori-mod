init 5 python:
    ##### GIFT REGISTRATION FOR SUBMODDERS
    # To register a new gift, simply call the 'register_gift' function
    # You can do this in your own submod .rpy file as well
    # Make sure your 'init python' block has a priority greater than -1 (e.g., 'init 5 python')

    # register_gift parameters:
    # 1. filename: The exact name of the file to look for (e.g., "my_gift.gift")
    # 2. reaction_label: The label to jump to when the gift is found
    # 3. delete_after (optional): Defaults to True. If False, the file will not be deleted
    # 4. unlock_var (optional): The name of a persistent variable that will be set to True

    # Cookies
    store.js_gift_manager.register_gift(
        filename="cookies.gift",
        reaction_label="js_cookies_reaction",
        unlock_var="js_gift_cookies_unlocked"
    )

    # Otter plushie
    store.js_gift_manager.register_gift(
        filename="otter.gift",
        reaction_label="js_otter_reaction",
        unlock_var="js_gift_otter_unlocked"
    )
    
    # Yum! (a gift that doesn't get deleted)
    store.js_gift_manager.register_gift(
        filename="yum.gift",
        reaction_label="js_yum_reaction",
        delete_after=False
    )


##### REACTION LABELS
# This is where you write what Sayori says or does for each gift

label js_cookies_reaction:
    # You can now use the get_gift_count function to see how many times you've received this gift
    if store.js_gift_manager.get_gift_count("cookies.gift") > 1:
        s abhfaaa "Oh, more cookies! I love them!"
    else:
        s abhfaaa "I found cookies!"
    s "Yum!"
    # The persistent variable 'js_gift_cookies_unlocked' is now True
    return

label js_otter_reaction:
    s "An otter plushie!"
    s "It's so cute! Thank you so much, [player]~"
    # The persistent variable 'js_gift_otter_unlocked' is now True
    # You could use this variable to display the otter in the room, for example.
    $ persistent.js_gifts_otter = True
    return

label js_yum_reaction:
    s "Yum!"
    # Since delete_after is False, the 'yum.gift' file will still be there.
    return


##### STATUS LABELS

label js_no_gift_found:
    s "I checked just in case, but I didn't find any gifts for me this time!"
    return

label js_no_gifts_folder_error:
    s "Hmm... something's not right with my gifting system."
    s "I can't seem to find the 'gifts' folder..."
    s "[player], could you please make sure the 'gifts' folder is in the game's main directory?"
    return

##### MAIN LABEL TO CALL
# Instead of calling a python function directly, you can now use this label

label check_for_gifts:
    $ store.js_gift_manager.check_for_gifts()
    return
