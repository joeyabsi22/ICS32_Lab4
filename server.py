from ttt_board import TicTacToeBoard
import random
import socket
import time


class Server:

    def __init__(self, ip: str = '127.0.0.1', port: int = 9999):
        self.ip = ip
        self.port = port
        self.algorithm = TicTacToeAlgorithm()

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.ip, self.port))
            while True:
                client_connection = None
                try:
                    server_socket.listen(1)
                    print("Listening for client connection.")
                    client_connection, address = server_socket.accept()
                    print("Found client connection.")
                    board = TicTacToeBoard()
                    while True:
                        print("Awaiting data...")
                        data = client_connection.recv(1024).decode()
                        print(f"Received data: {data}")
                        if not data:
                            break

                        difficulty_set = False
                        if data == "E":
                            self.algorithm.set_difficulty(0)
                            difficulty_set = True
                        if data == "M":
                            self.algorithm.set_difficulty(1)
                            difficulty_set = True
                        if data == "H":
                            self.algorithm.set_difficulty(2)
                            difficulty_set = True

                        if difficulty_set:
                            pass
                            #time.sleep(1)
                            #client_connection.send("M".encode())
                        else:
                            pos = int(data) - 1
                            game_over = False
                            try:
                                if board.is_taken(pos):
                                    raise Exception()
                                if board.do_turn(pos) is not None:
                                    game_over = True
                                else:
                                    client_connection.send(board.get().encode())
                                    client_connection.send("A".encode())  # thinking
                                    time.sleep(0.01)
                                if game_over or board.do_turn(self.algorithm.get_move(board)) is not None:
                                    game_over = True
                                client_connection.send(board.get().encode())

                                if game_over:
                                    print("Ending game.")
                                    if board.check_win_state() == 1:
                                        client_connection.send("P".encode())
                                    elif board.check_win_state() == 0:
                                        client_connection.send("T".encode())
                                    else:
                                        client_connection.send("C".encode())
                                    win = board.get_win()
                                    win_message = " "
                                    for p in win:
                                        win_message += str(p)
                                    client_connection.send(win_message.encode())
                                    break
                                else:
                                    client_connection.send("M".encode())
                            except:
                                client_connection.send("B".encode())

                except(ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
                    print("Client disconnect resulted in exception.")
                finally:
                    if client_connection is not None:
                        pass
                        # client_connection.close()
                        # print("Client connection closed.")


class TicTacToeAlgorithm:

    #  difficulty: 0 -> easy, 1 -> medium, 2 -> hard
    def __init__(self, difficulty=0):
        self._difficulty = None
        self.set_difficulty(difficulty)

    def set_difficulty(self, difficulty=0):
        if type(difficulty) != int:
            return ValueError(f"Difficulty should be an int, given type {type(difficulty)}.")
        if not 0 <= difficulty <= 2:
            raise ValueError(f"Difficulty should be an int 0-2, given {difficulty}.")
        self._difficulty = difficulty

    def get_move(self, board: TicTacToeBoard):
        if self._difficulty == 0:
            return self._get_move_easy(board)
        if self._difficulty == 1:
            return self._get_move_medium(board)
        if self._difficulty == 2:
            return self._get_move_hard(board)

    def _get_move_easy(self, board: TicTacToeBoard):
        return self._get_random_position(self._all_open_positions(board))

    def _get_move_medium(self, board: TicTacToeBoard):
        if self._exists_win(board):
            return self._get_random_position(self._exists_win(board))
        if self._exists_opponent_win(board):
            return self._get_random_position(self._exists_opponent_win(board))
        return self._get_move_easy(board)

    def _get_move_hard(self, board: TicTacToeBoard):
        for f in [self._exists_win(board),
                  self._exists_opponent_win(board),
                  self._exists_fork(board),
                  self._exists_opponent_fork(board),
                  self._center_open(board),
                  self._exists_opponent_corner(board),
                  self._corner_open(board),
                  self._edge_open(board)]:
            if f:
                return self._get_random_position(f)

        return self._get_move_easy(board)

    def _get_random_position(self, open_positions: list):
        return random.choice(open_positions) if open_positions else 0

    def _exists_win(self, board: TicTacToeBoard):
        open = []

        for pos in self._all_open_positions(board):
            sums = [0,  # row sum
                    0,  # col sum
                    0,  # 048 diagonal
                    0]  # 246 diagonal

            row = pos // 3
            for delta in [-2, -1, 1, 2]:
                if (pos + delta) // 3 == row:
                    sums[0] += board.is_taken_by_computer(pos + delta)
                sums[1] += board.is_taken_by_computer(pos + 3 * delta)
                sums[2] += board.is_taken_by_computer(pos + 4 * delta)

            if pos in [2, 4, 6]:
                sums[3] = board.is_taken_by_computer(2) + board.is_taken_by_computer(4) + board.is_taken_by_computer(6)

            for sum in sums:
                if sum == 2:
                    open.append(pos)
                    break
        return open

    def _exists_opponent_win(self, board: TicTacToeBoard):
        open = []

        for pos in self._all_open_positions(board):
            sums = [0,  # row sum
                    0,  # col sum
                    0,  # 048 diagonal
                    0]  # 246 diagonal

            row = pos // 3
            for delta in [-2, -1, 1, 2]:
                if (pos + delta) // 3 == row:
                    sums[0] += board.is_taken_by_player(pos + delta)
                sums[1] += board.is_taken_by_player(pos + 3 * delta)
                sums[2] += board.is_taken_by_player(pos + 4 * delta)

            if pos in [2, 4, 6]:
                sums[3] = board.is_taken_by_player(2) + board.is_taken_by_player(4) + board.is_taken_by_player(6)

            for sum in sums:
                if sum == 2:
                    open.append(pos)
                    break
        return open

    def _exists_fork(self, board: TicTacToeBoard):
        open = []

        for pos in self._all_open_positions(board):
            board_copy = board.copy()
            board_copy.do_turn(pos)
            if len(self._exists_win(board_copy)) > 1:
                open.append(pos)
        return open

    def _exists_opponent_fork(self, board: TicTacToeBoard):

        for pos in self._all_open_positions(board):
            board_copy = board.copy()
            board_copy.do_turn(pos)

            adverse = False
            for pos2 in self._all_open_positions(board_copy):
                board_copy_2 = board_copy.copy()
                board_copy_2.do_turn(pos2)
                if len(self._exists_opponent_win(board_copy_2)) > 1 and not self._exists_win(board_copy_2):
                    adverse = True

            if not adverse and self._exists_win(board_copy):
                return [pos]

        return []

    def _center_open(self, board: TicTacToeBoard):
        return [4] if board.is_open(4) else []

    def _exists_opponent_corner(self, board: TicTacToeBoard):
        open = []

        if board.is_open(0) and board.is_taken_by_player(8):
            open.append(0)
        elif board.is_open(8) and board.is_taken_by_player(0):
            open.append(8)

        if board.is_open(2) and board.is_taken_by_player(6):
            open.append(2)
        elif board.is_open(6) and board.is_taken_by_player(2):
            open.append(6)

        return open

    def _corner_open(self, board: TicTacToeBoard):
        open = []

        for position in [0, 2, 6, 8]:
            if board.is_open(position):
                open.append(position)

        return open

    def _edge_open(self, board: TicTacToeBoard):
        open = []

        for position in [1, 3, 5, 7]:
            if board.is_open(position):
                open.append(position)

        return open

    def _all_open_positions(self, board: TicTacToeBoard):
        open = []

        for position in range(0, 9):
            if board.is_open(position):
                open.append(position)
        return open


if __name__ == '__main__':
    Server().start()
