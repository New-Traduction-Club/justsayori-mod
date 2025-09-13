








label lockdown_check:

    $ version = renpy.version()

    if renpy.version_tuple > (7, 4, 11, 2266):

        scene black
        "{b}Warning:{/b} The version of Ren'Py you are trying to mod DDLC on has not been tested for modding compatibility."
        "The last recent version of Ren'Py that works for DDLC mods is \"{i}Ren'Py 7.4.10{/i}\"."
        "Running DDLC or your DDLC mod on a higher version than the one tested may introduce bugs and other game breaking features."

        menu:
            "By continuing to run your mod on [version!q], you acknoledge this disclaimer and the possible problems that can happen on a untested Ren'Py version."
            "I agree.":
                $ persistent.lockdown_warning = True
                return
    else:

        $ persistent.lockdown_warning = True
        return
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
