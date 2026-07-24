#Reversi/Othello
default persistent.reversi_winfactor = 30

init 10 python:
    def reversi_n_to_xy(n, sx = 1, sy = None, ox = 0, oy = 0):
        """
        Converts a linear board index (0-63) to 2D coordinates (x, y).

        IN:
            n - int: Linear board cell index.
            sx - int: Horizontal scale factor.
            sy - int: Vertical scale factor.
            ox - int: Horizontal offset.
            oy - int: Vertical offset.

        OUT:
            tuple: (x, y) coordinates.
        """
        y = n >> 3
        x = n & 7 
        return (x * sx + ox, y * (sy or sx) + oy)

    def reversi_xy_to_n(x, y):
        """
        Converts 2D board coordinates (x, y) to a linear index (0-63).

        IN:
            x - int: Horizontal position.
            y - int: Vertical position.

        OUT:
            int: Linear cell index.
        """
        return (y << 3) + x

    def reversi_gen_board(scheme = 0):
        """
        Generates the initial board state.

        IN:
            scheme - int: The layout scheme to use (0 = Standard).

        OUT:
            list of int: The 64-element board array.
        """
        if scheme == 0:
            b = [0] * 64
            # Place initial 4 discs in the center
            b[27] = 3
            b[28] = 1
            b[35] = 1
            b[36] = 3
            return b
        raise ValueError("Reversi start scheme %s not found" % scheme)

    def reversi_prep(self, restart = False, *args, **kwargs):
        """
        Prepares and initializes the Reversi game state.

        IN:
            restart - bool: True if restarting the game, preserving current scores.
        """
        self.board = reversi_gen_board(kwargs.get("scheme") or 0)
        self.players_turn = True
        self.state = 0 # 0 = in progress, 1 = player won, -1 = Sayori won, -2 = restart, 2 = draw
        self.occupied_cells = [2, 2] # Index 0: Sayori's score, Index 1: Player's score
        self.with_ai = kwargs.get('ai') if 'ai' in kwargs else True
        if not restart:
            self.score = [0, 0]
        reversi_check_board(1)
        self.last_move = None
        self.no_moves = False
    
    def reversi_cell(x, y = None):
        """
        Retrieves the content of a specific board cell.

        IN:
            x - int: Linear cell index, or 2D X coordinate if y is provided.
            y - int: Optional 2D Y coordinate.

        OUT:
            int: Cell state (0 = free, 1 = white/Sayori's, 3 = black/player's).
        """
        if not (y is None):
            try:
                return reversi.board[reversi_xy_to_n(x, y)]
            except IndexError:
                return 0
        elif not (x is None):
            try:
                return reversi.board[x]
            except IndexError:
                return 0
    
    def reversi_sprite(info):
        """
        Returns the sprite resource name for a given cell state.

        IN:
            info - int: Disc/cell state.

        OUT:
            str: Sprite resource tag.
        """
        n = "reversi_"
        if info == 3:
            n += 'black'
        else:
            n += 'white'
        return n
    
    def reversi_trajectory(a, b):
        """
        Calculates direction and distance between two board cells.

        IN:
            a - int: Starting linear cell index.
            b - int: Ending linear cell index.

        OUT:
            tuple: (dx, dy, distance) step direction and cell distance.
        """
        a, b = tuple(reversi_n_to_xy(a)), tuple(reversi_n_to_xy(b))
        dx, dy = b[0]-a[0], b[1]-a[1]
        adx, ady = abs(dx), abs(dy)
        dist = max(adx, ady)
        try:
            dx, dy = dx//adx, dy//ady
        except:
            if dx == 0:
                return 0, dy//ady, dist
            return dx//adx, 0, dist
        return dx, dy, dist

    def reversi_reverse(info):
        """
        Reverses a disc's color/party value.

        IN:
            info - int: Current cell value.

        OUT:
            int: Reversed cell value (1 -> 3, 3 -> 1, 0 -> 0).
        """
        if info == 1:
            return 3
        elif info == 3:
            return 1
        return 0
    
    class ReversiMove:
        """
        Represents a single Reversi move, tracking placement and flipped discs.
        """
        def __init__(self, who, cell, mate_cells):
            """
            Constructor for ReversiMove.

            IN:
                who - int: The player index (0 = Sayori, 1 = Player).
                cell - int: Placement cell index.
                mate_cells - set of int: Indices of mate discs that complete the flip lines.
            """
            self.performer = who
            self.cell = cell
            self.mate_cells = mate_cells
            self.undone = False
        
        def __str__(self):
            """
            Serializes the move into Reversi Notation format.

            OUT:
                str: Serialized move string.
            """
            note = str(self.cell) + ":"
            note += ",".join(str(i) for i in self.mate_cells)
            return note
            
        def unite(self, other):
            """
            Unites another move's flip paths with this move.

            IN:
                other - ReversiMove: The other move to merge with.
            """
            for mate in other.mate_cells:
                self.mate_cells.add(mate)
        
        def perform(self, jump = None):
            """
            Executes the move on the board, updating board cells and scores.
            """
            cell = self.cell
            cell_x,cell_y = reversi_n_to_xy(cell)
            reversi.board[cell] = (self.performer << 1) + 1
            new_cells = 1
            enemy = 0 if self.performer else 1
            for mate in self.mate_cells:
                dx, dy, dist = reversi_trajectory(cell, mate)
                x, y = cell_x, cell_y
                for i in range(dist-1):
                    x += dx
                    y += dy
                    n = reversi_xy_to_n(x, y)
                    info = reversi_cell(n)
                    reversi.board[n] = reversi_reverse(info)
                    reversi.occupied_cells[enemy] -= 1
                new_cells += dist - 1
            reversi.occupied_cells[self.performer] += new_cells
            self.undone = False
        
        def undo(self):
            """
            Undoes the move, restoring previous board states and scores.
            """
            if self.undone:
                raise ValueError("Can't undo undone move")
            cell = self.cell
            cell_x,cell_y = reversi_n_to_xy(cell)
            restored_cells = 1
            enemy = 0 if self.performer else 1
            for mate in self.mate_cells:
                dx, dy, dist = reversi_trajectory(cell, mate)
                x, y = cell_x, cell_y
                for i in range(dist-1):
                    x += dx
                    y += dy
                    n = reversi_xy_to_n(x, y)
                    info = reversi_cell(n)
                    reversi.board[n] = reversi_reverse(info)
                    reversi.occupied_cells[enemy] += 1
                restored_cells += dist - 1
            reversi.board[cell] = 0
            reversi.occupied_cells[self.performer] -= restored_cells
            self.undone = True
        
        def get_cost(self):
            """
            Calculates the strategic cost/value of the move.

            OUT:
                int: Calculated cost value.
            """
            cost = riversi_pos_eval(self.final, reversi_cell(self.start))
            for mate in self.mate_cells:
                dx, dy, dist = reversi_trajectory(self.cell, mate)
                cost = 10 * (dist-1)
            return cost
            
    def reversi_gen_moves(n, party = None):
        """
        Generates possible valid moves starting from a specific board cell.

        IN:
            n - int: Board cell index to check.
            party - int: Player index to filter moves for.

        OUT:
            list of ReversiMove: Generated moves list.
        """
        moves = []
        x, y = reversi_n_to_xy(n)
        cur_disk = reversi_cell(n)
        disk_party = (cur_disk & 2) >> 1
        if cur_disk & 1 != 0 and (party is None or disk_party == party):
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    ix, iy = x, y
                    dist = 0
                    while True:
                        ix += dx
                        iy += dy
                        dist += 1
                        i = reversi_xy_to_n(ix, iy)
                        if i > 63 or ix > 7 or ix < 0 or iy > 7 or iy < 0:
                            break
                        info = reversi.board[i]
                        if info == 0:
                            if dist > 1:
                                moves.append(ReversiMove(disk_party, i, {n}))
                            break 
                        elif info == cur_disk:
                            break
        return moves
    
    def reversi_all_moves(party):
        """
        Retrieves all possible valid moves on the board for a player.

        IN:
            party - int: Player index (0 = Sayori, 1 = Player).

        OUT:
            list of ReversiMove: List containing ReversiMove objects or None.
        """
        all_moves = [None] * 64
        for i in range(64):
            moves = reversi_gen_moves(i, party)
            for move in moves:
                k = move.cell
                if all_moves[k] is None:
                    all_moves[k] = move
                else:
                    all_moves[k].unite(move)
        return all_moves
    
    def reversi_cur_party():
        """
        Checks which player is currently active.

        OUT:
            int: Active player index (0 = Sayori, 1 = Player).
        """
        return 1 if reversi.players_turn else 0
    
    def reversi_win_factor_alter(alter):
        """
        Adjusts the AI difficulty win factor threshold.

        IN:
            alter - int: Value change (increment or decrement).
        """
        persistent.reversi_winfactor += alter
        if persistent.reversi_winfactor < 0:
            persistent.reversi_winfactor = 0
        elif persistent.reversi_winfactor > 59:
            persistent.reversi_winfactor = 59
    
    def reversi_check_state():
        """
        Checks if the game has ended and returns the winning state.

        OUT:
            int: Game state (0 = in progress, 1 = player won, -1 = Sayori won, 2 = draw).
        """
        oc = reversi.occupied_cells
        if sum(oc) >= 64 or reversi.no_moves:
            if oc[1] > oc[0]:
                return 1
            elif oc[1] == oc[0]:
                return 2
            else:
                return -1
        return 0
    
    def reversi_check_board(party):
        """
        Generates and assigns selectable moves for the current board state.

        IN:
            party - int: Active player index.
        """
        reversi.selectable = reversi_all_moves(party)
    
    def reversi_get_depth():
        """
        Calculates search depth for the AI lookahead.

        OUT:
            int: AI prediction lookahead depth.
        """
        return 1 + persistent.reversi_winfactor // 15
    
    def reversi_select(n):
        """
        Validates and registers a selected cell index.

        IN:
            n - int: Linear cell index to select.
        """
        if n is None or reversi.board[n] != 0:
            reversi.selected = None
        elif not (n < 0 or n > 63):
            reversi.selected = n
    
    def reversi_finish_turn(check_state = True, skipped = False):
        """
        Finalizes a player turn, swapping turns and checking state.

        IN:
            check_state - bool: True to run win condition checks.
            skipped - bool: True if the previous turn had no valid moves.
        """
        reversi_select(None)
        reversi.players_turn = not reversi.players_turn
        reversi_check_board(reversi_cur_party())
        if check_state:
            reversi.state = reversi_check_state()
            if reversi.state == 0 and not reversi.players_turn and reversi.with_ai:
                renpy.call_in_new_context('mg_reversi_ai_turn')
            elif reversi.state != 0:
                renpy.invoke_in_new_context(renpy.pause, 1.5)
                renpy.call('mg_reversi_s_comment', reversi.state)
                return None
        # Skip turn if active player has no moves available
        if not any(x is not None for x in reversi.selectable):
            if not skipped:
                reversi_finish_turn(check_state, True)
            else:
                reversi.no_moves = True
                reversi_finish_turn(True, True)
            
    def reversi_click(n):
        """
        Handles board clicks, executing moves on valid selectable cells.

        IN:
            n - int: Linear index of clicked board cell.
        """
        reversi_select(n)
        if not (reversi.selected is None or reversi.selectable[n] is None):
            reversi.selectable[n].perform()
            reversi_finish_turn()
    
    def reversi_ai_turn():
        """
        Executes AI move selection using minimax/best move calculation.
        """
        moves = reversi_best_move(0, 1)[1]
        if len(moves):
            move = renpy.random.choice(moves)
            reversi.last_move = move
            move.perform()
        reversi_finish_turn()
    
    def reversi_best_move(party, depth = None, alpha = -64, beta = 64):
        """
        Runs alpha-beta minimax algorithm to identify strategic moves.

        IN:
            party - int: Playing party ID.
            depth - int: Max search lookahead depth.
            alpha - int: Alpha cutoff score.
            beta - int: Beta cutoff score.

        OUT:
            tuple: (best_score, list of ReversiMove)
        """
        moves = list(filter(lambda x: x is not None, reversi.selectable))
        if len(moves) == 0 or depth == 0 or sum(reversi.occupied_cells) >= 64:
            alpha = reversi.occupied_cells[party] - reversi.occupied_cells[0 if party else 1]
            return alpha, ()
        
        best_moves = []
        for move in moves:
            if alpha >= beta:
                break
            move.perform()
            last_player = reversi.players_turn
            reversi_finish_turn(False)
            total_eval = 0
            if last_player != reversi.players_turn:
                recursion_result = reversi_best_move(reversi_cur_party(), depth - 1, -beta, -alpha)
                total_eval = -recursion_result[0]
            else:
                recursion_result = reversi_best_move(reversi_cur_party(), depth, alpha, beta)
                total_eval = recursion_result[0]
            if total_eval > alpha:
                best_moves = [move]
                alpha = total_eval
            elif total_eval == alpha:
                best_moves.append(move)
            move.undo()
            reversi_finish_turn(False)
        return alpha, best_moves
    
    import copy
    def reversi_copy_board():
        """
        Creates a copy of the active board fields.

        OUT:
            list: Copy of Reversi board cells.
        """
        return copy.copy(reversi.field)
    
    def reversi_debug_setState():
        """
        Debug helper to force game states manually.
        """
        new_state = renpy.invoke_in_new_context(renpy.input, _("Input the state ID"), allow = "0123456789-")
        new_state = int(new_state)
        reversi.state = new_state 
        renpy.call("mg_reversi_s_comment", new_state)
    
    def reversi_debug_restartScheme():
        """
        Debug helper to restart with custom start layout schemes.
        """
        scheme = renpy.invoke_in_new_context(renpy.input, _("Input the scheme ID"), allow = "0123456789-")
        scheme = int(scheme)
        reversi(True, scheme = scheme)

