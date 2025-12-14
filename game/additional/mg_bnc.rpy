#Bull and cows
init 5 python:
    def bnc_prep(self, restart = False, *args, **kwargs):
        self.state = 0 #0 = game not over, 1 = player won, -1 = player lost
        self.guessed = ""
        self.guessed_len = 0
        self.lifes = 0
        self.bulls = 0
        self.cows = 0
        
        ns = "0123456789" #All selectable numbers
        for i in range (renpy.random.randint(3, 6)):
            n = renpy.random.choice(ns) #Selected number
            self.guessed += n
            ns = ns.replace(n, "") #Remove the selected number from ns
        self.guessed_len = len(self.guessed)
        self.lifes = self.guessed_len
        self.last = "_ " * self.guessed_len
        
        def bnc_check(answer):
            self.last = ""
            self.bulls, self.cows = 0, 0
            for i in range(self.guessed_len):
                if answer[i] == self.guessed[i]:
                    self.bulls += 1
                    self.last += "{color=#00cc00}" + answer[i] + "{/color} "
                elif answer[i] in self.guessed:
                    self.cows += 1
                    self.last += "{color=#ffff00}" + answer[i] + "{/color} "
                else:
                    self.last += "{color=#ff0000}" + answer[i] + "{/color} "
            if self.bulls == self.guessed_len:
                self.state = 1
            else:
                self.lifes -= 1
                if self.lifes <= 0:
                    self.state = -1
            return self.state
        
        self.check = bnc_check
        
        if restart:
            renpy.call(self.label, mg_obj=self)
    
screen bnc_game_screen(mg_obj, prompt):
    zorder 110

    vbox:
        label _("Tries left: [mg_obj.lifes]")
        label _("Last answer: [mg_obj.last]")
        label _("{color=#00cc00}Bulls: [mg_obj.bulls]{/color}")
        label _("{color=#ffff00}Cows: [mg_obj.cows]{/color}")
        if config.developer:
            yoffset 1
            label _("{i}Right answer: [mg_obj.guessed]{/i}")

    window
    vbox:
        xalign 0.5
        yalign 0.95
        spacing 10

        text prompt xalign 0.5
        input id "bnc_answer" length mg_obj.guessed_len allow "0123456789" xalign 0.5

    vbox:
        style_prefix "choice"
        align (0.01, 0.99)
        spacing 5
        
        textbutton _("Restart (R)") xpadding 0 xsize 200 keysym 'r' action [Hide("bnc_game_screen"), Function(renpy.call, "mg_bnc_s_comment", -1, True, mg_obj=mg_obj)]
        textbutton _("Quit (Q)") xpadding 0 xsize 200 keysym 'q' action [Hide("bnc_game_screen"), Jump("mg_bnc_quit")]
    

    

