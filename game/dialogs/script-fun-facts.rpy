default persistent._fae_fun_facts_db = dict()
init offset = 5

init -15 python in fae_fun_facts:

    import store

    # fun_fact_db = {}

    def getUnseenFacts():
        
        return [
            fun_fact_label
            for fun_fact_label in store.persistent._fae_fun_facts_db
            if not store.persistent._fae_fun_facts_db[fun_fact_label]['unlocked']
        ]

    def getAllFactsLabels():
        
        return list(store.persistent._fae_fun_facts_db.keys())


# init python:
#     chatReg(
#         Chat(
#             persistent._chat_db,
#             label="s_fun_fact_beginning_fix",
#             prompt="Can you tell me a fun fact?",
#             category=["Misc"],
#             unlocked=True,
#             random=False
#         )
#     )

init python:
    chatReg(
        Chat(
            persistent._chat_db,
            label="s_fun_fact_beginning_test",
            prompt=_("Can you tell me a fun fact?"),
            category=[_('Misc')],
            unlocked=True,
            random=False
        )
    )

label s_fun_fact_beginning_test:
    s abbcaoa "Do you want to hear a fun fact, [player]?"

    python:

        unseen_fact_labels = fae_fun_facts.getUnseenFacts()
        if len(unseen_fact_labels) > 0:
            fact_label_list = unseen_fact_labels
        else:
            fact_label_list = fae_fun_facts.getAllFactsLabels()

        if fact_label_list:
            fun_fact_label = renpy.random.choice(fact_label_list)
            renpy.call(fun_fact_label)

    return


label fae_fun_facts_end:
    s abbccoa "I hope you enjoyed that one!"
    return


init python:
    chatReg(
        Chat(
            persistent._fae_fun_facts_db,
            label="s_fun_fact_arts"
        )
    )

label s_fun_fact_arts:
    s abaaaoa "Some artists add little details referring to different people or universes in their works."
    s "Like in some games and movies, you can find a poster or something that shows other characters. Maybe they're from a past work, or just there to fill in space."
    s abhaaca "We wouldn't know unless it was that obvious or they told us outright."
    s abbbaca "But some of them hide stuff in small things that could refer to a whole other universe, with different details and all."
    s "For example, do you remember {i}Parfait Girls{/i}?"
    s bbbbbaa "You've probably seen people talk about it around the community."
    s "This manga's plot isn't really known, is it?"
    s abaaaoa "Nat tells you a little of what it's about, then that's pretty much it."
    s abbcaoa "But who knows! Maybe it’s alluding to an upcoming game or manga!"

    call fae_fun_facts_end from _call_fae_fun_facts_end
    return

init python:
    chatReg(
        Chat(
            persistent._fae_fun_facts_db,
            label="s_fun_fact_number4"
        )
    )

label s_fun_fact_number4:
    s abhfcaa "Hey [player]! Can you guess what my favorite number is?"
    s abbccoa "It's {i}four{/i}!"
    s abhfaoa "I really like this number, It's a pretty magical one."
    s abhaaca "And I recently noticed that it's weirdly connected to this game too."
    s "You know, {i}4{/i} girls, {i}4{/i} acts."
    if persistent.last_playthrough > 0:
        s bbheboa "...And {i}4{/i} club meetings too..."
    s abbbaca "Maybe it's because it’s an unlucky number in East Asian culture."
    s abbbbca "But that's just superstition, right?"
    s abbbaoa "Ironically for me it was always a lucky number!"
    s abbccoa "Is it your lucky number too? That'd be such a funny coincidence, ehehe~"
    call fae_fun_facts_end from _call_fae_fun_facts_end_1
    return

init python:
    chatReg(
        Chat(
            persistent._fae_fun_facts_db,
            label="s_fun_fact_interpretingWords"
        )
    )
label s_fun_fact_interpretingWords:
    s abaaaoa "Hey [player], do you ever read a word without even noticing it's spelled wrong?"
    s abaacoa "And it always happens with the tiny obvious words!"
    s abbbaoa "{i}So I bet you can't find the mistake in tihs text! {/i}{#Y'see the mistake in 'tihs'} Ehehehe~"
    s abhaaca "So I did some googling and apparently it's because your lazy brain often only reads the letters at the start and the end of common words, without even considering the letters in between."
    s abbcaaa "And that's why we make silly mistakes while writing from time to time."
    s "There’s some funny and not so funny examples of misspellings in the past because someone didn't go back to fix a word or two."
    s abbccaa "But y’know, we’re people. We all make mistakes occasionally."
    s abaaaoa "In the end, no one's perfect."
    call fae_fun_facts_end from _call_fae_fun_facts_end_2
    return

init python:
    chatReg(
        Chat(
            persistent._fae_fun_facts_db,
            label="s_fun_fact_Binary"
        )
    )

label s_fun_fact_Binary:
    s abhaaca "Did you know that you can show numbers much bigger than 5 with just one hand?"
    s "And that’s with the binary system!"
    s "Just look at your fingers, they’re a perfect match for the classic 0/1 pair!"
    s "And it works pretty cleverly too!"
    s "The first number in the unit’s place represents 1, then the next represents 2, and 4, and 8, and so on."
    s "And by adding them up, you can work out the number in decimal form."
    s "Just like a computer would!"
    s "It’s really cool how they compact giant numbers to make calculations easier."
    s "I wish I could’ve done that in math class, ehehehe~"
    s abaaaoa "If you use both hands, you can even calculate numbers up to {i}1023{/i}!"
    call fae_fun_facts_end from _call_fae_fun_facts_end_3
    return

init python:
    chatReg(
        Chat(
            persistent._fae_fun_facts_db,
            label="s_fun_fact_dreams"
        )
    )

label s_fun_fact_dreams:
    s abhfaoa "Hey [player], have you ever woken up from an amazing dream and, no matter how hard you try, you just completely forget it?"
    s abbbaca "Well, I did a little research and found something super interesting!"
    s abbcaoa "Apparently, most people forget 90%% of their dreams within 10 minutes of waking up!"
    s bbhfaca "It's a little sad, don't you think? Sometimes I have really happy dreams and I wish I could remember them forever..."
    s bbfclfc "Especially if they're dreams with you in them, ehehe~"
    s abaaaoa "I guess that's why we should treasure the good moments, whether they're dreams or memories, while they last!"
    call fae_fun_facts_end from _call_fae_fun_facts_end_4
    return