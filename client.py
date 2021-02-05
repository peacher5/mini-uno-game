#!/usr/bin/env python3

"""
01418351 sec.1 Protocol Homework
--------------------------------
 6010405360
 Peranut Wattanakulsiri (Peach)
--------------------------------
"""

from socket import *
from typing import List
from ctypes import *
import os
import re
import sys


class Request:
    JOIN = 'JOIN'
    LISTEN_FOR_UPDATES = 'LISTEN_FOR_UPDATES'
    CHOOSE = 'CHOOSE'
    DRAW = 'DRAW'

    class Get:
        OPPONENT_NAME = 'GET OPPONENT_NAME'
        GAME_STATUS = 'GET GAME_STATUS'


class Response:
    OK = 'OK'
    WAIT = 'WAIT'

    class Now:
        YOUR_TURN = 'NOW YOUR_TURN'
        OPPONENT_TURN = 'NOW OPPONENT_TURN'
        WIN = 'NOW WIN'
        LOSE = 'NOW LOSE'

    class Error:
        GAME_BUSY = 'ERROR GAME_BUSY'
        CANNOT_PLAY_THIS_CARD = 'ERROR CANNOT_PLAY_THIS_CARD'
        INVALID_COMMAND = 'ERROR INVALID_COMMAND'
        ILLEGAL_COMMAND = 'ERROR ILLEGAL_COMMAND'


class NoResponseError(Exception):
    pass


class Color:
    BLACK = ('30', '40')
    WHITE = ('37', '47')
    RED = ('31', '41')
    GREEN = ('32', '42')
    YELLOW = ('33', '43')
    BLUE = ('34', '44')


class CardColor:
    RED = '1;37;41'
    GREEN = '1;30;42'
    YELLOW = '1;30;43'
    BLUE = '1;37;44'
    WHITE = '2;30;47'


class TextStyle:
    NORMAL = '0'
    BOLD = '1'
    DIM = '2'


class Game:
    def __init__(self, player_name, opponent_name):
        self.player_name: str = player_name
        self.opponent_name: str = opponent_name
        self.my_turn: bool = None
        self.cards: List[str] = None
        self.opponent_cards_no: int = None
        self.action_card: str = None
        self.color: str = None
        self.is_over: bool = None
        self.is_won: bool = None

    def update(self, my_turn: bool, cards: List[str], opponent_cards_no: int, action_card: str, color: str):
        self.my_turn = my_turn
        self.cards = cards
        self.opponent_cards_no = opponent_cards_no
        self.action_card = action_card
        self.color = color

    def over(self, is_won: bool):
        self.is_over = True
        self.is_won = is_won


COLOR_INFO = {
    'R': ('RED', CardColor.RED),
    'G': ('GREEN', CardColor.GREEN),
    'Y': ('YELLOW', CardColor.YELLOW),
    'B': ('BLUE', CardColor.BLUE),
}


def with_color(msg: str, code=None, fg=None, bg=None, style=TextStyle.NORMAL):
    if not code:
        styles = [style]
        if fg:
            styles.append(fg[0])
        if bg:
            styles.append(bg[1])
        code = ';'.join(x for x in styles)
    return f'\x1b[{code}m{msg}\x1b[0m'


def clear_screen(use_command=False):
    if use_command:
        if os.name == 'nt':
            os.system('cls')
            return
        print("\033[2J")
        return

    clear_text = ''
    for i in range(17):
        clear_text += ' ' * 72 + '\n'
    move_cursor(0, 0)
    print(clear_text)


def move_cursor(x, y):
    if os.name == 'nt':
        h = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        windll.kernel32.SetConsoleCursorPosition(h, COORD(x + 1, y + 1))
    else:
        print(f"\033[{y + 1};{x + 1}H", end='')


def print_card(x, y, card_color, symbol):
    move_cursor(x, y)
    print(f'\x1b[{card_color}m     \x1b[0m')
    move_cursor(x, y + 1)
    print(f'\x1b[{card_color}m  {symbol}  \x1b[0m')
    move_cursor(x, y + 2)
    print(f'\x1b[{card_color}m     \x1b[0m')


