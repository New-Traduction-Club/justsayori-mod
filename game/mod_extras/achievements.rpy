





init python:
    import math
    from collections import OrderedDict 

    achievementList = None
    selectedAchievement = None











    class Achievements:
        
        def __init__(self, name, description, image, persistent, count=False, maxCount=100):
            global achievementList
            
            
            self.name = name
            
            
            self.description = description
            
            
            self.image = image
            
            
            
            self.locked = im.MatrixColor(image, im.matrix.desaturate())
            
            
            self.count = count
            
            
            self.persistent = persistent
            
            
            self.maxCount = maxCount
            
            if achievementList is None:
                achievementList = OrderedDict([(self.name, self)])
            else:
                achievementList[self.name] = self



    startup = Achievements("Welcome to DDLC!", "Thanks for accepting the TOS.",
            "gui/logo.png", "persistent.first_run")














screen achievements():
    tag menu

    style_prefix "achievements"

    use game_menu(_("Awards")):

        fixed:


            vbox:
                xpos 0.26
                ypos -0.1

                hbox:

                    if selectedAchievement:

                        python:
                            currentVal = eval(selectedAchievement.persistent)

                            if not currentVal:
                                currentVal = False

                        if selectedAchievement.count:
                            add ConditionSwitch(
                                    currentVal >= selectedAchievement.maxCount, selectedAchievement.image, "True",
                                    selectedAchievement.locked) at achievement_scaler(128)
                        else:
                            add ConditionSwitch(
                                    currentVal, selectedAchievement.image, "True",
                                    selectedAchievement.locked) at achievement_scaler(128)
                    else:
                        null height 128

                    spacing 20

                    vbox:
                        xsize 400
                        ypos 0.2

                        if selectedAchievement:

                            text selectedAchievement.name:
                                font gui.name_font
                                color "#fff"
                                outlines [(2, "#505050", 0, 0)]

                            if selectedAchievement.count:
                                text "[selectedAchievement.description] ([currentVal] / [selectedAchievement.maxCount])"
                            else:
                                text selectedAchievement.description
                        else:
                            null height 128


            vpgrid:
                id "avp"
                rows math.ceil(len(achievementList) / 6.0)
                if len(achievementList) > 6:
                    cols 6
                else:
                    cols len(achievementList)

                spacing 25
                mousewheel True

                xalign 0.5
                yalign 0.85
                ysize 410

                for name, al in achievementList.items():

                    python:
                        currentVal = eval(al.persistent)

                        if not currentVal:
                            currentVal = False

                    if al.count:

                        imagebutton:
                            idle Transform(ConditionSwitch(
                                    currentVal >= al.maxCount, al.image, "True",
                                    al.locked), size=(128,128))
                            action SetVariable("selectedAchievement", al)
                    else:
                        imagebutton:
                            idle Transform(ConditionSwitch(
                                    currentVal, al.image, "True",
                                    al.locked), size=(128,128))
                            action SetVariable("selectedAchievement", al)

            vbar value YScrollValue("avp") xalign 1.01 ypos 0.2 ysize 400

        textbutton "?":
            style "return_button"
            xpos 0.99 ypos 1.1
            action ShowMenu("dialog", "{b}Help{/b}\nGray icons indicate that this achievement is locked.\nContinue your progress in [config.name]\nto unlock all the achievements possible.", ok_action=Hide("dialog"))

        if config.developer:
            textbutton "Test Notif":
                style "return_button"
                xpos 0.8 ypos 1.1
                action ShowMenu("achievement_notify", startup)











screen achievement_notify(reward):

    style_prefix "achievements"

    frame at achievement_notif_transition:
        xsize 300
        ysize 100
        xpos 0.4

        has hbox
        xalign 0.27
        yalign 0.5
        add reward.image at achievement_scaler(50)
        spacing 20
        vbox:
            spacing 5
            text "Achievement Unlocked!" size 16
            text reward.name size 14

    timer 5.0 action [Hide("achievement_notify"), With(Dissolve(1.0))]

style achievements_text is gui_text
style achievements_text:
    color "#000"
    outlines []
    size 20

transform achievement_scaler(x):
    size (x, x)

transform achievement_notif_transition:
    alpha 0.0
    linear 0.5 alpha 1.0

style achievements_image_button:
    hover_sound gui.hover_sound
    activate_sound gui.activate_sound
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