init 11 python:
    class ReversiWrapper(object):
        def __call__(self, restart=False, *args, **kwargs):
            reversi_prep(self, restart, *args, **kwargs)

    if "reversi" not in globals() or not isinstance(reversi, ReversiWrapper):
        reversi = ReversiWrapper()
        reversi()

    
    
image reversi_selectable:
    "mod_assets/images/minigames/checkers_selected.png"
    zoom 0.75
    
image reversi_cursor:
    
    im.MatrixColor("mod_assets/images/minigames/checkers_selected.png",
    (0, 0, 0, 0, 0,
    0, 0, 0, 0, 1,
    0, 1, 0, 0, 0,
    0, 0, 0, 0.5, 0))
    zoom 0.75

image reversi_white:
    "mod_assets/images/minigames/checkers_manW.png"
    zoom 0.75
image reversi_black:
    "mod_assets/images/minigames/checkers_manB.png"
    zoom 0.75

image reversi_board = "mod_assets/images/minigames/reversi_board.png"

## Reversi Board Screen #######################################################
## Renders the grid background, playable coordinates, and selectable cells.
screen mg_reversi_board():
    add "paper" xalign 0.5 xzoom 1.1
    for move in reversi.selectable:
        if move is not None and (reversi.players_turn or config.developer):
            add "reversi_selectable" pos reversi_n_to_xy(move.cell, 75, -75, 442, 585)
    add "reversi_board" xalign 0.65 yalign 0.5
    vbox:
        pos 1045, 80
        spacing 46
        
        for i in range(1, 9):
            text str(i) style "choice_button_text" color "#000"
    hbox:
        pos 475, 36
        spacing 58
        
        for i in "HGFEDCBA":
            text i style "choice_button_text" color "#000"