def print_back_card(x, y):
    move_cursor(x, y)
    print(f'\x1b[{CardColor.WHITE}m     \x1b[0m')
    move_cursor(x, y + 1)
    print(f'\x1b[{CardColor.WHITE}m UNO \x1b[0m')
    move_cursor(x, y + 2)
    print(f'\x1b[{CardColor.WHITE}m     \x1b[0m')


def print_wild_card(x, y, draw_no_indicator):
    if draw_no_indicator == '4':
        label = '+4'
    else:
        label = '  '

    move_cursor(x, y)
    print(f'\x1b[1;30;47m  {label} \x1b[0m')
    move_cursor(x, y + 1)
    print(f'\x1b[1;30;47m \x1b[0m', end='')
    print(f'\x1b[{CardColor.RED}m \x1b[0m', end='')
    print(f'\x1b[{CardColor.GREEN}m \x1b[0m', end='')
    print(f'\x1b[{CardColor.BLUE}m \x1b[0m', end='')
    print(f'\x1b[1;30;47m \x1b[0m')
    move_cursor(x, y + 2)
    print(f'\x1b[1;30;47m     \x1b[0m')


def print_star_frame():
    for i in range(16):
        move_cursor(0, i)
        print('*')

        move_cursor(72, i)
        print('*')

    move_cursor(2, 0)
    print('*')

    move_cursor(70, 0)
    print('*')

    move_cursor(2, 15)
    print('*')

    move_cursor(70, 15)
    print('*')


def draw_main_ui():
    clear_screen(use_command=True)

    print_star_frame()

    move_cursor(6, 2)
    print(' ███▄ ▄███▓ ██▓ ███▄    █  ██▓    █    ██  ███▄    █  ▒█████')
    move_cursor(6, 3)
    print('▓██▒▀█▀ ██▒▓██▒ ██ ▀█   █ ▓██▒    ██  ▓██▒ ██ ▀█   █ ▒██▒  ██▒')
    move_cursor(6, 4)
    print('▓██    ▓██░▒██▒▓██  ▀█ ██▒▒██▒   ▓██  ▒██░▓██  ▀█ ██▒▒██░  ██▒')
    move_cursor(6, 5)
    print('▒██    ▒██ ░██░▓██▒  ▐▌██▒░██░   ▓▓█  ░██░▓██▒  ▐▌██▒▒██   ██░')
    move_cursor(6, 6)
    print('▒██▒   ░██▒░██░▒██░   ▓██░░██░   ▒▒█████▓ ▒██░   ▓██░░ ████▓▒░')
    move_cursor(6, 7)
    print('░ ▒░   ░  ░░▓  ░ ▒░   ▒ ▒ ░▓     ░▒▓▒ ▒ ▒ ░ ▒░   ▒ ▒ ░ ▒░▒░▒░')
    move_cursor(6, 8)
    print('░  ░      ░ ▒ ░░ ░░   ░ ▒░ ▒ ░   ░░▒░ ░ ░ ░ ░░   ░ ▒░  ░ ▒ ▒░')
    move_cursor(6, 9)
    print('░      ░    ▒ ░   ░   ░ ░  ▒ ░    ░░░ ░ ░    ░   ░ ░ ░ ░ ░ ▒')
    move_cursor(6, 10)
    print('       ░    ░           ░  ░        ░              ░     ░ ░')

    move_cursor(4, 12)
    print(with_color('- Press ENTER to play -'.center(65), style=TextStyle.BOLD))

    move_cursor(4, 13)
    print(with_color('- Press CTRL + C to quit the game -'.center(65), style=TextStyle.BOLD))

    move_cursor(4, 15)
    input(with_color(' 6010405360 Peranut W. (Protocol Design Project 2020) ',
                     fg=Color.BLACK, bg=Color.WHITE, style=TextStyle.BOLD))