label mg_bnc(mg_obj=None):
    $ Sayori.setInGame(True)
    $ js_update_rpc(state="Playing Bows and Cows")
    #$justIsSitting = False
    #$show_s_mood(ss1)
    # TODO: LEAVE CONDITION
    #show s gbaabira "did you- just try to close and reopen the game to play bows and cows again >:|"

    if persistent.cooldown is not None:
        if persistent.cooldown >= datetime.datetime.now():
            $ persistent.cooldown = None
        else:
            s gbaaipa "..."
            return
    else:
        pass

        call mg_bnc_s_comment(0, mg_obj=mg_obj) from _call_mg_bnc_s_comment

    

        while mg_obj.state == 0:

            $ prompt = __("Guess the number:")

            $ invalid_answers = 0

            while True:

                call screen bnc_game_screen(mg_obj, prompt)

                $ bnc_answer = _return

                

                if bnc_answer is None:
                    jump mg_bnc_quit
                elif len(bnc_answer) == 0:

                    pass

                elif len(bnc_answer) != mg_obj.guessed_len:

                    $ invalid_answers += 1

                    if invalid_answers < 5:

                        $ prompt = __("Wrong length! Your answer should consist of [mg_obj.guessed_len] different digits.")

                    elif invalid_answers == 5:

                        s "It stops being funny, [player]."

                        $ prompt = __("It stops being funny, [player].")

                    elif invalid_answers == 6:

                        s "Come on, give a valid answer already!"

                        $ prompt = __("Come on, give a valid answer already!")

                    elif invalid_answers == 7:

                        s "Just type as more numbers as you can. This field has the needed max length anyway."

                        $ prompt = __("Just type as more numbers as you can. This field has the needed max length anyway.")

                    elif invalid_answers == 8:

                        s "I'm getting annoyed, [player]."

                        $ prompt = __("I'm getting annoyed, [player].")

                    elif invalid_answers == 9:

                        s "Further error will cost you a try."

                        $ prompt = __("Further error will cost you a try.")

                    elif mg_obj.lifes > 2:

                        $ mg_obj.lifes -= 1

                        s "I warned you."

                        $ prompt = __("I warned you.")

                    elif mg_obj.lifes == 2:

                        $ mg_obj.lifes -= 1

                        $ mr = _("mr.")

                        if gender is True:

                            $ mr = _("mrs.")

                        s "Last chance, [mr] I Can't Count Up To [mg_obj.guessed_len]."

                        $ prompt = __("Last chance, [mr] I Can't Count Up To [mg_obj.guessed_len].")

                    else:

                        $ mg_obj.lifes -= 1

                        hide screen bnc_game_screen

                        call mg_bnc_s_comment(-2, mg_obj=mg_obj) from _call_mg_bnc_s_comment_2

                        jump mg_bnc_after_check # Break the inner loop

                else:

                    jump mg_bnc_after_check # Break the inner loop

    

            label mg_bnc_after_check:

                hide screen bnc_game_screen

                $ mg_obj.check(bnc_answer)

    

        hide screen bnc_game_screen

        call mg_bnc_s_comment(mg_obj.state, mg_obj=mg_obj) from _call_mg_bnc_s_comment_1
    return

label mg_bnc_s_comment(state=-1, restart=False, mg_obj=None):
    hide screen mg_bnc_scr
    if state == 0: # Starting prompt
        s abaaaoa "I propose you a number of [mg_obj.guessed_len] digits..."
        s "Try to guess it."
    elif state == -1: # Game end (restart or out of tries.)
        if restart:
            s bbaaada "Are you giving up?"
        else:
            s abaacia "Your tries are over."
        if mg_obj.bulls + mg_obj.cows == mg_obj.guessed_len: # NO CLUE WHAT THIS IS. FUCK THIS CODE (XD)
            s "You were close to the right answer."
        elif restart:
            s abaadaa "OK, I'll tell you the right answer."
        s abaaloa "The right number was {i}[mg_obj.guessed]{/i}."
        s ebaacqa "Let me think of another number."
        $ mg_obj.prep(mg_obj, restart=True)
    elif state == 1: # Correct answer
        s abaacoa "You're right. It was {i}[mg_obj.guessed]{/i}!"
        s abaaaea "Let's play one more time."
        $ mg_obj.prep(mg_obj, restart=True)
    elif state == -2: # If you try to guess past the amount you're allowed to guess
        s gbaaipa "OK, you win, {i}meanie{/i}!"
        s "I'm really annoyed right now..."
        $ mg_list.remove(mg_obj)
        s gbaabpa "So I don't want to play this game with you anymore."
        s "I won't lose next time."
        $ persistent.cooldown = datetime.datetime.now() + datetime.timedelta(minutes=5)
        return


    
label mg_bnc_quit:
    $ Sayori.setInGame(False)
    hide screen mg_bnc_scr
    $ js_update_rpc(state="In the spaceroom")
    # $ setupRPC("In the spaceroom")
    #$s_mood = 'h'
    #$show_s_mood(ss1)
    return