## Reversi Play Screen ########################################################
## Displays game pieces, selection buttons, and scores for the game.
screen mg_reversi_scr():
    layer "master"
    zorder 100
    
    python:
        from math import sqrt
        sc = 0.8
        diag_sc = sqrt(sc*sc * 2)

    use mg_reversi_board()
    
    for y in range(8):
        for x in range(0, 8):
            $ p = (442 + x * 75, 585 - y * 75)
            $ n = reversi_xy_to_n(x, y)
            $ i = reversi_cell(n)
            
            #Add a selection button
            if reversi.players_turn or not reversi.with_ai:
                button:
                    background None
                    pos p
                    xysize (70, 70)
                    anchor (0, 0)
                    hover_background "reversi_cursor"
                    keyboard_focus True
                    action Function(reversi_click, n)
            
            #Draw the piece sprite
            if i & 1:
                add reversi_sprite(i) pos p
            
                    
    vbox:
        pos (205, 85)
        spacing 5
        text "[s_name]: " + str(reversi.score[0]):# style s_text_style():
            if not reversi.players_turn:
                color "#6acdcd"
        text "[player]: " + str(reversi.score[1]):# style s_text_style():
            if reversi.players_turn:
                color "#f00"
        hbox:
            spacing 8
            text str(reversi.occupied_cells[0]) color "#6acdcd" xsize 60# style s_text_style()
            text ":" color "#000"# style s_text_style()
            text str(reversi.occupied_cells[1]) color "#f00" xsize 60# style s_text_style()
    vbox:
        style_prefix "choice"
        yalign 0.99
        xanchor 0
        pos (205, 600)
        spacing 5
        
        textbutton _("Restart (R)") xpadding 0 xsize 200 keysym 'r' action [SetField(reversi, 'state', -2), Function(renpy.call, "mg_reversi_s_comment", -2)]
        textbutton _("Quit (Q)") xpadding 0 xsize 200 keysym 'q' action Jump("mg_reversi_quit")
        # if config.developer:
        #     textbutton _("Restart without AI (Shift+R)") xpadding 0 xsize 200 keysym 'shift_R' action Function(reversi, True, ai = False)
        #     textbutton _("Restart with a debug scheme (Alt+R)") xpadding 0 xsize 200 keysym 'alt_R' action Function(reversi_debug_restartScheme)
        #     textbutton _("Set state") xpadding 0 xsize 200 action Function(reversi_debug_setState)
        #     if reversi.last_move:
        #         if reversi.last_move.undone:
        #             textbutton _("Redo (Z)") xpadding 0 xsize 200 keysym 'z' action Function(reversi.last_move.perform)
        #         else:
        #             textbutton _("Undo (Z)") xpadding 0 xsize 200 keysym 'z' action Function(reversi.last_move.undo)