def draw_in_game_ui(game: Game):
    color_name, style_code = COLOR_INFO.get(game.color)

    clear_screen()

    print_star_frame()

    # Current color
    move_cursor(4, 0)
    print(with_color(color_name.center(65), code=style_code))

    # Opponent name
    move_cursor(4, 1)
    print(with_color(game.opponent_name.center(65), style=TextStyle.BOLD))

    # Opponent cards
    x = int(65 / 2 - (game.opponent_cards_no * 5 + game.opponent_cards_no - 1) / 2) + 4

    opponent_show_card_no = min(game.opponent_cards_no, 10)

    for _ in range(opponent_show_card_no):
        print_back_card(x, 2)
        x += 6

    # Action card
    x = int(65 / 2 - 5 / 2) + 4

    if game.action_card[0] == 'C':
        print_wild_card(x, 6, game.action_card[1])
    elif game.action_card[1] == 'S':
        print_card(x, 6, COLOR_INFO.get(game.action_card[0])[1], '⊘')
    else:
        print_card(x, 6, COLOR_INFO.get(game.action_card[0])[1], game.action_card[1])

    # Deck
    print_back_card(64, 6)

    # Player cards
    show_cards = game.cards[:10]

    cards_no = len(show_cards)
    x = int(65 / 2 - (cards_no * 5 + cards_no - 1) / 2) + 4

    if show_cards[0]:
        for i, card in enumerate(show_cards):
            if card[0] == 'C':
                print_wild_card(x, 10, card[1])
            elif card[1] == 'S':
                if os.name == 'nt':
                    skip = '0'
                else:
                    skip = '⊘'
                print_card(x, 10, COLOR_INFO.get(card[0])[1], skip)
            else:
                print_card(x, 10, COLOR_INFO.get(card[0])[1], card[1])

            move_cursor(x + 1, 13)
            card_id = chr(ord('A') + i)
            print(with_color(f'[{card_id}]', style=TextStyle.DIM))
            x += 6

    # Player name
    move_cursor(4, 14)
    print(with_color(game.player_name.center(65), style=TextStyle.BOLD))

    # Turn
    move_cursor(4, 15)
    if game.is_over:
        turn = ' GAME OVER '
    elif game.my_turn:
        turn = ' YOUR TURN '
    else:
        turn = ' OPPONENT TURN '

    print(with_color(turn, fg=Color.BLACK, bg=Color.WHITE, style=TextStyle.BOLD))

    move_cursor(0, 16)
    print()


def send(client_socket: socket, message: str):
    client_socket.send(message.encode())


def log_response(message):
    move_cursor(0, 17)
    print(' ' * 72)
    move_cursor(0, 17)
    print(with_color(f'Response from server: {message}', style=TextStyle.DIM))


def recieve(client_socket: socket, multicheck=False):
    message = client_socket.recv(1024).decode()
    if not message:
        raise NoResponseError()

    if multicheck:
        messages = message[:-1].split('\n')

        log_response(messages[-1])
        return messages

    log_response(message[:-1])
    return message[:-1]


def update_game_status(client_socket: socket, game: Game):
    send(client_socket, Request.Get.GAME_STATUS)
    response = recieve(client_socket)

    regex = re.search(r'^(NOW .+) (.*) (\d+) (.{2}) ([RGYB])$', response)

    if not regex:
        return

    if regex.group(1).startswith(Response.Now.WIN):
        game.over(True)
    elif regex.group(1).startswith(Response.Now.LOSE):
        game.over(False)

    my_turn = regex.group(1).startswith(Response.Now.YOUR_TURN)
    cards = regex.group(2).split(',')
    opponent_cards_no = int(regex.group(3))
    action_card = regex.group(4)
    color = regex.group(5)

    game.update(my_turn, cards, opponent_cards_no, action_card, color)

    draw_in_game_ui(game)


