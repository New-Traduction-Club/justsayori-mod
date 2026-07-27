# NAU Cardgame
# Adapted logic of original MAS NOU Cardgame:
# https://github.com/Monika-After-Story/MonikaModDev/blob/master/Monika%20After%20Story/game/zz_cardgames.rpy

image bg cardgames desk = "mod_assets/games/nau/desks/spaceroom.png"

# transform nau_note_rotate_left:
#     rotate -23
#     rotate_pad True
#     transform_anchor True

# transform nau_pen_rotate_right:
#     rotate 40
#     rotate_pad True
#     transform_anchor True

# style nau_note_text:
#     size 22
#     color "#000"
#     outlines []

init 5 python in js_nau:
    import random
    import store
    from store import (
        persistent,
        config,
        Solid,
        Null,
        Transform,
        Fixed
    )

    ASSETS = "mod_assets/games/nau/"
    winner = None
    player_win_streak = 0
    sayori_win_streak = 0
    in_progress = False
    game = None
    disable_remind_button = False
    disable_yell_button = False
    disable_sfx = False

    def js_get_displayable(d):
        """
        Retrieves a Ren'Py displayable object safely.
        
        IN:
            d - str or Displayable: Asset path or displayable.
        OUT:
            Displayable: Ren'Py displayable.
        """
        if not d:
            return None
        if isinstance(d, renpy.display.core.Displayable):
            return d
        return renpy.easy.displayable(d)

    class _NAUCard(object):
        """
        Represents a card.
        """
        def __init__(self, t, l, c=None):
            """
            Initializes a new card instance.

            IN:
                t - str: Type of card.
                l - str: Label of card.
                c - str: Color of card.
            """
            self.type = t
            self.label = l
            self.color = c

        @property
        def value(self):
            """
            Calculates the point value of the card.

            OUT:
                int: Points value of the card.
            """
            if self.type == "number":
                return int(self.label)
            elif self.type == "action":
                return 20
            return 50

        def __repr__(self):
            """
            Returns a string representation of the card.

            OUT:
                str: String representation.
            """
            if self.color is not None:
                card_info = "'{} {}'".format(self.color.capitalize(), self.label)
            else:
                card_info = "'{}'".format(self.label)
            return "<_NAUCard {}>".format(card_info)

    class _NAUPlayer(object):
        """
        Represents a player.
        """
        def __init__(self, leftie=False):
            """
            Initializes a new player instance.

            IN:
                leftie - bool: Is player left-handed.
            """
            self.leftie = leftie
            self.isAI = False
            self.hand = None
            self.drew_card = False
            self.should_draw_cards = 0
            self.played_card = False
            self.plays_turn = False
            self.should_skip_turn = False
            self.yelled_nou = False
            self.should_play_card = False
            self.nou_reminder_timeout = 0

        def __repr__(self):
            """
            Returns a string representation of the player.

            OUT:
                str: String representation.
            """
            return "<_NAUPlayer '{0}'>".format(persistent.playername)

    class _NAUPlayerAI(_NAUPlayer):
        """
        Sayori AI player.
        """
        MIN_THONK_TIME = 0.2
        MAX_THONK_TIME = 0.8

        def __init__(self, game, leftie=False):
            """
            Initializes a new Sayori AI player instance.

            IN:
                game - NAU: NAU game object.
                leftie - bool: Is AI player left-handed.
            """
            super().__init__(leftie)
            self.isAI = True
            self.game = game
            self.queued_card = None
            self.chosen_color = None
            self.player_cards_data = {
                "reset_in": 0,
                "has_color": None,
                "lacks_colors": []
            }

        def __repr__(self):
            """
            Returns a string representation of the AI player.

            OUT:
                str: String representation.
            """
            return "<_NAUPlayerAI 'Sayori'>"

        def thonk_pause(self):
            """
            Pauses to simulate AI thonking.
            """
            if len(self.hand) == 1:
                t = self.MIN_THONK_TIME
            else:
                t = renpy.random.uniform(self.MIN_THONK_TIME, self.MAX_THONK_TIME)
            renpy.pause(t, hard=True)

        def guess_player_cards(self):
            """
            Guesses cards' colors in the player's hand based on their moves.
            """
            if len(self.game.game_log) < 2:
                return

            if self.player_cards_data["reset_in"] > 0 and self.game.game_log[-2]["played_card"] is not None:
                self.player_cards_data["reset_in"] -= 1

            if (
                (
                    self.game.game_log[-2]["played_card"] is not None
                    and self.game.game_log[-2]["played_card"].type == "wild"
                )
                or (
                    self.game.current_turn == 2
                    and len(self.game.discardpile) > 1
                    and self.game.discardpile[-2].type == "wild"
                )
            ):
                color = self.game.game_log[-2]["played_card"].color
                self.player_cards_data["has_color"] = color
                self.player_cards_data["reset_in"] = 3
                if color in self.player_cards_data["lacks_colors"]:
                    self.player_cards_data["lacks_colors"].remove(color)

            if (
                self.game.game_log[-2]["played_card"] is not None
                and self.game.game_log[-2]["played_card"].type == "wild"
                and len(self.game.discardpile) > 1
            ):
                if self.game.discardpile[-2].color not in self.player_cards_data["lacks_colors"]:
                    self.player_cards_data["lacks_colors"].append(self.game.discardpile[-2].color)

                if self.player_cards_data["has_color"] in self.player_cards_data["lacks_colors"]:
                    self.player_cards_data["has_color"] = None

            elif (
                self.game.game_log[-2]["drew_card"]
                and not self.game.game_log[-2]["had_skip_turn"]
            ):
                if not self.game.game_log[-2]["played_card"]:
                    self.player_cards_data["lacks_colors"] = [self.game.discardpile[-1].color]
                elif self.game.discardpile[-2].color not in self.player_cards_data["lacks_colors"]:
                    self.player_cards_data["lacks_colors"].append(self.game.discardpile[-2].color)

                if self.player_cards_data["has_color"] in self.player_cards_data["lacks_colors"]:
                    self.player_cards_data["has_color"] = None

            if len(self.player_cards_data["lacks_colors"]) == 3:
                missing_colors = self.player_cards_data["lacks_colors"]
                all_colors = frozenset(self.game.COLORS)
                self.player_cards_data["has_color"] = next(iter(all_colors.difference(missing_colors)))
                self.player_cards_data["reset_in"] = 3

            if self.game.game_log[-2]["drew_card"] and self.game.game_log[-2]["had_draw_cards"]:
                self.player_cards_data["lacks_colors"] = []

            if self.player_cards_data["reset_in"] == 0:
                self.player_cards_data["has_color"] = None

        def _get_cards_data(self, cards=None):
            """
            Compiles a dictionary of data about the AI player's cards.

            IN:
                cards - list of _NAUCard: Optional cards list to analyze.

            OUT:
                dict: Structured data of AI cards.
            """
            if cards is None:
                cards = [card for card in self.hand]

            new_cards_data = {
                "num_red": {"amount": 0, "value": 0, "ids": []},
                "num_blue": {"amount": 0, "value": 0, "ids": []},
                "num_green": {"amount": 0, "value": 0, "ids": []},
                "num_yellow": {"amount": 0, "value": 0, "ids": []},
                "act_red": {"amount": 0, "value": 0, "ids": []},
                "act_blue": {"amount": 0, "value": 0, "ids": []},
                "act_green": {"amount": 0, "value": 0, "ids": []},
                "act_yellow": {"amount": 0, "value": 0, "ids": []},
                "wcc": {"amount": 0, "ids": []},
                "wd4": {"amount": 0, "ids": []}
            }

            for id, card in enumerate(cards):
                if card.type == "number":
                    key = "num_" + card.color
                    new_cards_data[key]["amount"] += 1
                    new_cards_data[key]["value"] += card.value
                    new_cards_data[key]["ids"].append(id)
                elif card.type == "action":
                    key = "act_" + card.color
                    new_cards_data[key]["amount"] += 1
                    new_cards_data[key]["value"] += card.value
                    new_cards_data[key]["ids"].append(id)
                else:
                    key = "wcc" if card.label == "Wild" else "wd4"
                    new_cards_data[key]["amount"] += 1
                    new_cards_data[key]["ids"].append(id)

            for key in new_cards_data:
                if "ids" in new_cards_data[key] and "value" in new_cards_data[key]:
                    new_cards_data[key]["ids"].sort(key=lambda idx: cards[idx].value, reverse=True)

            return new_cards_data

        def _sort_cards_data(self, cards_data, consider_player_cards_data=True):
            """
            Sorts the card categories based on amount, values, and player guesses.

            IN:
                cards_data - dict: The cards data dictionary.
                consider_player_cards_data - bool: True to consider guessed player colors.

            OUT:
                list of tuples: Sorted card categories.
            """
            def sortKey(item):
                if not item[0].startswith("num_"):
                    return (0, 0, 0, 0)

                color = item[0].replace("num_", "")
                amount = item[1]["amount"]
                value = item[1]["value"]

                lacks_color_bonus = 0
                has_color_penalty = 0

                if consider_player_cards_data:
                    if color in self.player_cards_data["lacks_colors"]:
                        lacks_color_bonus = 1
                    if self.player_cards_data["has_color"] == color:
                        has_color_penalty = -1

                return (amount, value, lacks_color_bonus, has_color_penalty)

            color_keys = ["num_red", "num_blue", "num_green", "num_yellow"]
            sorted_list = sorted(
                [(k, cards_data[k]) for k in color_keys],
                key=sortKey,
                reverse=True
            )
            return sorted_list

        def choose_card(self):
            """
            Sayori chooses a card to play based on her current hand and game state.
            
            OUT:
                _NAUCard or None: The card to play, or None if drawing is needed.
            """
            def analyse_numbers():
                highest_value = float(sorted_cards_data[0][1]["amount"])
                reserved_card = None

                for color_id in range(4):
                    if sorted_cards_data[color_id][1]["amount"] > 2:
                        last_card = self.hand[sorted_cards_data[color_id][1]["ids"][-1]]
                        if (
                            last_card.label == "0"
                            and (
                                last_card.color in self.player_cards_data["lacks_colors"]
                                or (
                                    total_player_cards > 2
                                    and (
                                        (
                                            self.player_cards_data["has_color"] is not None
                                            and last_card.color != self.player_cards_data["has_color"]
                                        )
                                        or (
                                            self.player_cards_data["has_color"] is None
                                            and random.random() < 0.3
                                        )
                                    )
                                )
                            )
                        ):
                            if self.game._is_matching_card(self, last_card):
                                return last_card

                    this_color = sorted_cards_data[color_id][0].replace("num_", "")
                    next_color_id = color_id + 1
                    if next_color_id < 4:
                        next_color_value = float(sorted_cards_data[next_color_id][1]["amount"])
                    else:
                        next_color_value = None

                    want_try_another_color = (
                        this_color == self.player_cards_data["has_color"]
                        and next_color_value is not None
                        and (
                            highest_value == 0
                            or (highest_value - next_color_value) / highest_value < 0.5
                            or total_player_cards < 4
                        )
                        and (
                            this_color != self.game.discardpile[-1].color
                            or random.random() < 0.2
                        )
                    )

                    for id in sorted_cards_data[color_id][1]["ids"]:
                        card = self.hand[id]
                        if self.game._is_matching_card(self, card):
                            if want_try_another_color and reserved_card is None:
                                reserved_card = card
                                break
                            else:
                                return card

                if reserved_card is not None and (total_cards < 4 or random.random() < 0.25):
                    return reserved_card
                return None

            def analyse_actions():
                def sortKey(id):
                    label_order = ("Skip", "Draw Two", "Reverse")
                    sorted_colors = [sorted_cards_data[i][0].replace("num_", "") for i in range(4)]
                    return [self.hand[id].label == label for label in label_order] + [self.hand[id].color == color for color in sorted_colors]

                action_cards_ids = []
                for color in self.game.COLORS:
                    action_cards_ids += cards_data["act_" + color]["ids"]

                action_cards_ids.sort(key=sortKey, reverse=True)
                for id in action_cards_ids:
                    card = self.hand[id]
                    if self.game._is_matching_card(self, card):
                        return card
                return None

            def analyse_wilds(label=None):
                if not label:
                    wild_cards_ids = cards_data["wd4"]["ids"] + cards_data["wcc"]["ids"]
                else:
                    wild_cards_ids = cards_data[label]["ids"]

                if not wild_cards_ids:
                    return None

                card = self.hand[renpy.random.choice(wild_cards_ids)]
                if self.game._is_matching_card(self, card):
                    return card
                return None

            def analyse_cards(func_list):
                for func, args, kwargs in func_list:
                    card = func(*args, **kwargs)
                    if card is not None:
                        return card
                return None

            cards_data = self._get_cards_data()
            total_cards = len(self.hand)
            total_player_cards = len(self.game.player.hand)

            if self.queued_card is not None and self.game._is_matching_card(self, self.queued_card):
                return self.queued_card

            if total_cards == 1:
                card = self.hand[0]
                if self.game._is_matching_card(self, card):
                    return card
                return None

            sorted_cards_data = self._sort_cards_data(cards_data)

            if (
                total_player_cards < 4
                or total_cards / total_player_cards > 1.05
                or random.random() < 0.2
            ):
                analysis = (
                    (analyse_wilds, (), {"label": "wd4"}),
                    (analyse_actions, (), {}),
                    (analyse_numbers, (), {}),
                    (analyse_wilds, (), {"label": "wcc"})
                )
            else:
                analysis = (
                    (analyse_numbers, (), {}),
                    (analyse_actions, (), {}),
                    (analyse_wilds, (), {})
                )

            return analyse_cards(analysis)

        def _randomise_color(self):
            """
            Chooses one of the colors at random, prioritizing colors the player lacks.
            """
            if self.player_cards_data["lacks_colors"]:
                return renpy.random.choice(self.player_cards_data["lacks_colors"])
            colors = list(self.game.COLORS)
            if self.player_cards_data["has_color"] is not None and self.player_cards_data["has_color"] in colors:
                colors.remove(self.player_cards_data["has_color"])
            return renpy.random.choice(colors)

        def choose_color(self, ignored_card=None):
            """
            Chooses color based on AI hand and game situation.
            
            IN:
                ignored_card - _NAUCard: Optional card to ignore in calculation.

            OUT:
                str: Chosen color.
            """
            def sortKey(id):
                labels = (
                    "Skip",
                    "Draw Two",
                    "Reverse"
                )
                sorted_colors = [sorted_cards_data[i][0].replace("num_", "") for i in range(4)]
                return [cards[id].label == label for label in labels] + [cards[id].color == color for color in sorted_colors]

            cards = [card for card in self.hand]
            if ignored_card is not None and ignored_card in cards:
                cards.remove(ignored_card)

            cards_data = self._get_cards_data(cards)

            if len(cards) == 1:
                if cards[0].type == "wild":
                    return self._randomise_color()
                else:
                    return cards[0].color

            sorted_cards_data = self._sort_cards_data(cards_data, consider_player_cards_data=False)

            if len(self.game.player.hand) < 3:
                action_ids = []
                for color in self.game.COLORS:
                    action_ids += cards_data["act_" + color]["ids"]

                if action_ids:
                    action_ids.sort(key=sortKey, reverse=True)
                    self.queued_card = cards[action_ids[0]]
                    return self.queued_card.color

            highest_value = float(sorted_cards_data[0][1]["amount"])
            if highest_value > 0:
                for j in range(4):
                    if float(highest_value - sorted_cards_data[j][1]["amount"]) / highest_value >= 0.6:
                        break

                    if sorted_cards_data[j][1]["amount"] > 0:
                        data_key = sorted_cards_data[j][0].replace("num_", "act_")
                        if cards_data[data_key]["amount"] > 0:
                            sortByLabel = lambda card: (
                                card.label == "Skip",
                                card.label == "Draw Two",
                                card.label == "Reverse"
                            )
                            self.queued_card = sorted(
                                [cards[id] for id in cards_data[data_key]["ids"]],
                                key=sortByLabel,
                                reverse=True
                            )[0]
                            return self.queued_card.color

            color_counts = {}
            for col in self.game.COLORS:
                color_counts[col] = cards_data["num_" + col]["amount"] + cards_data["act_" + col]["amount"]
            sorted_colors = sorted(self.game.COLORS, key=lambda col: color_counts[col], reverse=True)
            if color_counts[sorted_colors[0]] > 0:
                return sorted_colors[0]
            
            return self._randomise_color()

        def play_card(self, card):
            """
            AI plays a card.
            
            IN:
                card - _NAUCard: Card to play.
            """
            if card is None:
                if self.should_draw_cards:
                    self.game.deal_cards(self, self.should_draw_cards)
                else:
                    self.game.deal_cards(self)
                    new_card = self.hand[-1]
                    if self.game._is_matching_card(self, new_card):
                        if new_card.type == "wild":
                            self.chosen_color = self.choose_color(ignored_card=new_card)
                            new_card.color = self.chosen_color
                            self.game.play_card(self, self.game.player, new_card)
                            self.game._say_quip("Dlg when Sayori plays a wild card choosing " + self.chosen_color + ".", new_context=True)
                        else:
                            self.game.play_card(self, self.game.player, new_card)
                self.game.end_turn(self, self.game.player)
                return

            if card is self.queued_card:
                self.queued_card = None

            if card.type == "wild":
                self.chosen_color = self.choose_color(ignored_card=card)
                card.color = self.chosen_color
                self.game.play_card(self, self.game.player, card)
                self.game._say_quip("Dlg when Sayori plays a wild card choosing " + self.chosen_color + ".", new_context=True)
                self.game.end_turn(self, self.game.player)
            else:
                self.game.play_card(self, self.game.player, card)
                self.game.end_turn(self, self.game.player)

            self.game._win_check(self)

    class _NAUReaction(object):
        """
        Reactions data structure.
        """
        def __init__(self, type_=0, turn=-1, sayori_card=None, player_card=None, tier=0, shown=False):
            """
            Initializes a new NAU reaction instance.

            IN:
                type_ - int: The type of reaction.
                turn - int: The turn number when this reaction was triggered.
                sayori_card - _NAUCard: The card Sayori played.
                player_card - _NAUCard: The card the player played.
                tier - int: The tier of reaction (0-2).
                shown - bool: Whether this reaction has been displayed.
            """
            self.type = type_
            self.turn = turn
            self.sayori_card = sayori_card
            self.player_card = player_card
            self.tier = tier
            self.shown = shown

        @property
        def tier(self):
            """
            Gets the reaction tier.

            OUT:
                int: Reaction tier value (0-2).
            """
            return self._tier

        @tier.setter
        def tier(self, value):
            """
            Sets the reaction tier, clamped between 0 and 2.

            IN:
                value - int: The reaction tier value.
            """
            self._tier = max(min(value, 2), 0)

        def __getitem__(self, key):
            """
            Allows indexing attributes of the reaction object.

            IN:
                key - str: The attribute name.

            OUT:
                any: The attribute value.
            """
            return getattr(self, key)

        def __setitem__(self, key, value):
            """
            Allows setting attributes of the reaction object via indexing.

            IN:
                key - str: The attribute name.
                value - any: The new value for the attribute.
            """
            setattr(self, key, value)

    class CardEvent(object):
        """
        Represents cards events.
        """
        def __init__(self):
            """
            Initializes a new CardEvent instance with default None/0 values.
            """
            self.type = None
            self.stack = None
            self.card = None
            self.drag_cards = None
            self.drop_stack = None
            self.drop_card = None
            self.time = 0

    class Table(renpy.display.core.Displayable):
        """
        Table for card rendering.
        """
        def __init__(self, back=None, base=None, springback=0.3, rotate=0.15, doubleclick=0.33, **kwargs):
            """
            Initializes the card table displayable.

            IN:
                back - str or Displayable: The displayable to use for the card back.
                base - str or Displayable: The displayable to use for the stack base.
                springback - float: The springback transition duration in seconds.
                rotate - float: The maximum rotation angle multiplier.
                doubleclick - float: The double click threshold in seconds.
                **kwargs: Additional keyword arguments for the parent Displayable class.
            """
            super().__init__(**kwargs)
            self.back = js_get_displayable(back)
            self.base = js_get_displayable(base)
            self.springback = springback
            self.rotate = rotate
            self.doubleclick = doubleclick
            self.cards = {}
            self.stacks = []
            self.sensitive = True
            self.last_event = CardEvent()
            self.click_card = None
            self.click_stack = None
            self.drag_cards = []
            self.dragging = False
            self.click_x = 0
            self.click_y = 0
            self.st = 0

        def show(self, layer="master"):
            """
            Displays the table on the specified screen layer.

            IN:
                layer - str: The screen layer on which to show the table.
            """
            for v in self.cards.values():
                v._offset = __Fixed(0, 0)
            ui.layer(layer)
            ui.implicit_add(self)
            ui.close()

        def hide(self, layer="master"):
            """
            Hides the table from the specified screen layer.

            IN:
                layer - str: The screen layer from which to remove the table.
            """
            ui.layer(layer)
            ui.remove(self)
            ui.close()

        def set_sensitive(self, value):
            """
            Sets the interaction sensitivity of the table.

            IN:
                value - bool: True to enable interactions, False to disable.
            """
            self.sensitive = value

        def get_card(self, value):
            """
            Retrieves the internal __Card instance corresponding to the given value key.

            IN:
                value - any: The card identifier value.

            OUT:
                __Card: The internal card displayable helper instance.
            """
            if value not in self.cards:
                raise Exception("No card has the value {0!r}.".format(value))
            return self.cards[value]

        def set_faceup(self, card, faceup=True):
            """
            Sets whether a card should be face up or face down with animation.

            IN:
                card - any: The card identifier value.
                faceup - bool: True for face up, False for face down.
            """
            card_obj = self.get_card(card)
            if card_obj.faceup != faceup:
                __Flip(card_obj, faceup)
            renpy.redraw(self, 0)

        def get_faceup(self, card):
            """
            Checks whether a specific card is currently face up.

            IN:
                card - any: The card identifier value.

            OUT:
                bool: True if face up, False otherwise.
            """
            return self.get_card(card).faceup

        def set_rotate(self, card, rotation):
            """
            Applies a rotation animation/state to a card.

            IN:
                card - any: The card identifier value.
                rotation - float: The target rotation angle in degrees.
            """
            __Rotate(self.get_card(card), rotation)
            renpy.redraw(self, 0)

        def get_rotate(self, card):
            """
            Retrieves the current rotation angle of a card.

            IN:
                card - any: The card identifier value.

            OUT:
                float: The rotation angle in degrees.
            """
            return self.get_card(card).rotate.rotate_limit()

        def card(self, value, face, back=None):
            """
            Registers a new card on the table.

            IN:
                value - any: The card identifier value.
                face - str or Displayable: The displayable to use for the card face.
                back - str or Displayable: Optional displayable for the card back override.
            """
            self.cards[value] = __Card(self, value, face, back)

        def stack(self, x, y, xoff=0, yoff=0, show=1024, base=None, click=False, drag=0, drop=False, hover=False, hidden=False):
            """
            Creates and registers a card stack on the table.

            IN:
                x - int: The horizontal screen position of the stack.
                y - int: The vertical screen position of the stack.
                xoff - int: The horizontal offset between stacked cards.
                yoff - int: The vertical offset between stacked cards.
                show - int: The maximum number of cards to display in the stack.
                base - str or Displayable: Optional displayable for the stack base override.
                click - bool: Whether cards in this stack can be clicked.
                drag - int: The drag mode (0=none, 1=drag single card, 4=drag top card).
                drop - bool: Whether cards can be dropped onto this stack.
                hover - bool: Whether hovering over cards in this stack is interactive.
                hidden - bool: Whether the stack is hidden from rendering.

            OUT:
                __Stack: The newly created stack object.
            """
            rv = __Stack(self, x, y, xoff, yoff, show, base, click, drag, drop, hover, hidden)
            self.stacks.append(rv)
            return rv

        def per_interact(self):
            """
            Called at the start of each interaction to request a redraw.
            """
            renpy.redraw(self, 0)

        def render(self, width, height, st, at):
            """
            Renders the table and all its stacks/cards to the screen.

            IN:
                width - int: Available rendering width.
                height - int: Available rendering height.
                st - float: Time since the displayable was first shown.
                at - float: Time since the displayable was first shown (animation time).

            OUT:
                Render: The Ren'Py Render object.
            """
            self.st = st
            rv = renpy.Render(width, height)
            deferred_render = []
            for s in self.stacks:
                if s.hidden:
                    s.rect = None
                    for c in s.cards:
                        c.rect = None
                    continue
                s.render_to(rv, width, height, st, at)
                for c in s.cards:
                    if c.hovered or c in self.drag_cards:
                        deferred_render.append(c)
                    else:
                        c.render_to(rv, width, height, st, at)
            for c in deferred_render:
                c.render_to(rv, width, height, st, at)
            return rv

        def visit(self):
            """
            Returns a list of nested displayable objects that Ren'Py needs to visit.

            OUT:
                list of Displayable: The child displayables.
            """
            stacks_bases = [stack.base for stack in self.stacks]
            cards_faces = [card.face for card in self.cards.values()]
            cards_backs = [card.back for card in self.cards.values()]
            return [x for x in (stacks_bases + cards_faces + cards_backs) if x is not None]

        def event(self, ev, x, y, st):
            """
            Handles input and mouse/drag events on the table.

            IN:
                ev - Event: The event object from pygame.
                x - int: Mouse horizontal position.
                y - int: Mouse vertical position.
                st - float: Time since the displayable was first shown.

            OUT:
                list of CardEvent or None: A list of triggered card events, or None.
            """
            self.st = st
            if not self.sensitive:
                return
            evt_list = list()
            grabbed = renpy.display.focus.get_grab()
            if (grabbed is not None) and (grabbed is not self):
                return
            
            import pygame
            if (
                ev.type == pygame.MOUSEMOTION
                or (
                    ev.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP)
                    and ev.button == 1
                )
            ):
                if not self.drag_cards:
                    for s in self.stacks:
                        if s.hidden or not s.hover:
                            continue
                        for i, c in enumerate(s.cards):
                            if c.rect is None:
                                continue
                            c_w, c_h = 150, 214
                            c_x_min = s.x + s.xoff * i - c_w // 2
                            c_y_min = s.y + s.yoff * i - c_h // 2
                            c_x_max = 0
                            c_y_max = 0
                            if i == len(s.cards) - 1:
                                c_x_max = c_x_min + c_w
                                c_y_max = c_y_min + c_h
                            elif not s.xoff == 0 or not s.yoff == 0:
                                if abs(s.xoff) >= c_w:
                                    c_x_max = c_x_min + c_w
                                else:
                                    if s.xoff > 0:
                                        c_x_max = c_x_min + s.xoff
                                    elif s.xoff < 0:
                                        c_x_max = c_x_min + c_w
                                        c_x_min = c_x_min + c_w + s.xoff
                                    else:
                                        c_x_max = c_x_min + c_w
                                if abs(s.yoff) >= c_h:
                                    c_y_max = c_y_min + c_h
                                else:
                                    if s.yoff > 0:
                                        c_y_max = c_y_min + s.yoff
                                    elif s.yoff < 0:
                                        c_y_max = c_y_min + c_h + s.yoff
                                        c_y_min = c_y_min + s.yoff
                                    else:
                                        c_y_max = c_y_min + c_h

                            if not c.hovered and c_x_min <= x < c_x_max and c_y_min <= y < c_y_max:
                                evt = CardEvent()
                                evt.type = "hover"
                                evt.table = self
                                evt.stack = s
                                evt.card = c.value
                                evt.time = st
                                c.hovered = True
                                evt_list.insert(0, evt)
                                renpy.redraw(self, 0)
                            elif c.hovered and (not c_x_min <= x < c_x_max or not c_y_min <= y < c_y_max):
                                evt = CardEvent()
                                evt.type = "unhover"
                                evt.table = self
                                evt.stack = s
                                evt.card = c.value
                                evt.time = st
                                c.hovered = False
                                evt_list.insert(0, evt)
                                renpy.redraw(self, 0)

            import pygame
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                self.click_x = x
                self.click_y = y
                self.click_card = None
                self.click_stack = None
                
                for s in self.stacks:
                    if s.hidden:
                        continue
                    for c in reversed(s.cards):
                        if c.rect is not None:
                            cx, cy, cw, ch = c.rect
                            if cx <= x < cx + cw and cy <= y < cy + ch:
                                self.click_card = c
                                self.click_stack = s
                                break
                    if self.click_stack is not None:
                        break
                    if s.rect is not None:
                        sx, sy, sw, sh = s.rect
                        if sx <= x < sx + sw and sy <= y < sy + sh:
                            self.click_stack = s
                            
                if self.click_stack is not None:
                    renpy.display.focus.set_grab(self)
                    if self.click_card is not None and self.click_stack.drag == 1:
                        self.dragging = True
                        self.drag_cards = [self.click_card]
                    elif self.click_stack.drag == 4:
                        if self.click_stack.cards:
                            self.dragging = True
                            self.drag_cards = [self.click_stack.cards[-1]]
                            
            elif ev.type == pygame.MOUSEMOTION or (ev.type == pygame.MOUSEBUTTONUP and ev.button == 1):
                if self.dragging:
                    dx = x - self.click_x
                    dy = y - self.click_y
                    for c in self.drag_cards:
                        c.set_offset(dx, dy)
                    renpy.redraw(self, 0)
                    
            if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                renpy.display.focus.set_grab(None)
                evt = None
                if self.dragging:
                    if self.drag_cards:
                        for c in self.drag_cards:
                            if c.hovered:
                                evt = CardEvent()
                                evt.type = "unhover"
                                evt.table = self
                                evt.stack = self.click_stack
                                evt.card = c.value
                                evt.time = st
                                c.hovered = False
                                evt_list.append(evt)
                        
                        drop_stack = None
                        for s in self.stacks:
                            if s.hidden or not s.drop:
                                continue
                            if s.rect is not None:
                                sx, sy, sw, sh = s.rect
                                if sx <= x < sx + sw and sy <= y < sy + sh:
                                    drop_stack = s
                                    break
                                    
                        if drop_stack is not None:
                            evt = CardEvent()
                            evt.type = "drag"
                            evt.table = self
                            evt.stack = self.click_stack
                            evt.card = self.drag_cards[0].value
                            evt.drag_cards = [c.value for c in self.drag_cards]
                            evt.drop_stack = drop_stack
                            evt.drop_card = drop_stack.cards[-1].value if drop_stack.cards else None
                            evt.time = st
                            evt_list.append(evt)
                        for c in self.drag_cards:
                            c.springback()
                    self.dragging = False
                    self.drag_cards = []
                    renpy.redraw(self, 0)
                else:
                    if self.click_stack is not None:
                        click_time = st - self.last_event.time
                        is_double = (self.last_event.type in ("click", "doubleclick") and
                                    self.last_event.stack is self.click_stack and
                                    self.last_event.card == (self.click_card.value if self.click_card else None) and
                                    click_time < self.doubleclick)
                        evt = CardEvent()
                        evt.type = "doubleclick" if is_double else "click"
                        evt.table = self
                        evt.stack = self.click_stack
                        evt.card = self.click_card.value if self.click_card else None
                        evt.time = st
                        evt_list.append(evt)
                        self.last_event = evt
            
            if evt_list:
                return evt_list

    class __Card(object):
        """
        Internal representation of a single card displayable.
        """
        def __init__(self, table, value, face, back):
            """
            Initializes the __Card helper.

            IN:
                table - Table: The parent Table instance.
                value - any: Unique identifier/value of the card.
                face - str or Displayable: Displayable for the card front.
                back - str or Displayable: Displayable for the card back.
            """
            self.table = table
            self.value = value
            self.face = js_get_displayable(face)
            self.back = js_get_displayable(back) if back else self.table.back
            if not self.back:
                raise Exception("No back defined for card.")
            self.faceup = True
            self.rotate = None
            self.markers = []
            self.stack = None
            self._offset = __Fixed(0, 0)
            self.rect = None
            self.hovered = False
            self.positional_offset = (0, 0)
            self.flip_anim = None
            __Rotate(self, 0)

        def set_offset(self, x=0, y=0):
            """
            Sets the positional offset for rendering.

            IN:
                x - int: Horizontal offset.
                y - int: Vertical offset.
            """
            self.positional_offset = (x, y)

        def place(self):
            """
            Calculates the current coordinate placement of the card on the table.

            OUT:
                tuple: (x, y) target rendering position coordinates.
            """
            s = self.stack
            offset = max(len(s.cards) - s.show, 0)
            index = max(s.cards.index(self) - offset, 0)
            x_pos_off, y_pos_off = self.positional_offset
            return (x_pos_off + s.x + s.xoff * index, y_pos_off + s.y + s.yoff * index)

        def springback(self):
            """
            Triggers the springback animation from current drag position back to stack position.
            """
            if self.rect is None:
                self._offset = __Fixed(0, 0)
            else:
                self._offset = __Springback(self)

        def render_to(self, rv, width, height, st, at):
            """
            Blits/renders the card displayable onto the parent render object.

            IN:
                rv - Render: The parent Ren'Py Render surface.
                width - int: Available width.
                height - int: Available height.
                st - float: State time.
                at - float: Animation time.
            """
            x, y = self.place()
            xoffset, yoffset = self._offset.offset()
            x += xoffset
            y += yoffset

            if self.flip_anim:
                xzoom, d = self.flip_anim.get_render_info(st)
            else:
                xzoom = 1.0
                d = self.face if self.faceup else self.back

            if self.markers:
                d = Fixed(* ([d] + [renpy.easy.displayable(i) for i in self.markers]))

            is_hover_scaled = self.stack.hover and self.hovered
            zoom_factor = 1.05 if is_hover_scaled else 1.0

            r = self.rotate.rotate()
            if r or xzoom != 1.0 or zoom_factor != 1.0:
                d = Transform(d, rotate=r, xzoom=xzoom * zoom_factor, yzoom=zoom_factor)

            render = renpy.render(d, width, height, st, at)
            w, h = render.get_size()
            x -= w // 2
            y -= h // 2
            self.rect = (x, y, w, h)
            rv.blit(render, (x, y))

        def __repr__(self):
            """
            Returns string representation of the card helper.

            OUT:
                str: String representation.
            """
            return "<__Card {0!r}>".format(self.value)

    class __Springback(object):
        """
        Transition handler to animate a card back to its stack position.
        """
        def __init__(self, card):
            """
            Initializes the __Springback helper.

            IN:
                card - __Card: The card to animate.
            """
            self.card = card
            self.table = card.table
            self.start = self.table.st
            cx, cy, cw, ch = self.card.rect
            self.startx = cx + cw // 2
            self.starty = cy + ch // 2

        def offset(self):
            """
            Calculates the current offset during springback animation.

            OUT:
                tuple: (x, y) offset coordinates.
            """
            t = (self.table.st - self.start) / self.table.springback
            t = min(t, 1.0)
            t_eased = t * (2.0 - t)
            if t < 1.0:
                renpy.redraw(self.table, 0)
            px, py = self.card.place()
            return int((self.startx - px) * (1.0 - t_eased)), int((self.starty - py) * (1.0 - t_eased))

    class __Fixed(object):
        """
        Constant offset wrapper for static card positioning.
        """
        def __init__(self, x, y):
            """
            Initializes the static offset wrapper.

            IN:
                x - int: Static horizontal offset.
                y - int: Static vertical offset.
            """
            self.x = x
            self.y = y

        def offset(self):
            """
            Retrieves the static offset.

            OUT:
                tuple: (x, y) offset coordinates.
            """
            return self.x, self.y

    class __Rotate(object):
        """
        Handles card rotation calculations and limits.
        """
        def __init__(self, card, amount):
            """
            Initializes the __Rotate helper.

            IN:
                card - __Card: The card to rotate.
                amount - float: Starting rotation angle in degrees.
            """
            self.card = card
            self.table = card.table
            self.start = self.table.st
            if card.rotate is None:
                self.start_rotate = amount
            else:
                self.start_rotate = card.rotate.rotate()
            self.end_rotate = amount
            card.rotate = self

        def rotate(self):
            """
            Gets the current rotation angle.

            OUT:
                float: The rotation angle in degrees.
            """
            if self.start_rotate == self.end_rotate:
                return self.start_rotate
            t = (self.table.st - self.start) / self.table.springback
            t = min(t, 1.0)
            t_eased = t * (2.0 - t)
            if t < 1.0:
                renpy.redraw(self.table, 0)
            return self.start_rotate + (self.end_rotate - self.start_rotate) * t_eased

        def rotate_limit(self):
            """
            Gets the card's rotation limit.

            OUT:
                float: The rotation angle.
            """
            return self.end_rotate

    class __Flip(object):
        """
        Handles the 3D-like flip transition of a card (between face up/down).
        """
        def __init__(self, card, faceup, duration=0.25):
            """
            Initializes the __Flip animation helper.

            IN:
                card - __Card: The card to flip.
                faceup - bool: Target face state (True = face up, False = face down).
                duration - float: Transition duration in seconds.
            """
            self.card = card
            self.table = card.table
            self.start = self.table.st
            self.start_faceup = card.faceup
            self.target_faceup = faceup
            self.duration = duration
            card.flip_anim = self

        def get_render_info(self, st):
            """
            Calculates rendering zoom factor and face texture at a specific time step during flipping.

            IN:
                st - float: Current state time.

            OUT:
                tuple: (xzoom, displayable) horizontal scale factor and current texture.
            """
            t = (st - self.start) / self.duration
            t = min(t, 1.0)
            if t < 1.0:
                renpy.redraw(self.table, 0)
            else:
                self.card.faceup = self.target_faceup
                self.card.flip_anim = None
                return 1.0, (self.card.face if self.target_faceup else self.card.back)
            if t < 0.5:
                t_inner = t * 2.0
                t_eased = t_inner * (2.0 - t_inner)
                xzoom = 1.0 - t_eased
                d = self.card.face if self.start_faceup else self.card.back
            else:
                t_inner = (t - 0.5) * 2.0
                t_eased = t_inner * (2.0 - t_inner)
                xzoom = t_eased
                d = self.card.face if self.target_faceup else self.card.back
            return xzoom, d

    class __Stack(object):
        """
        Represents a stack of cards on the table.
        """
        def __init__(self, table, x, y, xoff, yoff, show, base, click, drag, drop, hover, hidden):
            """
            Initializes a card stack instance.

            IN:
                table - Table: The parent Table instance.
                x - int: Horizontal position.
                y - int: Vertical position.
                xoff - int: Horizontal offset between cards.
                yoff - int: Vertical offset between cards.
                show - int: Maximum number of cards to display.
                base - Displayable: The base/background displayable for the stack.
                click - bool: Whether cards in stack are clickable.
                drag - int: The drag mode.
                drop - bool: Whether cards can be dropped.
                hover - bool: Whether cards are hoverable.
                hidden - bool: Whether stack is hidden from rendering.
            """
            self.table = table
            self.x = x
            self.y = y
            self.xoff = xoff
            self.yoff = yoff
            self.show = show
            self.base = js_get_displayable(base) if base else self.table.base
            self.click = click
            self.drag = drag
            self.drop = drop
            self.hover = hover
            self.hidden = hidden
            self.cards = []
            self.rect = None

        def insert(self, index, card, animate=True):
            """
            Inserts a card into the stack at a given index.

            IN:
                index - int: Insertion position index.
                card - any: Card identifier value.
                animate - bool: Whether to animate the transition.
            """
            card_obj = self.table.get_card(card)
            if card_obj.stack is not None:
                card_obj.stack.remove(card)
            card_obj.stack = self
            self.cards.insert(index, card_obj)
            self.table.stacks.remove(self)
            self.table.stacks.append(self)
            if animate:
                card_obj.springback()
            else:
                card_obj._offset = __Fixed(0, 0)

        def append(self, card, animate=True):
            """
            Appends a card to the end of the stack.

            IN:
                card - any: Card identifier value.
                animate - bool: Whether to animate the transition.
            """
            if card in self.cards:
                self.insert(len(self.cards) - 1, card, animate)
            else:
                self.insert(len(self.cards), card, animate)

        def remove(self, card):
            """
            Removes a card from the stack.

            IN:
                card - any: Card identifier value.
            """
            card_obj = self.table.get_card(card)
            self.cards.remove(card_obj)
            card_obj.stack = None
            renpy.redraw(self.table, 0)

        def shuffle(self):
            """
            Randomizes the card order in the stack.
            """
            renpy.random.shuffle(self.cards)
            renpy.redraw(self.table, 0)

        def __len__(self):
            """
            Gets the number of cards in the stack.

            OUT:
                int: Card count.
            """
            return len(self.cards)

        def __getitem__(self, idx):
            """
            Allows indexing/slicing cards in the stack.

            IN:
                idx - int or slice: Index or slice to fetch.

            OUT:
                any or list of any: Card value(s).
            """
            if isinstance(idx, slice):
                return [card.value for card in self.cards[idx]]
            return self.cards[idx].value

        def __iter__(self):
            """
            Iterates through card values in the stack.

            OUT:
                generator: Iterator over card values.
            """
            for i in self.cards:
                yield i.value

        def __contains__(self, card):
            """
            Checks if a card is in the stack.

            IN:
                card - any: Card identifier value.

            OUT:
                bool: True if card is present, False otherwise.
            """
            return self.table.get_card(card) in self.cards

        def render_to(self, rv, width, height, st, at):
            """
            Renders the stack base displayable to the parent Render object.

            IN:
                rv - Render: The parent Ren'Py Render surface.
                width - int: Available width.
                height - int: Available height.
                st - float: State time.
                at - float: Animation time.
            """
            if not self.base:
                self.rect = (self.x, self.y, 0, 0)
                return
            render = renpy.render(self.base, width, height, st, at)
            cw, ch = render.get_size()
            cx = self.x - cw // 2
            cy = self.y - ch // 2
            self.rect = (cx, cy, cw, ch)
            rv.blit(render, (cx, cy))

    class NAU(object):
        """
        Main controller class for the NAU card game. Handles state, rules, players, hands, sound effects, and rendering orchestration.
        """
        TYPES = ("number", "action", "wild")
        NUMBER_LABELS = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")
        ACTION_LABELS = ("Skip", "Draw Two", "Reverse")
        WILD_LABELS = ("Wild", "Wild Draw Four")
        COLORS = ("red", "blue", "green", "yellow")

        DRAWPILE_X = 445
        DRAWPILE_Y = 352
        DISCARDPILE_X = 850
        DISCARDPILE_Y = 352
        PLAYERHAND_X = 640
        PLAYERHAND_Y = 595
        SAYORIHAND_X = PLAYERHAND_X
        SAYORIHAND_Y = 110
        PLAYER_CARDS_OFFSET = 0
        SAYORI_CARDS_OFFSET = -6
        HAND_CARDS_LIMIT = 30

        SFX_SHUFFLE = ["mod_assets/games/nau/sfx/shuffle_0.mp3"]
        SFX_MOVE = ["mod_assets/games/nau/sfx/move_deck_0.mp3"]
        SFX_DRAW = [
            "mod_assets/games/nau/sfx/slide_0.mp3",
            "mod_assets/games/nau/sfx/slide_1.mp3",
            "mod_assets/games/nau/sfx/slide_2.mp3",
            "mod_assets/games/nau/sfx/slide_3.mp3",
            "mod_assets/games/nau/sfx/slide_4.mp3",
            "mod_assets/games/nau/sfx/slide_5.mp3"
        ]
        SFX_PLAY = [
            "mod_assets/games/nau/sfx/place_0.mp3",
            "mod_assets/games/nau/sfx/place_1.mp3",
            "mod_assets/games/nau/sfx/place_2.mp3",
            "mod_assets/games/nau/sfx/place_3.mp3",
            "mod_assets/games/nau/sfx/shove_0.mp3",
            "mod_assets/games/nau/sfx/shove_1.mp3",
            "mod_assets/games/nau/sfx/shove_2.mp3",
            "mod_assets/games/nau/sfx/shove_3.mp3"
        ]

        def __init__(self):
            """
            Initializes the NAU minigame controller, setting up stacks, hands, players, and loading the card deck.
            """
            self.table = Table(
                back=ASSETS + "cards/back.png",
                base=Null(150, 214),
                springback=0.3,
                rotate=0.15,
                can_drag=self.__can_drag
            )
            self.drawpile = self.table.stack(
                self.DRAWPILE_X,
                self.DRAWPILE_Y,
                xoff=0,
                yoff=0,
                click=True,
                drag=0
            )
            self.discardpile = self.table.stack(
                self.DISCARDPILE_X,
                self.DISCARDPILE_Y,
                xoff=0,
                yoff=0,
                drag=4,
                drop=True
            )
            self.player = _NAUPlayer(leftie=False)
            self.sayori = _NAUPlayerAI(self, leftie=True)
            self.player.hand = self.table.stack(
                self.PLAYERHAND_X,
                self.PLAYERHAND_Y,
                xoff=self.__calculate_xoffset(self.player),
                yoff=0,
                click=True,
                drag=1,
                drop=True,
                hover=True
            )
            self.sayori.hand = self.table.stack(
                self.SAYORIHAND_X,
                self.SAYORIHAND_Y,
                xoff=self.__calculate_xoffset(self.sayori, self.SAYORI_CARDS_OFFSET),
                yoff=0,
                click=True
            )
            self.set_sensitive(False)
            self.game_log = []
            self.current_turn = 1
            self.__fill_deck()

        def __can_drag(self, table, stack, card):
            """
            Determines whether a card is allowed to be dragged from a stack.

            IN:
                table - Table: The parent Table instance.
                stack - __Stack: The stack the card belongs to.
                card - any: The card value identifier.

            OUT:
                bool: True if the card can be dragged, False otherwise.
            """
            return not (stack is self.discardpile and len(self.discardpile) < 2)

        def __springback_cards(self, hand):
            """
            Triggers springback animation for all cards in a player's hand.

            IN:
                hand - __Stack: The player's hand stack.
            """
            for card in hand:
                self.table.get_card(card).springback()

        def _say_quip(self, what, interact=True, new_context=False):
            """
            Triggers Sayori to speak a given line or random choice of lines.

            IN:
                what - str or list of str: Dialog line(s) to speak.
                interact - bool: Whether to wait for user input/interaction.
                new_context - bool: Whether to run dialogue in a new Ren'Py context.
            """
            if isinstance(what, (list, tuple)):
                quip = renpy.random.choice(what)
            else:
                quip = what
            if new_context:
                renpy.invoke_in_new_context(renpy.say, store.s, quip, interact=interact)
            else:
                renpy.say(store.s, quip, interact=interact)

        def _play_sfx(self, sfx_files, channel="sound"):
            """
            Plays a random sound effect from a list of audio file paths.

            IN:
                sfx_files - list of str: SFX file paths.
                channel - str: The audio channel to use.
            """
            global disable_sfx
            if not sfx_files or disable_sfx:
                return
            sfx_file = random.choice(sfx_files)
            renpy.play(sfx_file, channel=channel)

        def _play_shuffle_sfx(self):
            """
            Plays the shuffle sound effect.
            """
            self._play_sfx(self.SFX_SHUFFLE)

        def _play_move_sfx(self):
            """
            Plays the move/deck slide sound effect.
            """
            self._play_sfx(self.SFX_MOVE)

        def _play_draw_sfx(self):
            """
            Plays a card drawing sound effect.
            """
            self._play_sfx(self.SFX_DRAW)

        def _play_play_sfx(self):
            """
            Plays a card placement sound effect.
            """
            self._play_sfx(self.SFX_PLAY)

        def __calculate_xoffset(self, player, shift=0):
            """
            Calculates card rendering spacing offset based on player hand count.

            IN:
                player - _NAUPlayer: The player object.
                shift - int: Extra shift adjustment.

            OUT:
                int: Offset distance in pixels.
            """
            offset = 32
            if player.hand is not None:
                amount = len(player.hand)
                if amount > 10:
                    offset = 28
                elif amount > 7:
                    offset = 30
            if player.isAI:
                xoffset = offset + shift
            else:
                xoffset = -(offset + shift)
            return xoffset

        def __set_xoffset(self, player, shift=0):
            """
            Applies calculated offset spacing to the player's cards and redraws.

            IN:
                player - _NAUPlayer: The player object.
                shift - int: Extra shift adjustment.
            """
            player.hand.xoff = self.__calculate_xoffset(player, shift)
            self.__springback_cards(player.hand)

        def __calculate_xpos(self, player):
            """
            Calculates starting horizontal coordinate for player hand centering.

            IN:
                player - _NAUPlayer: The player object.

            OUT:
                int: Target horizontal coordinate.
            """
            xpos = self.SAYORIHAND_X if player.isAI else self.PLAYERHAND_X
            if player.hand is not None:
                amount = len(player.hand) - 1
                offset = player.hand.xoff
            else:
                amount = 6
                offset = 32
            xpos -= (amount * offset // 2)
            return xpos

        def __set_xpos(self, player):
            """
            Applies centering coordinate to player hand and updates positions.

            IN:
                player - _NAUPlayer: The player object.
            """
            player.hand.x = self.__calculate_xpos(player)
            self.__springback_cards(player.hand)

        def __update_cards_positions(self, player, shift=0):
            """
            Updates the layout (offset spacing and start position) for a player's hand.

            IN:
                player - _NAUPlayer: The player object.
                shift - int: Extra shift adjustment.
            """
            self.__set_xoffset(player, shift)
            self.__set_xpos(player)

        def __get_card_filename(self, card):
            """
            Gets the filename tag for a card asset based on type/color/label.

            IN:
                card - _NAUCard: The card object.

            OUT:
                str: Asset filename suffix.
            """
            if card.color:
                part1 = card.color[0]
                if card.type == "number":
                    part2 = card.label
                else:
                    if card.label == "Skip":
                        part2 = "s"
                    elif card.label == "Draw Two":
                        part2 = "d2"
                    else:
                        part2 = "r"
            else:
                part1 = ""
                if card.label == "Wild":
                    part2 = "wcc"
                else:
                    part2 = "wd4"
            return part1 + part2

        def __load_card_asset(self, card):
            """
            Registers card asset image on the table.

            IN:
                card - _NAUCard: The card object to register.
            """
            card_png = self.__get_card_filename(card)
            self.table.card(card, "{0}cards/{1}.png".format(ASSETS, card_png))
            self.table.set_faceup(card, False)

        def __fill_deck(self):
            """
            Populates the draw pile with a standard card set (numbers, actions, wilds).
            """
            for t in self.TYPES:
                if t != "wild":
                    for color in self.COLORS:
                        if t == "number":
                            for dupe in range(2):
                                for label in self.NUMBER_LABELS:
                                    if dupe == 1 and label == "0":
                                        continue
                                    card = _NAUCard(t, label, color)
                                    self.__load_card_asset(card)
                                    self.drawpile.append(card)
                        else:
                            for dupe in range(2):
                                for label in self.ACTION_LABELS:
                                    card = _NAUCard(t, label, color)
                                    self.__load_card_asset(card)
                                    self.drawpile.append(card)
                else:
                    for dupe in range(4):
                        for label in self.WILD_LABELS:
                            card = _NAUCard(t, label)
                            self.__load_card_asset(card)
                            self.drawpile.append(card)

        def _update_drawpile(self, smooth=True, sound=None):
            """
            Recycles the discarded cards (except the top one) back into the draw pile and shuffles.

            IN:
                smooth - bool: Whether to pause for visual smoothing transitions.
                sound - bool: Whether to play deck move/shuffle sounds.
            """
            if sound is None:
                sound = smooth
            if smooth:
                renpy.pause(0.5, hard=True)
            if sound:
                self._play_move_sfx()
            while len(self.discardpile) > 1:
                card = self.discardpile[0]
                if card.type == "wild":
                    card.color = None
                self.table.set_faceup(card, False)
                self.table.set_rotate(card, 0)
                self.table.get_card(card).set_offset(0, 0)
                self.drawpile.append(card)
            if smooth:
                renpy.pause(0.2, hard=True)
            last_card = self.table.get_card(self.discardpile[0])
            self.table.set_rotate(last_card.value, 90)
            last_card.set_offset(0, 0)
            self.shuffle_drawpile(smooth=smooth, sound=sound)

        def _update_game_log(self, current_player, next_player):
            """
            Records the move history and player states for the current turn.

            IN:
                current_player - _NAUPlayer: The active player who just played.
                next_player - _NAUPlayer: The player whose turn is next.
            """
            next_player_data = {
                "turn": self.current_turn + 1,
                "player": next_player,
                "had_skip_turn": next_player.should_skip_turn,
                "had_draw_cards": next_player.should_draw_cards,
                "drew_card": None,
                "played_card": None
            }
            current_player_data = {
                "drew_card": current_player.drew_card,
                "played_card": self.discardpile[-1] if current_player.played_card else None
            }
            if not self.game_log:
                self.game_log.append(current_player_data)
            else:
                self.game_log[-1].update(current_player_data)
            self.game_log.append(next_player_data)

        def _actually_deal_cards(self, player, amount, smooth, sound):
            """
            Internal helper that physically transfers cards from draw pile to player hand.

            IN:
                player - _NAUPlayer: The recipient player.
                amount - int: The number of cards to deal.
                smooth - bool: Whether to animate card movement.
                sound - bool: Whether to play card drawing sounds.
            """
            player_cards = len(player.hand)
            if player_cards + amount > self.HAND_CARDS_LIMIT:
                amount = self.HAND_CARDS_LIMIT - player_cards
            for i in range(amount):
                if sound:
                    self._play_draw_sfx()
                card = self.drawpile[-1]
                player.hand.append(card, animate=smooth)
                if player.isAI:
                    self.table.set_rotate(card, -180)
                    faceup = False
                    offset = self.SAYORI_CARDS_OFFSET
                else:
                    faceup = True
                    offset = self.PLAYER_CARDS_OFFSET
                self.table.set_faceup(card, faceup)
                self.__update_cards_positions(player, offset)
                if smooth:
                    renpy.pause(0.3, hard=True)

        def deal_cards(self, player, amount=1, smooth=True, sound=None, mark_as_drew_card=True, reset_nou_var=True):
            """
            Deals cards to a player, handling drawing rules, recycling the discard pile if needed, and card count limits.

            IN:
                player - _NAUPlayer: The player to deal cards to.
                amount - int: Number of cards to deal.
                smooth - bool: Whether to animate drawing.
                sound - bool: Whether to play drawing sounds.
                mark_as_drew_card - bool: True to set player's drew_card flag.
                reset_nou_var - bool: True to reset player's yelled_nou flag.
            """
            if sound is None:
                sound = smooth
            drawpile_cards = len(self.drawpile)
            if mark_as_drew_card:
                player.drew_card = True
            if reset_nou_var:
                player.yelled_nou = False
                player.nou_reminder_timeout = 0
            if drawpile_cards >= amount:
                self._actually_deal_cards(player, amount, smooth, sound=sound)
                if player.should_draw_cards:
                    player.should_draw_cards -= amount
                if drawpile_cards == amount:
                    self._update_drawpile(smooth=smooth, sound=sound)
            else:
                cards_to_deal = amount - drawpile_cards
                self._actually_deal_cards(player, drawpile_cards, smooth, sound=sound)
                if player.should_draw_cards:
                    player.should_draw_cards -= drawpile_cards
                self._update_drawpile(smooth=smooth, sound=sound)
                drawpile_cards = len(self.drawpile)
                if drawpile_cards < cards_to_deal:
                    self._actually_deal_cards(player, drawpile_cards, smooth, sound=sound)
                    player.should_draw_cards = 0
                else:
                    self._actually_deal_cards(player, cards_to_deal, smooth, sound=sound)
                    player.should_draw_cards = 0

        def _get_current_next_players(self):
            """
            Decides who starts first based on win streaks or random selection.

            OUT:
                tuple: (current_player, next_player) player objects.
            """
            global player_win_streak
            global sayori_win_streak
            if player_win_streak:
                current_player = self.player
                next_player = self.sayori
            elif sayori_win_streak:
                current_player = self.sayori
                next_player = self.player
            else:
                if random.random() < 0.5:
                    current_player = self.player
                    next_player = self.sayori
                else:
                    current_player = self.sayori
                    next_player = self.player
            return (current_player, next_player)

        def _deal_initial_cards(self, current_player, next_player):
            """
            Deals initial hands of 7 cards to each player at game start.

            IN:
                current_player - _NAUPlayer: First player.
                next_player - _NAUPlayer: Second player.
            """
            starting_cards = 7
            for i in range(starting_cards * 2):
                if i % 2:
                    temp_player = next_player
                else:
                    temp_player = current_player
                self.deal_cards(temp_player, mark_as_drew_card=False, reset_nou_var=False)

        def prepare_game(self):
            """
            Sets up the initial board state, shuffles, deals, and places the first card onto the discard pile.
            """
            current_player, next_player = self._get_current_next_players()
            self.shuffle_drawpile()
            self._deal_initial_cards(current_player, next_player)
            ready = False
            pulled_wdf = False
            while not ready:
                card = self.drawpile[-1]
                self._play_draw_sfx()
                self.discardpile.append(card)
                self.table.set_rotate(card, 90)
                self.table.set_faceup(card, True)
                if card.type != "number":
                    if not pulled_wdf:
                        pulled_wdf = True
                        self._say_quip("Dlg when Sayori reshuffles deck.")
                        renpy.pause(0.5, hard=True)
                    else:
                        renpy.pause(1.0, hard=True)
                    new_id = len(self.drawpile) // 2 + renpy.random.randint(-10, 10)
                    self._play_draw_sfx()
                    self.drawpile.insert(new_id, card)
                    self.table.set_rotate(card, 0)
                    self.table.set_faceup(card, False)
                    renpy.pause(0.1, hard=True)
                    self.shuffle_drawpile()
                else:
                    ready = True

            if self.discardpile[-1].label == "Wild":
                if current_player.isAI:
                    self.sayori.chosen_color = self.sayori.choose_color()
                    self.discardpile[-1].color = self.sayori.chosen_color
            elif self.discardpile[-1].type == "action":
                current_player.should_skip_turn = True
                if self.discardpile[-1].label == "Draw Two":
                    current_player.should_draw_cards = 2

            current_player_data = {
                "turn": self.current_turn,
                "player": current_player,
                "had_skip_turn": current_player.should_skip_turn,
                "had_draw_cards": current_player.should_draw_cards,
                "drew_card": None,
                "played_card": None
            }
            self.game_log.append(current_player_data)
            current_player.plays_turn = True
            self.set_sensitive(not current_player.isAI)

        def play_card(self, current_player, next_player, card):
            """
            Performs the card play action: transfers a card to the discard pile, handles action/wild card logic, and schedules timeouts.

            IN:
                current_player - _NAUPlayer: Active player.
                next_player - _NAUPlayer: Inactive player.
                card - _NAUCard: The card being played.
            """
            if current_player.isAI:
                cards_offset = self.SAYORI_CARDS_OFFSET
                card_rotation = renpy.random.randint(-205, -155)
            else:
                cards_offset = self.PLAYER_CARDS_OFFSET
                card_rotation = renpy.random.randint(-13, 13)
            card_position = (renpy.random.randint(-14, 14), renpy.random.randint(-10, 10))
            self._play_play_sfx()
            self.discardpile.append(card)
            self.table.set_rotate(self.discardpile[-1], card_rotation)
            self.table.get_card(self.discardpile[-1]).set_offset(*card_position)
            self.table.set_faceup(self.discardpile[-1], True)
            self.__update_cards_positions(current_player, cards_offset)
            current_player.played_card = True
            current_player.should_play_card = False
            if self.discardpile[-1].type == "action" or self.discardpile[-1].label == "Wild Draw Four":
                next_player.should_skip_turn = True
                current_player.should_skip_turn = False
                if self.discardpile[-1].label == "Draw Two":
                    next_player.should_draw_cards = 2
                    current_player.should_draw_cards = 0
                elif self.discardpile[-1].label == "Wild Draw Four":
                    next_player.should_draw_cards = 4
                    current_player.should_draw_cards = 0
            if len(current_player.hand) == 1 and not current_player.yelled_nou:
                current_player.nou_reminder_timeout = self.current_turn + 2

        def end_turn(self, current_player, next_player):
            """
            Finalizes the turn: resets buttons, handles false-yelled penalty, handles card limits, and shifts active player.

            IN:
                current_player - _NAUPlayer: The player ending their turn.
                next_player - _NAUPlayer: The player starting their turn next.
            """
            global disable_remind_button
            global disable_yell_button
            disable_remind_button = False
            disable_yell_button = False
            if not self.drawpile:
                renpy.invoke_in_new_context(self._update_drawpile)
            self._update_game_log(current_player, next_player)
            if current_player.yelled_nou:
                if len(current_player.hand) > 1:
                    current_player.yelled_nou = False
                    current_player.nou_reminder_timeout = 0
                if current_player.should_play_card:
                    if current_player.isAI:
                        quips = _("Dlg when Sayori false-yelled 'NAU'.")
                    else:
                        quips = _("Dlg when Player false-yelled 'NAU'.")
                    self.set_sensitive(False)
                    self._say_quip(quips, new_context=True)
                    current_player.should_play_card = False
            current_player.should_skip_turn = False
            current_player.plays_turn = False
            if next_player.should_draw_cards and len(next_player.hand) + next_player.should_draw_cards > self.HAND_CARDS_LIMIT:
                if next_player.isAI:
                    quips = _("Dlg when Sayori reaches card limit.")
                else:
                    quips = _("Dlg when Player reaches card limit.")
                self.set_sensitive(False)
                self._say_quip(quips, new_context=True)
                next_player.should_draw_cards = max(self.HAND_CARDS_LIMIT - len(next_player.hand), 0)
            next_player.drew_card = False
            next_player.played_card = False
            next_player.plays_turn = True
            self.current_turn += 1
            self.set_sensitive(not next_player.isAI)

        def _win_check(self, player):
            """
            Checks if a player has run out of cards and won.

            IN:
                player - _NAUPlayer: Player to check.
            """
            global winner
            if player.hand:
                return
            self.set_sensitive(False)
            if player.isAI:
                winner = "Sayori"
            else:
                winner = "Player"
            renpy.pause(2.0, hard=True)
            renpy.jump("js_nau_game_end")

        def _is_matching_card(self, player, card):
            """
            Checks if a card from a player's hand can legally be played onto the discard pile.

            IN:
                player - _NAUPlayer: Player playing the card.
                card - _NAUCard: Card to play.

            OUT:
                bool: True if card match is legal, False otherwise.
            """
            if card not in player.hand:
                return False
            if player.should_skip_turn:
                return False
            if card.label == "Wild":
                return True
            if card.label == "Wild Draw Four":
                has_col = any(c.color == self.discardpile[-1].color for c in player.hand if c.color is not None)
                return not has_col
            return card.color == self.discardpile[-1].color or card.label == self.discardpile[-1].label

        def game_loop(self):
            """
            Executes one full iteration of player and AI turn checks.
            """
            self.sayori_turn_loop()
            self.player_turn_loop()

        def set_visible(self, value):
            """
            Shows or hides the minigame board.

            IN:
                value - bool: True to show, False to hide.
            """
            if value:
                self.table.show()
            else:
                self.table.hide()

        def set_sensitive(self, value):
            """
            Enables or disables game interaction sensitivity.

            IN:
                value - bool: True to enable, False to disable.
            """
            self.table.set_sensitive(value)

        def is_sensitive(self):
            """
            Checks if game interaction is currently enabled.

            OUT:
                bool: True if interaction enabled, False otherwise.
            """
            return self.table.sensitive

        def shuffle_drawpile(self, smooth=True, sound=None):
            """
            Shuffles the draw pile, playing card shuffling animations and sound effects.

            IN:
                smooth - bool: Whether to animate cards during shuffling.
                sound - bool: Whether to play shuffle sounds.
            """
            if sound is None:
                sound = smooth
            total_cards = len(self.drawpile)
            if total_cards > 15:
                if sound:
                    self._play_shuffle_sfx()
                k = renpy.random.randint(0, 9)
                self.table.springback = 0.2
                if smooth:
                    renpy.pause(0.2, hard=True)
                for i in range(7):
                    card_id = renpy.random.randint(0, total_cards - 2)
                    insert_id = total_cards - 1 if k == i else renpy.random.randint(0, total_cards - 2)
                    card = self.table.get_card(self.drawpile[card_id])
                    x_offset = renpy.random.randint(160, 190)
                    y_offset = renpy.random.randint(-15, 15)
                    card.set_offset(x_offset, y_offset)
                    card.springback()
                    if smooth:
                        renpy.pause(0.15, hard=True)
                    self.drawpile.insert(insert_id, card.value)
                    card.set_offset(0, 0)
                    card.springback()
                    if smooth:
                        renpy.pause(0.15, hard=True)
                self.table.springback = 0.3
            self.drawpile.shuffle()
            if smooth:
                renpy.pause(0.2, hard=True)

        def handle_nou_logic(self, player):
            """
            Validates when a player screams 'NAU' or accuses the AI of forgetting.

            IN:
                player - str: "sayori" or "player" specifying who was accused/yelled.
            """
            self.set_sensitive(False)
            if player == "sayori":
                if self.sayori.yelled_nou:
                    self._say_quip("Dlg when Sayori has already yelled 'NAU'.", new_context=True)
                elif len(self.sayori.hand) > 1:
                    self._say_quip("Dlg when Sayori doesn't need to yell 'NAU' (has more than 1 card).", new_context=True)
                elif self.sayori.nou_reminder_timeout <= self.current_turn:
                    self._say_quip("Dlg when Sayori timed out from being caught for 'NAU'.", new_context=True)
                else:
                    self._say_quip("Dlg when Sayori forgot to yell 'NAU'.", new_context=True)
                    self.deal_cards(self.sayori, amount=2, smooth=False, sound=True, mark_as_drew_card=False)
                    renpy.invoke_in_new_context(renpy.pause, 0.5, hard=True)
            elif player == "player":
                if self.player.yelled_nou:
                    self._say_quip("Dlg when Player already yelled 'NAU'.", new_context=True)
                elif len(self.player.hand) == 2:
                    self.player.yelled_nou = True
                    self.player.should_play_card = True
                    self._say_quip("Dlg when Player yells 'NAU'.", new_context=True)
                elif len(self.player.hand) > 2:
                    self._say_quip("Dlg when Player doesn't need to yell 'NAU'.", new_context=True)
                    self.deal_cards(self.player, amount=2, smooth=False, sound=True, mark_as_drew_card=False)
                    renpy.invoke_in_new_context(renpy.pause, 0.5, hard=True)
                else:
                    self._say_quip("Dlg when Player already late to yell 'NAU'.", new_context=True)
                    self.deal_cards(self.player, amount=2, smooth=False, sound=True, mark_as_drew_card=False)
                    renpy.invoke_in_new_context(renpy.pause, 0.5, hard=True)
            self.set_sensitive(True)

        def player_turn_loop(self):
            """
            Handles player interaction loops and event routing. Includes nested functions for card action authorization.
            """
            def is_player_allowed_draw_card():
                """
                Checks if player is allowed to draw a card.

                OUT:
                    bool: True if drawing is allowed, False otherwise.
                """
                return (
                    self.discardpile[-1].color is not None
                    and not (
                        (self.player.drew_card or self.player.should_skip_turn)
                        and not self.player.should_draw_cards
                    )
                    and len(self.player.hand) < self.HAND_CARDS_LIMIT
                )

            def is_player_allowed_play_card():
                """
                Checks if player is allowed to play a card.

                OUT:
                    bool: True if playing is allowed, False otherwise.
                """
                return (
                    self.discardpile[-1].color is not None
                    and not self.player.played_card
                    and not self.player.should_draw_cards
                    and not (self.player.should_skip_turn and self.player.drew_card)
                )

            def player_play_card(card_to_play):
                """
                Performs the player card action.

                IN:
                    card_to_play - _NAUCard: Card the player plays.
                """
                if not self._is_matching_card(self.player, card_to_play):
                    return
                self.set_sensitive(False)
                self.play_card(self.player, self.sayori, card_to_play)
                self.set_sensitive(True)
                self._win_check(self.player)
                if self.discardpile[-1].color is not None:
                    self.end_turn(self.player, self.sayori)

            while self.player.plays_turn:
                events = ui.interact(type="minigame")
                for event in events:
                    if event.type == "hover":
                        if event.card in self.player.hand:
                            card = self.table.get_card(event.card)
                            card.set_offset(0, -35)
                            card.springback()
                    elif event.type == "unhover":
                        if event.card in self.player.hand:
                            card = self.table.get_card(event.card)
                            card.set_offset(0, 0)
                            card.springback()
                    elif event.type in ("click", "doubleclick"):
                        if event.stack is self.drawpile and is_player_allowed_draw_card():
                            self.set_sensitive(False)
                            if self.player.should_draw_cards:
                                self.deal_cards(self.player, self.player.should_draw_cards)
                                if self.player.should_skip_turn:
                                    self.end_turn(self.player, self.sayori)
                            else:
                                self.deal_cards(self.player)
                            self.set_sensitive(True)
                        elif event.type == "doubleclick" and event.stack is self.player.hand and event.card is not None and is_player_allowed_play_card():
                            player_play_card(event.card)
                        elif event.type == "click" and event.stack is self.sayori.hand and random.random() < 0.2:
                            self._say_quip("Dlg when Player clicks Sayori's cards.")
                    elif event.type == "drag":
                        if event.stack is self.player.hand and event.drop_stack is self.discardpile and is_player_allowed_play_card():
                            player_play_card(event.card)
 
        def sayori_turn_loop(self):
            """
            Executes Sayori AI turn reasoning, card selection, and turn execution.
            """
            if not self.sayori.plays_turn:
                return
            self.sayori.thonk_pause()
            self.sayori.hand.shuffle()
            self.sayori.thonk_pause()
            if self.sayori.should_skip_turn and not self.sayori.should_draw_cards:
                self.end_turn(self.sayori, self.player)
                return
            self.sayori.guess_player_cards()
            next_card_to_play = self.sayori.choose_card()
            
            if len(self.player.hand) == 1 and not self.player.yelled_nou and self.player.nou_reminder_timeout > self.current_turn:
                if random.random() < 0.7:
                    self.set_sensitive(False)
                    self._say_quip("Dlg when Player forgot to yell 'NAU'.", new_context=True)
                    self.deal_cards(self.player, amount=2, smooth=False, sound=True, mark_as_drew_card=False)
                    renpy.invoke_in_new_context(renpy.pause, 0.5, hard=True)
                    self.set_sensitive(True)
            
            if next_card_to_play is not None and len(self.sayori.hand) == 2:
                if random.random() < 0.85:
                    self.sayori.yelled_nou = True
                    self.sayori.should_play_card = True
                    self._say_quip("Dlg when Sayori yells 'NAU'!", new_context=True)
                    self.sayori.nou_reminder_timeout = self.current_turn + 2
            
            self.sayori.play_card(next_card_to_play)

# Screens
# screen nau_stats():
#     layer "master"
#     zorder 5
#     style_prefix "choice"
    
#     add js_nau.js_get_displayable("mod_assets/games/nau/note.png") pos (5, 120) anchor (0, 0) at nau_note_rotate_left
#     add js_nau.js_get_displayable("mod_assets/games/nau/pen.png") pos (210, 370) anchor (0.5, 0.5) at nau_pen_rotate_right
    
#     text _("Cards in hand:") pos (87, 110) anchor (0, 0.5) at nau_note_rotate_left style "nau_note_text"
    
#     $ sayori_count = len(store.js_nau.game.sayori.hand)
#     $ player_count = len(store.js_nau.game.player.hand)
    
#     text _("[s_name]: [sayori_count]") pos (60, 204) anchor (0, 0.5) at nau_note_rotate_left style "nau_note_text"
#     text _("[player]: [player_count]") pos (96, 298) anchor (0, 0.5) at nau_note_rotate_left style "nau_note_text"

screen nau_gui():
    zorder 50
    style_prefix "choice"
    
    $ fn_end_turn = store.js_nau.game.end_turn
    $ fn_handle_nou_logic = store.js_nau.game.handle_nou_logic
    $ game = store.js_nau.game
    $ player = store.js_nau.game.player
    $ sayori = store.js_nau.game.sayori
    $ discardpile = store.js_nau.game.discardpile
    
    vbox:
        align (0.975, 0.5)
        spacing 10
        
        textbutton _("I'm skipping this turn"):
            xsize 294
            sensitive (
                player.plays_turn
                and (
                    (player.drew_card or len(player.hand) >= game.HAND_CARDS_LIMIT)
                    or player.should_skip_turn
                )
                and (
                    not player.should_draw_cards
                    or len(player.hand) >= game.HAND_CARDS_LIMIT
                )
                and (
                    discardpile
                    and discardpile[-1].color is not None
                )
            )
            action [
                Function(fn_end_turn, player, sayori),
                Return([])
            ]
            
        if player.plays_turn and not player.played_card:
            textbutton _("NAU!"):
                xsize 294
                sensitive not store.js_nau.disable_yell_button
                action [
                    SetField(store.js_nau, "disable_yell_button", True),
                    Function(fn_handle_nou_logic, "player")
                ]
            textbutton _("You forgot to say 'NAU'!"):
                xsize 294
                sensitive (
                    not store.js_nau.disable_remind_button
                    and not player.drew_card
                )
                action [
                    SetField(store.js_nau, "disable_remind_button", True),
                    Function(fn_handle_nou_logic, "sayori")
                ]
        else:
            textbutton _("NAU!") xsize 294 sensitive False
            textbutton _("You forgot to say 'NAU'!") xsize 294 sensitive False
            
        textbutton _("I'm giving up..."):
            xsize 294
            sensitive bool(player.hand and sayori.hand)
            action [
                SetField(store.js_nau, "winner", "Surrendered"),
                SetField(store.js_nau, "in_progress", False),
                Jump("js_nau_game_end")
            ]

    vbox:
        align (0.5, 0.5)
        spacing 10
        if (
            player.plays_turn
            and (
                discardpile
                and discardpile[-1].color is None
            )
            and player.hand
        ):
            $ top_card = game.discardpile[-1]
            
            textbutton _("Red"):
                xsize 200
                action If(
                    player.played_card,
                    true = [
                        SetField(top_card, "color", "red"),
                        Function(fn_end_turn, player, sayori),
                        Return([])
                    ],
                    false = [
                        SetField(top_card, "color", "red"),
                        Return([])
                    ]
                )
            textbutton _("Blue"):
                xsize 200
                action If(
                    player.played_card,
                    true = [
                        SetField(top_card, "color", "blue"),
                        Function(fn_end_turn, player, sayori),
                        Return([])
                    ],
                    false = [
                        SetField(top_card, "color", "blue"),
                        Return([])
                    ]
                )
            textbutton _("Green"):
                xsize 200
                action If(
                    player.played_card,
                    true = [
                        SetField(top_card, "color", "green"),
                        Function(fn_end_turn, player, sayori),
                        Return([])
                    ],
                    false = [
                        SetField(top_card, "color", "green"),
                        Return([])
                    ]
                )
            textbutton _("Yellow"):
                xsize 200
                action If(
                    player.played_card,
                    true = [
                        SetField(top_card, "color", "yellow"),
                        Function(fn_end_turn, player, sayori),
                        Return([])
                    ],
                    false = [
                        SetField(top_card, "color", "yellow"),
                        Return([])
                    ]
                )

# Labels
label mg_nau(mg_obj=None):
    $ js_update_rpc(state="Playing NAU")
    s "Sayori dlg before start."
    call js_nau_game_start from _call_js_nau_game_start
    $ js_update_rpc(state="In the spaceroom")
    return

label js_nau_game_start:
    $ store.js_nau.game = store.js_nau.NAU()

label js_nau_game_loop:
    window hide
    scene bg cardgames desk onlayer master zorder 0
    $ store.js_nau.game.set_visible(True)
    show screen nau_gui
    with Fade(0.2, 0, 0.2)
    $ renpy.pause(0.2, hard=True)
    $ store.js_nau.game.prepare_game()
    $ store.js_nau.in_progress = True
    
    while store.js_nau.in_progress:
        $ store.js_nau.game.game_loop()

label js_nau_game_end:
    $ store.js_nau.in_progress = False
    $ store.js_nau.game.set_visible(False)
    hide screen nau_gui
    
    $ main_background.form()
    show sayori abfcaa zorder 2
    
    if store.js_nau.winner == "Player":
        s "Dlg when Player wins game."
        $ store.js_nau.player_win_streak += 1
        $ store.js_nau.sayori_win_streak = 0
    elif store.js_nau.winner == "Sayori":
        s "Dlg when Sayori wins game."
        $ store.js_nau.sayori_win_streak += 1
        $ store.js_nau.player_win_streak = 0
    else:
        s "Dlg when Player surrenders."
        $ store.js_nau.player_win_streak = 0
        
    s "Would you like to play another game?{nw}"
    $ _history_list.pop()
    menu:
        s "Would you like to play another game?{fast}"
        
        "Yes.":
            jump js_nau_game_start
        "No.":
            s "Dlg when Player quits game."
            jump js_nau_quit

label js_nau_quit:
    hide screen nau_gui
    return
