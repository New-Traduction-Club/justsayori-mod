default persistent.language = None

screen choose_language():
    default local_lang = _preferences.language
    default chosen_lang = _preferences.language

    modal True
    style_prefix "radio"

    add "gui/overlay/confirm.png"

    frame:
        style "confirm_frame"

        vbox:
            xalign .5
            yalign .5
            xsize 760
            spacing 30

            label _("Please select a language"):
                style "confirm_prompt"
                xalign 0.5

            vbox:
                style_prefix "radio"
                label _("Language")

                # Real languages should go in alphabetical order by English name.
                textbutton "English" text_font "gui/font/Aller_Rg.ttf" action [
                    Language(None),
                    SetField(persistent, "language", "english"),
                    SetScreenVariable("chosen_lang", "english"),
                    Show("dialog", message="It is recommended to restart to apply the changes.", ok_action=Quit())
                ]
                # textbutton "한국어" text_font "gui/font/NotoSansKR-Regular.ttf" action [
                #     Language("ko"),
                #     SetField(persistent, "language", "ko"),
                #     SetScreenVariable("chosen_lang", "ko"),
                #     Show("dialog", message="변경 사항을 적용하려면 게임을 재시작하는 것이 좋습니다.", ok_action=Quit())
                # ]
                # textbutton "中文" text_font "gui/font/NotoSansSC-Regular.ttf" action [
                #     Language("zh_CN"),
                #     SetField(persistent, "language", "zh_CN"),
                #     SetScreenVariable("chosen_lang", "zh_CN"),
                #     Show("dialog", message="변경 사항을 적용하려면 게임을 재시작하는 것이 좋습니다.", ok_action=Quit())
                # ]
                textbutton "Español" text_font "gui/font/Aller_Rg.ttf" action [
                    Language("spanish"),
                    SetField(persistent, "language", "spanish"),
                    SetScreenVariable("chosen_lang", "spanish"),
                    Show("dialog", message="Se recomienda reiniciar el juego\npara aplicar los cambios.", ok_action=Quit())
                ]
                # textbutton "Français" text_font "gui/font/Aller_Rg.ttf" action [
                #     Language("fr"),
                #     SetField(persistent, "language", "fr"),
                #     SetScreenVariable("chosen_lang", "fr"),
                #     Show("dialog", message="Il est recommandé de redémarrer le jeu pour appliquer les changements.", ok_action=Quit())
                # ]
                # textbutton "日本語" text_font "gui/font/NotoSansJP-Regular.ttf" action [
                #     Language("ja"),
                #     SetField(persistent, "language", "ja"),
                #     SetScreenVariable("chosen_lang", "ja"),
                #     Show("dialog", message="変更を適用するにはゲームを再起動することをおすすめします。", ok_action=Quit())
                # ]
                textbutton "Português (BR)" text_font "gui/font/Aller_Rg.ttf" action [
                    Language("ptbr"),
                    SetField(persistent, "language", "ptbr"),
                    SetScreenVariable("chosen_lang", "ptbr"),
                    Show("dialog", message="É recomendado reiniciar o jogo para aplicar as alterações.", ok_action=Quit())
                ]
                # textbutton "Español (MX)" text_font "DejaVuSans.ttf" action [
                #     Language("spanish_mx"),
                #     SetField(persistent, "language", "spanish_mxF"),
                #     SetScreenVariable("chosen_lang", "spanish_mx"),
                #     Show("dialog", message="Se recomienda reiniciar el juego\npara aplicar los cambios.", ok_action=Quit())
                # ]

            hbox:
                xalign 0.5
                spacing 100

                textbutton _("OK") action [
                    Language(None),
                    SetField(persistent, "language", "english"),
                    SetScreenVariable("chosen_lang", "english"),
                    Show("dialog", message="It is recommended to restart to apply the changes.", ok_action=Quit())
                    ] style "ok_button_custom"

style ok_button_custom is button:
    background None
    foreground None
    hover_background None
    hover_foreground None
    insensitive_background None
    insensitive_foreground None

label choose_language:
    call screen choose_language
    return

#######################################
###           Transforms            ###
#######################################

# transform slide_in_from_right(i=0):
#     xoffset 1500
#     alpha 0.0
#     linear 0.5*i xoffset 0 alpha 1.0

# transform slide_in_from_bottom_confirm(i=0):
#     yoffset 200
#     alpha 0.0
#     zoom 1.5
#     linear 0.5*i yoffset 0 alpha 1.0 zoom 1.0