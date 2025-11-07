# init python:

#     chatReg(
#         Chat(
#             persistent._chat_db,
#             label="music_dev",
#             unlocked=True,
#             prompt="music-dev",
#             conditional="",
#             random=True,
#             category=["Music"],
#             affection_range=(fae_affection.HAPPY, None)
#         ),
#         chat_group=CHAT_GROUP_NORMAL
#     )

# label music_dev:
#     s abfcaoa "Hey [player]! Guess what!"
#     s abfccaa "I did some coding and I found a way to let you play your own music here!"
#     s abegabaj "It might be a little buggy, ehehehe~"
#     s abegmoaj "It was my first attempt after all..."
#     s abfccaa "But it seems to be working fine for me!"
#     s abagaoa "All you need to do is put a .mp3 file in the {i}music{/i} folder in the game directory, and click on the {i}Music{/i} tab in the bottom-left!"
#     s abagcka "I'm basically giving you the aux cord to the rest of my existence, so no pressure! Ehehehe~"
#     $ persistent.fae_custom_music_unlocked_redux = True
#     return