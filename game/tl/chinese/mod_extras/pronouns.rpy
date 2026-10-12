# TODO: Translation updated at 2025-11-03 13:58

translate chinese pronoun_screen:

    # # game/mod_extras/pronouns.rpy:31
    # old "Enter your first pronoun (He/She/They)"
    # new ""

    # # game/mod_extras/pronouns.rpy:32
    # old "Enter your second pronoun (He's/She's/They're)"
    # new ""

    # # game/mod_extras/pronouns.rpy:33
    # old "Enter your third pronoun (Him/Her/Them)"
    # new ""

    # # game/mod_extras/pronouns.rpy:34
    # old "Enter your fourth pronoun (Is/Are)"
    # new ""

    menu:
        "请选择你的代词称呼："

        "他":
            $ persistent.he = "他"
            $ he = "他"
            $ he_capital = "他"
            $ persistent.hes = "他"
            $ hes = "他"
            $ hes_capital = "他"
            $ persistent.him = "他"
            $ him = "他"
            $ him_capital = "他"
            $ persistent.are = "是"
            $ are = "是"
            $ are_capital = "是"

        "她":
            $ persistent.he = "她"
            $ he = "她"
            $ he_capital = "她"
            $ persistent.hes = "她"
            $ hes = "她"
            $ hes_capital = "她"
            $ persistent.him = "她"
            $ him = "她"
            $ him_capital = "她"
            $ persistent.are = "是"
            $ are = "是"
            $ are_capital = "是"

        "TA（性别中立）":
            $ persistent.he = "TA"
            $ he = "TA"
            $ he_capital = "TA"
            $ persistent.hes = "TA"
            $ hes = "TA"
            $ hes_capital = "TA"
            $ persistent.him = "TA"
            $ him = "TA"
            $ him_capital = "TA"
            $ persistent.are = "是"
            $ are = "是"
            $ are_capital = "是"

    return