init 15 python in fae_quips:

    import store
    import random

    persistent = renpy.game.persistent
    layout = store.layout

    quips = [
        _("What would you like to talk about?"),
        _("What are you thinking of?"),
        _("Is there something you'd like to talk about?"),
        _("Something on your mind?"),
        _("Yes, [player]?"),
    ]



    happy_quips = [
        _("What would you like to talk about?"),
        _("What are you thinking of?"),
        _("Is there something you'd like to talk about?"),
        _("Something on your mind?"),
        _("Up to chat, [player]?"),
        _("Yes, [player]?"),
        _("What's on your mind, [player]?"),
        _("What's up, [player]?"),
        _("Ask away, [player]."),
        _("Don't be shy, [player]."),
    ]



    aff_quips = [
        _("What would you like to talk about?"),
        _("What would you like to talk about, [player]?"),
        _("What are you thinking of?"),
        _("Is there something you'd like to talk about, [player]?"),
        _("Something on your mind?"),
        _("Something on your mind, [player]?"),
        _("Up to chat, [player]?"),
        _("Yes, [player]?"),
        _("What's on your mind, [player]?"),
        _("What's up, [player]?"),
        _("Ask away, [player]."),
        _("Don't be shy, [player]~"),
        _("I'm all ears, [player]~"),
        _("Of course we can talk, [player]."),
    ]



    enamoured_quips = [
        _("What would you like to talk about? <3"),
        _("What would you like to talk about, [player]? <3"),
        _("What are you thinking of?"),
        _("Is there something you'd like to talk about, [player]?"),
        _("Something on your mind?"),
        _("Something on your mind, [player]?"),
        _("Up to chat, I see~"),
        _("Yes, [player]?"),
        _("What's on your mind, [player]?"),
        _("What's up, [player]?"),
        _("Ask away, [player]~"),
        _("I'm all ears, [player]~"),
        _("Of course we can talk, [player]~"),
        _("Take all the time you need, [player]."),
        _("We can talk about whatever you'd like, [player]."),
    ]



    love_quips = [
        _("What would you like to talk about? <3"),
        _("What would you like to talk about, [player]? <3"),
        _("What are you thinking of?"),
        _("Something on your mind?"),
        _("Something on your mind, [player]?"),
        _("Up to chat, I see~"),
        _("Yes, [player]?"),
        _("What's on your mind, [player]?"),
        _("<3"),
        _("What's up, [player]?"),
        _("Ask away, [player]~"),
        _("I'm all ears, [player]~"),
        _("We can talk about whatever you'd like, [player]."),
        _("Of course we can talk, [player]~"),
        _("Take all the time you need, [player]~"),
        _("I'm all yours, [player]~"),
        _("Oh? Something...{w=0.3}{i}important{/i} on your mind, [player]?~"),
    ]



    def get_quip():
        
        affection_status = store.Affection._getAffectionTierName()
        
        if affection_status == "NORMAL":
            return random.choice(quips)
        
        elif affection_status == "HAPPY":
            return random.choice(happy_quips)
        
        elif affection_status == "AFFECTIONATE":
            return random.choice(aff_quips)
        
        elif affection_status == "ENAMORED":
            return random.choice(enamoured_quips)
        
        elif affection_status == "LOVE":
            return random.choice(love_quips)
        
        else:
            return random.choice(quips)