def main(host, port):
    try:
        draw_main_ui()

        move_cursor(4, 12)
        print(' ' * 65)

        move_cursor(4, 13)
        print(' ' * 65)

        move_cursor(4, 13)
        print(with_color('*****************************'.center(65), style=TextStyle.BOLD))

        move_cursor(4, 12)
        player_name = input(with_color('Enter your name:             '.center(
            65).rstrip(' ') + ' ', style=TextStyle.BOLD))

        move_cursor(4, 12)
        print(' ' * 65)

        move_cursor(4, 13)
        print(' ' * 65)

        move_cursor(4, 13)
        print(with_color('Connecting to the server...'.center(65), style=TextStyle.DIM))

        client_socket = socket(AF_INET, SOCK_STREAM)

        client_socket.connect((host, port))

        move_cursor(4, 12)
        print(' ' * 65)

        move_cursor(4, 13)
        print(' ' * 65)

        move_cursor(4, 12)
        print(with_color(f'Welcome, {player_name}!'.center(65), style=TextStyle.BOLD))

        move_cursor(4, 13)
        print(with_color('Waiting for a player...'.center(65), style=TextStyle.DIM))

    except KeyboardInterrupt:
        print()
        return
    except ConnectionError as e:
        clear_screen(use_command=True)
        move_cursor(0, 0)
        print('Cannot connect to the server:', e)
        return

    try:
        send(client_socket, f'{Request.JOIN} {player_name}')

        response = recieve(client_socket)

        if response == Response.Error.GAME_BUSY:
            print('Server is full! Please try again later.')
            return

        if response == Response.WAIT:
            response = recieve(client_socket)

        if response != Response.OK:
            return

        send(client_socket, Request.Get.OPPONENT_NAME)

        opponent_name = recieve(client_socket)

        game = Game(player_name, opponent_name)

        while True:
            update_game_status(client_socket, game)

            if game.is_over:
                if game.is_won:
                    result = 'You Win!'
                else:
                    result = 'You Lose.'

                move_cursor(16, 15)
                input(with_color(f'{result} Press ENTER to quit the game.', style=TextStyle.BOLD))
                clear_screen(use_command=True)
                move_cursor(0, 0)
                return

            if game.my_turn:
                while True:
                    move_cursor(16, 15)
                    print(' ' * 52)

                    move_cursor(16, 15)
                    max_id = chr(ord('A') + len(game.cards) - 1)
                    card = input(with_color(
                        f'Choose a card (A-{max_id}) or draw one (X): ', style=TextStyle.BOLD))

                    if len(card) == 1:
                        card = card.upper()

                        if 'A' <= card <= max_id:
                            card_index = ord(card) - ord('A')

                            request = f'{Request.CHOOSE} {card_index}'

                            if game.cards[card_index][0] == 'C':
                                move_cursor(16, 15)
                                print(' ' * 52)

                                move_cursor(16, 15)
                                color = input(with_color(
                                    f'Choose a color (R)ed, (G)reen, (Y)ellow or (B)lue: ', style=TextStyle.BOLD))

                                color = color.upper()
                                if color in ['R', 'G', 'Y', 'B']:
                                    request += f' {color}'

                            send(client_socket, request)
                            response = recieve(client_socket)

                            if response == Response.OK:
                                break

                            if response == Response.Error.CANNOT_PLAY_THIS_CARD:
                                move_cursor(16, 15)
                                print(' ' * 52)

                                move_cursor(16, 15)
                                input(with_color(
                                    'You can\'t play this card. Choose again. [ENTER]', style=TextStyle.BOLD))
                            else:
                                move_cursor(16, 15)
                                print(' ' * 52)

                                move_cursor(16, 15)
                                input(f'Unknown Error: {response}')

                        elif card == 'X':
                            send(client_socket, Request.DRAW)
                            response = recieve(client_socket)

                            if response == Response.OK:
                                break

                            move_cursor(16, 15)
                            input(f'Unknown Error: {response}')
            else:
                move_cursor(20, 15)
                print(with_color('Waiting for your opponent...', style=TextStyle.BOLD))

                send(client_socket, Request.LISTEN_FOR_UPDATES)
                responses = recieve(client_socket, multicheck=True)

                if responses[-1] == Response.WAIT:
                    responses = recieve(client_socket, multicheck=True)

                if responses[-1] != Response.OK:
                    return

    except (NoResponseError, EOFError, KeyboardInterrupt):
        pass
    except ConnectionError as e:
        print(f'Error: {e}')
    finally:
        client_socket.close()
        print()


# Windows Cursor Move Fix
class COORD(Structure):
    pass


STD_OUTPUT_HANDLE = -11

if __name__ == '__main__':

    if os.name == 'nt':
        COORD._fields_ = [("X", c_short), ("Y", c_short)]

    HOST = 'localhost'
    PORT = 12099

    argc = len(sys.argv)
    if argc >= 2:
        HOST = sys.argv[1]
    if argc == 3:
        PORT = int(sys.argv[2])

    main(HOST, PORT)
