import socket
import tkinter
import tkinter as tk

class Client:

    def __init__(self, ip=None, port: int = 9999):
        self.ip = ip
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_think_milliseconds = 1000

        self._awaiting_move_text = "Your turn! Please choose a position above."
        self._bad_move_text = "That position is already taken.\nPlease choose a different position above."

    def start(self):
        self.connect()
        self.handle_difficulty()
        self.handle_game()

    def connect(self):
        if self.ip is not None:
            self.connect_to_ip(self.ip)
            return

        self.connect_window = tk.Tk()
        self.main_frame = tk.Frame(self.connect_window)
        self.main_frame.pack()
        entry_label = tk.Label(self.main_frame, text="Please enter the IP address:", font=('Courier', 20), height=4, width=30)
        entry_label.pack()
        self.ip_entry_var = tk.StringVar()
        ip_entry = tk.Entry(self.main_frame, font=('Courier', 20), textvariable=self.ip_entry_var)
        ip_entry.pack()
        ok_button = tk.Button(self.main_frame, text="OK", font=('Courier', 20), height=4, width=10)
        ok_button.bind('<Button-1>', self.handle_ip_entry)
        ok_button.pack()
        self.error_label = tk.Label(self.main_frame, text="", foreground="red", height=7)
        self.error_label.pack()

        self.connect_window.eval('tk::PlaceWindow . center')
        self.connect_window.mainloop()

        if self.ip is None:
            print("User manually closed IP address entry window.")
            quit(0)

    def handle_ip_entry(self, event):
        provided_ip = self.ip_entry_var.get()
        error_text = ""
        if not provided_ip:
            error_text = "Please enter an IP address."
        elif self.connect_to_ip(provided_ip):
            print("Connected to IP address.")
            self.connect_window.destroy()
            self.ip = provided_ip
            return
        else:
            error_text = f"The provided IP address ({provided_ip}) failed to connect. Please try again."
        self.error_label.config(text=error_text)


    def connect_to_ip(self, ip):
        try:
            self.client_socket.connect((ip, self.port))
            print("Connected.")
        except Exception as e:
            print(e)
            return False
        return True

    def handle_difficulty(self):
        self.chosen_difficulty = None
        self.difficulty_window = tk.Tk()

        frame = tk.Frame(self.difficulty_window)
        frame.grid(row=0, columnspan=3)
        tk.Label(frame, text="Please choose a difficulty:", font=('Courier', 20), height=4).pack()

        button_frame = tk.Frame(self.difficulty_window)
        button_frame.grid(row=1, column=0)
        tk.Button(button_frame, text="EASY", foreground='green', font=('Courier', 30), command=self.easy, width=10, height=4).pack()

        button_frame = tk.Frame(self.difficulty_window)
        button_frame.grid(row=1, column=1)
        tk.Button(button_frame, text="MEDIUM", foreground='orange', font=('Courier', 30), command=self.medium, width=10, height=4).pack()

        button_frame = tk.Frame(self.difficulty_window)
        button_frame.grid(row=1, column=2)
        tk.Button(button_frame, text="HARD", foreground='red', font=('Courier', 30), command=self.hard, width=10, height=4).pack()

        self.difficulty_window.eval('tk::PlaceWindow . center')
        self.difficulty_window.mainloop()

        if self.chosen_difficulty is None:
            print("User manually closed difficulty window.")
            self.client_socket.close()
            quit(0)
        else:
            self.client_socket.send(self.chosen_difficulty.encode())

    def easy(self):
        self.chosen_difficulty = "E"
        self.difficulty_window.destroy()

    def medium(self):
        self.chosen_difficulty = "M"
        self.difficulty_window.destroy()

    def hard(self):
        self.chosen_difficulty = "H"
        self.difficulty_window.destroy()

    def handle_game(self):
        self.server_is_asking = False
        self.buttons = []

        self.window = tk.Tk()
        frame = tk.Frame(self.window)
        frame.grid(row=0, columnspan=3)
        difficulty_text = ""
        difficulty_color = ""
        if self.chosen_difficulty == "E":
            difficulty_text = "EASY"
            difficulty_color = "green"
        elif self.chosen_difficulty == "M":
            difficulty_text = "MEDIUM"
            difficulty_color = "orange"
        elif self.chosen_difficulty == "H":
            difficulty_text = "HARD"
            difficulty_color = "red"
        tk.Label(frame, text=difficulty_text, font=('Courier', 20), foreground=difficulty_color, height=3).pack()


        button_handlers = [self.handle_b1,
                           self.handle_b2,
                           self.handle_b3,
                           self.handle_b4,
                           self.handle_b5,
                           self.handle_b6,
                           self.handle_b7,
                           self.handle_b8,
                           self.handle_b9]

        i = 0
        for r in range(3):
            for c in range(3):
                frame = tk.Frame(self.window)
                frame.grid(row=r+1, column=c)
                self.buttons.append(tk.Button(frame, text=" ", command=button_handlers[i], font=('Courier', 30),
                                              width=10, height=4))
                self.buttons[-1].pack()
                i += 1

        frame = tk.Frame(self.window)
        frame.grid(row=4, columnspan=3)
        self.status_label = tk.Label(frame, text=self._awaiting_move_text, font=('Courier', 20), height=4)
        self.status_label.pack()

        frame = tk.Frame(self.window)
        frame.grid(row=4, columnspan=3)
        self.play_again_button = tk.Button(frame, font=('Courier', 20), command=self.handle_play_again, height=3)
        # do not pack till game is over

        self.server_is_asking = True
        self.window.eval('tk::PlaceWindow . center')
        self.window.mainloop()
        self.client_socket.close()

    def send_to_server(self, message: str):
        if self.server_is_asking:
            self.server_is_asking = False
            self.client_socket.send(message.encode())
            return True
        else:
            return False

    def get_server_response(self):
        return self.client_socket.recv(1024).decode()

    def handle_grid_button(self, button: int):
        if self.send_to_server(str(button)):

            responses = []

            response = "A"
            while len(response) > 1 or response == "A" or response == "P" or response == "T" or response == "C":
                response = self.get_server_response()
                responses.append(response)

            if len(responses) == 1:
                self.status_label.config(text=self._bad_move_text)
                self.server_is_asking = True
                return

            self.update_grid(responses[0])
            if responses[1] != "A":
                self.write_win_condition(responses[1], responses[2])
                return
            else:
                self.status_label.config(text="The computer is thinking...")
                self.window.after(self.server_think_milliseconds, lambda: self.update_grid(responses[2]))
                if responses[3] != "M":
                    self.window.after(self.server_think_milliseconds, lambda: self.write_win_condition(responses[3], responses[4]))
                else:
                    self.window.after(self.server_think_milliseconds, lambda: self.status_label.config(text=self._awaiting_move_text))
                    self.window.after(self.server_think_milliseconds, lambda: self.server_asking())

    def server_asking(self):
        self.server_is_asking = True

    def write_win_condition(self, status, win_pattern):
        self.status_label.destroy()
        color = ""
        if status == "P":
            self.play_again_button.config(text="You won!\nClick here to play again.")
            color = "green"
        if status == "T":
            self.play_again_button.config(text="The game ended in a tie!\nClick here to play again.")
            color = "orange"
        if status == "C":
            self.play_again_button.config(text="You lost!\nClick here to play again.")
            color = "red"

        for n in range(9):
            if str(n) in win_pattern:
                self.buttons[n].config(background=color)
        self.play_again_button.pack()

    def update_grid(self, board_data):
        for i in range(9):
            self.buttons[i].config(text=board_data[i])

    def handle_b1(self):
        self.handle_grid_button(1)
    def handle_b2(self):
        self.handle_grid_button(2)
    def handle_b3(self):
        self.handle_grid_button(3)
    def handle_b4(self):
        self.handle_grid_button(4)
    def handle_b5(self):
        self.handle_grid_button(5)
    def handle_b6(self):
        self.handle_grid_button(6)
    def handle_b7(self):
        self.handle_grid_button(7)
    def handle_b8(self):
        self.handle_grid_button(8)
    def handle_b9(self):
        self.handle_grid_button(9)

    def handle_play_again(self):
        self.window.destroy()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.start()


if __name__ == '__main__':
   Client().start()
