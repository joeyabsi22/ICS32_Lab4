class InvalidPositionException(Exception):
    pass


class TicTacToeBoard:

    def __init__(self):
        self._board = [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]
        self._turn = True
        self._num_turns = 0

    def copy(self):
        new_board = TicTacToeBoard()
        new_board._board = [self._board[0].copy(), self._board[1].copy(), self._board[2].copy()]
        new_board._turn = self._turn
        new_board._num_turns = self._num_turns
        return new_board

    def __str__(self):
        return f" {self._board[0][0]} | {self._board[0][1]} | {self._board[0][2]} \n" \
               f"-----------\n" \
               f" {self._board[1][0]} | {self._board[1][1]} | {self._board[1][2]} \n" \
               f"-----------\n" \
               f" {self._board[2][0]} | {self._board[2][1]} | {self._board[2][2]} "

    def get(self):
        return f"{self._board[0][0]}{self._board[0][1]}{self._board[0][2]}" \
               f"{self._board[1][0]}{self._board[1][1]}{self._board[1][2]}" \
               f"{self._board[2][0]}{self._board[2][1]}{self._board[2][2]}"

    def get_num_turns(self):
        return self._num_turns

    #  True -> player
    #  False -> computer
    def get_turn(self):
        return self._turn

    def get_row_col(self, pos):
        if not 0 <= pos <= 8:
            raise InvalidPositionException(f"The selected position ({pos}) is out of bounds (must be 0-8).")
        r = pos // 3
        c = pos % 3
        return r, c

    def is_taken(self, pos):
        r, c = 0, 0
        try:
            r, c = self.get_row_col(pos)
        except:
            return False
        return False if self._board[r][c] == ' ' else True

    def is_open(self, pos):
        r, c = 0, 0
        try:
            r, c = self.get_row_col(pos)
        except:
            return False
        return not self.is_taken(pos)

    def is_taken_by_player(self, pos):
        r, c = 0, 0
        try:
            r, c = self.get_row_col(pos)
        except:
            return False
        return True if self._board[r][c] == 'X' else False

    def is_taken_by_computer(self, pos):
        r, c = 0, 0
        try:
            r, c = self.get_row_col(pos)
        except:
            return False
        return True if self._board[r][c] == 'O' else False

    def do_turn(self, pos):
        if self._num_turns == 9:
            raise InvalidPositionException("The board is full, thus the game has ended.")
        if self.is_taken(pos):
            raise InvalidPositionException(f"The selected position ({pos}) is already occupied.")
        else:
            r, c = self.get_row_col(pos)
            self._board[r][c] = 'X' if self._turn else 'O'
            self._turn = not self._turn
            self._num_turns += 1
            return self.check_win_state()

    #  None -> no game-ending condition yet
    #  1 -> player has won
    #  0 -> tie
    #  -1 -> computer has won
    def check_win_state(self):
        for r in range(3):
            if self._board[r][0] == self._board[r][1] == self._board[r][2] != ' ':
                return 1 if self._board[r][0] == 'X' else -1

        for c in range(3):
            if self._board[0][c] == self._board[1][c] == self._board[2][c] != ' ':
                return 1 if self._board[0][c] == 'X' else -1

        if self._board[0][0] == self._board[1][1] == self._board[2][2] != ' ':
            return 1 if self._board[1][1] == 'X' else -1

        if self._board[2][0] == self._board[1][1] == self._board[0][2] != ' ':
            return 1 if self._board[1][1] == 'X' else -1

        return 0 if self._num_turns == 9 else None

    def get_win(self):
        positions = set()

        if self._board[0][0] == self._board[1][1] == self._board[2][2] != ' ':
            positions.add(0)
            positions.add(4)
            positions.add(8)

        if self._board[0][2] == self._board[1][1] == self._board[2][0] != ' ':
            positions.add(2)
            positions.add(4)
            positions.add(6)

        if self._board[0][0] == self._board[0][1] == self._board[0][2] != ' ':
            positions.add(0)
            positions.add(1)
            positions.add(2)

        if self._board[1][0] == self._board[1][1] == self._board[1][2] != ' ':
            positions.add(3)
            positions.add(4)
            positions.add(5)

        if self._board[2][0] == self._board[2][1] == self._board[2][2] != ' ':
            positions.add(6)
            positions.add(7)
            positions.add(8)

        if self._board[0][0] == self._board[1][0] == self._board[2][0] != ' ':
            positions.add(0)
            positions.add(3)
            positions.add(6)

        if self._board[0][1] == self._board[1][1] == self._board[2][1] != ' ':
            positions.add(1)
            positions.add(4)
            positions.add(7)

        if self._board[0][2] == self._board[1][2] == self._board[2][2] != ' ':
            positions.add(2)
            positions.add(5)
            positions.add(8)

        return positions