## Main entry label to start the Reversi minigame.
label mg_reversi(mg_obj=None):
    # $justIsSitting = False
    $ js_update_rpc(state="Playing Reversi")
    show sayori abhfaaa at t11
    call screen mg_reversi_scr() nopredict
    return

## Handles Sayori's reaction comments based on the end-game state or actions.
## state: -1 = Sayori victory, 1 = Player victory, 2 = draw, -2 = restart
label mg_reversi_s_comment(id = 0):
    pause 1.5
    hide screen mg_reversi_scr
    
    if id == -1: # Sayori wins
        $ random_id = renpy.random.randint(0, 2)
        if random_id == 0:
            s ebbccea "Yay! I won this game!"
            s abgcaoa "Don't worry, you'll have better luck next time~"
        elif random_id == 1:
            s abgckda "Oh, the board is full."
            s "And you have less pieces."
            s abgcaoa "Well, maybe you'll have more next time!"
        else:
            s ebgccaa "Don't worry!"
            s "Maybe you'll win next time."
            s abagiia "You'll just have to watch out for my ultra smart moves~."
    elif id == 1: # Player wins
        $ random_id = renpy.random.randint(0, 2)
        if random_id == 0:
            s abagaha "Okay, you win!"
            s gbagiaa "But know I'll be more crafty next time!"
        elif random_id == 1:
            s bbegboaj "Woah, you're better than me at this game."
            s "Maybe, I should pay more attention next round."
        else:
            s abagkgaj "Wait, you took more pieces than me!"
            s bbagciaj "I should probably be more attentive next time."
    elif id == 2: # Draw
        $ random_id = renpy.random.randint(0, 1)
        if random_id == 0:
            s eahcaoa "Hey, we split the board in half!"
            s gahdkdaj "Unless I messed up my math."
            s abfdcoa "But a draw is also a result, isn't it?"
        else:
            s ebbcaoa "Hey, we have the same number of pieces!"
            s ebgccqa "We really seem to have {i}soooooooooo{/i} much in common, ehehe~"
    elif id == -2: # Restart
        $ random_id = renpy.random.randint(0, 1)
        if random_id == 0:
            s ebhfada "Are you giving up?"
            s abhfcaa "Ok, we'll start again, but I'll get a point for this game."
        else:
            s ebagaba "What's up, [player]?"
            s "Do you think you'll lose?"
            s ebagbca "Or do you just want to do a nice thing?"
            s abhfcaa "Anyways, according to the game rules, I'll get a point for this game."
            s "But maybe, you'll win next time."
    python:
        if id < 0:
            reversi_win_factor_alter(id)
            reversi.score[0] += 1
        elif id == 1:
            reversi_win_factor_alter(1)
            reversi.score[1] += 1
        else:
            reversi.score[0] += 1
            reversi.score[1] += 1
        reversi(True)
    
    return


## Event label representing the AI thinking time and move execution.
label mg_reversi_ai_turn:
    python:
        randTime = renpy.random.triangular(0.25, 2)
        renpy.pause(randTime)
        reversi_ai_turn()
    pause 0.25
    return
    
## Exit cleanup label for Reversi.
label mg_reversi_quit:
    $ js_update_rpc(state="In the spaceroom")
    hide screen mg_reversi_scr
    
    with dissolve

    return
