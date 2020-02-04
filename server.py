#!/usr/bin/env python3

"""
01418351 sec.1 Protocol Homework
--------------------------------
 6010405360
 Peranut Wattanakulsiri (Peach)
--------------------------------
"""

from socket import *
from datetime import datetime
from threading import Thread
from typing import List
import os
import random
import re


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


class Card:
    NUMBERS = (
        'R1', 'R2', 'R3', 'R4', 'R5', 'R6',
        'G1', 'G2', 'G3', 'G4', 'G5', 'G6',
        'Y1', 'Y2', 'Y3', 'Y4', 'Y5', 'Y6',
        'B1', 'B2', 'B3', 'B4', 'B5', 'B6',
    )
    SKIPS = ('RS', 'GS', 'YS', 'BS')
    WILDS = ('C0', 'C0', 'C4', 'C4')


class Player:
    def __init__(self, name, client_socket):
        self.name = name
        self.client_socket = client_socket
        self.in_hand: List[str] = None
        self.is_waiting = False
        self.last_turn_received = 0


class SharedData:
    def __init__(self):
        self.is_game_created = False
        self.players: List[Player] = []
        self.turn: bool = None
        self.turn_no = 0
        self.current_color: str = None
        self.deck: List[str] = None
        self.discard_pile: List[str] = None


class TextColor:
    BLACK = (30, 40)
    WHITE = (37, 30)
    RED = (31, 41)
    GREEN = (32, 42)
    YELLOW = (33, 43)
    BLUE = (34, 44)


class TextStyle:
    NORMAL = 0
    BOLD = 1
    DIM = 2


def with_color(msg: str, fg=None, bg=None, style=TextStyle.NORMAL):
    if os.name == 'nt':
        return msg

    styles = [style]
    if fg:
        styles.append(fg)
    if bg:
        styles.append(bg)
    code = ';'.join(str(x) for x in styles)
    return f'\x1b[{code}m{msg}\x1b[0m'


def log(message: str):
    time = datetime.now().strftime('[%d/%m/%y %H:%M:%S]')
    print(f'{with_color(time, style=TextStyle.DIM)} {message}')


def recieve(client_socket: socket, prefix: str):
    message = client_socket.recv(1024).decode()
    log(f'[{prefix}] >> {message}')
    return message


def send(client_socket: socket, message: str, prefix: str):
    client_socket.send(f'{message}\n'.encode())
    log(f'[{prefix}] << {message}')


def generate_game_state(sharedData: SharedData):
    sharedData.turn = random.randint(0, 1)

    number_cards = list(Card.NUMBERS)
    sharedData.discard_pile = [number_cards.pop(random.randint(0, len(number_cards) - 1))]

    sharedData.current_color = sharedData.discard_pile[0][0]

    sharedData.deck = number_cards + list(Card.SKIPS) + list(Card.WILDS)

    sharedData.players[0].in_hand = []
    sharedData.players[1].in_hand = []

    for i in range(6):
        sharedData.players[0].in_hand.append(
            sharedData.deck.pop(random.randint(0, len(sharedData.deck) - 1)))

        sharedData.players[1].in_hand.append(
            sharedData.deck.pop(random.randint(0, len(sharedData.deck) - 1)))


def clear_game_state(sharedData: SharedData):
    for player in sharedData.players:
        player.client_socket.close()
    sharedData.players.clear()
    sharedData.is_game_created = False
    sharedData.turn = None
    sharedData.turn_no = 0
    sharedData.current_color = None
    sharedData.deck = None
    sharedData.discard_pile = None


def draw_card(sharedData, index, amount):
    for i in range(amount):
        if len(sharedData.deck) == 0:
            discard_pile_without_action_card = sharedData.discard_pile[:-1]

            random.shuffle(discard_pile_without_action_card)

            sharedData.deck = discard_pile_without_action_card
            action_card = sharedData.discard_pile[-1]
            sharedData.discard_pile = [action_card]

        top_deck = sharedData.deck.pop(0)
        sharedData.players[index].in_hand.append(top_deck)


def can_play_card(card1, card2):
    color1, number1 = card1
    color2, number2 = card2
    return color1 == color2 or number1 == number2 or color1 == 'C' or color2 == 'C'


def handle_client(client_socket: socket, address_info, client_no, sharedData: SharedData):
    game_crashed = False

    try:
        #
        # Init Game State
        #
        while True:
            join_request = recieve(client_socket, client_no)

            if not join_request:
                return

            join_regex = re.search(r'^JOIN (.*)$', join_request)

            if join_regex:
                if len(sharedData.players) >= 2:
                    send(client_socket, Response.Error.GAME_BUSY, client_no)
                    return
                break

            send(client_socket, Response.Error.INVALID_COMMAND, client_no)

        player_name = join_regex.group(1)
        player_index = len(sharedData.players)

        sharedData.players.append(Player(player_name, client_socket))

        send(client_socket, Response.WAIT, client_no)

        if len(sharedData.players) == 2:
            generate_game_state(sharedData)

            send(client_socket, Response.OK, client_no)
            send(sharedData.players[0].client_socket, Response.OK, client_no)

            sharedData.is_game_created = True

        #
        # Playing State
        #
        while True:
            request = recieve(client_socket, client_no)

            if not request:
                return

            if not sharedData.is_game_created:
                send(client_socket, Response.Error.INVALID_COMMAND, client_no)
                continue

            if request == 'LISTEN_FOR_UPDATES':
                send(client_socket, Response.WAIT, client_no)

                if sharedData.turn_no > sharedData.players[player_index].last_turn_received:
                    send(client_socket, Response.OK, client_no)
                    continue

                sharedData.players[player_index].is_waiting = True
                continue

            opponent_index = 1 - player_index
            action_card = sharedData.discard_pile[-1]
            current_color = sharedData.current_color

            get_regex = re.search(r'^GET (.*)$', request)

            if get_regex:
                action = get_regex.group(1)

                if action == 'OPPONENT_NAME':
                    send(client_socket, sharedData.players[opponent_index].name, client_no)

                elif action == 'GAME_STATUS':

                    cards = ','.join(sharedData.players[player_index].in_hand)
                    cards_no = len(sharedData.players[player_index].in_hand)
                    opponent_cards_no = len(sharedData.players[opponent_index].in_hand)

                    if cards_no == 0 or opponent_cards_no > 10:
                        response = Response.Now.WIN
                    elif opponent_cards_no == 0 or cards_no > 10:
                        response = Response.Now.LOSE
                    elif sharedData.turn == player_index:
                        response = Response.Now.YOUR_TURN
                    else:
                        response = Response.Now.OPPONENT_TURN

                    response += f' {cards} {opponent_cards_no} {action_card} {current_color}'

                    sharedData.players[player_index].last_turn_received = sharedData.turn_no
                    send(client_socket, response, client_no)
            elif sharedData.turn != player_index:
                send(client_socket, Response.Error.ILLEGAL_COMMAND, client_no)
            else:
                if request == 'DRAW':
                    draw_card(sharedData, player_index, 1)
                    sharedData.turn = opponent_index
                else:
                    choose_regex = re.search(r'^CHOOSE (\d+)(.*)$', request)

                    if not choose_regex:
                        send(client_socket, Response.Error.INVALID_COMMAND, client_no)
                        continue

                    card_index = int(choose_regex.group(1))

                    if card_index >= len(sharedData.players[player_index].in_hand):
                        send(client_socket, Response.Error.INVALID_COMMAND, client_no)
                        continue

                    card = sharedData.players[player_index].in_hand[card_index]

                    if not can_play_card(card, action_card):
                        send(client_socket, Response.Error.CANNOT_PLAY_THIS_CARD, client_no)
                        continue

                    if card in ['C0', 'C4']:
                        color_regex = re.search(r'^ ([RGYB])$', choose_regex.group(2))

                        if not color_regex:
                            send(client_socket, Response.Error.INVALID_COMMAND, client_no)
                            continue

                        sharedData.current_color = color_regex.group(1)

                        if card == 'C4':
                            draw_card(sharedData, opponent_index, 4)
                    else:
                        sharedData.current_color = card[0]

                    sharedData.players[player_index].in_hand.pop(card_index)
                    sharedData.discard_pile.append(card)

                    if not card in Card.SKIPS:
                        sharedData.turn = opponent_index

                sharedData.turn_no += 1
                send(client_socket, Response.OK, client_no)

                if sharedData.players[opponent_index].is_waiting:
                    sharedData.players[opponent_index].is_waiting = False
                    send(sharedData.players[opponent_index].client_socket, Response.OK, client_no)

    except (ConnectionError, OSError, KeyboardInterrupt):
        game_crashed = True
    finally:
        if game_crashed:
            clear_game_state(sharedData)
        elif sharedData.is_game_created:
            is_joined_player = False
            for player in sharedData.players:
                if player.client_socket == client_socket:
                    is_joined_player = True
                    break
            if is_joined_player:
                clear_game_state(sharedData)
            else:
                client_socket.close()
        else:
            for i in range(len(sharedData.players)):
                if sharedData.players[i].client_socket == client_socket:
                    sharedData.players.pop(i)
                    break

            client_socket.close()
            ip, port = address_info
            log(f'Client {ip} on port {port} connection closed')


def main(port):
    try:
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind(('', port))
        server_socket.listen(2)

        log(f'Server is running on port {port}')

        sharedData = SharedData()

        client_no = 0

        while True:
            client_socket, address_info = server_socket.accept()

            ip, port = address_info
            log(f'Connected to client {ip} on port {port}')

            client_no += 1

            Thread(target=handle_client, args=(
                client_socket, address_info, client_no, sharedData)).start()

    except OSError as e:
        log(f'Error: {e}')
    except KeyboardInterrupt:
        pass
    finally:
        server_socket.close()
        log('Server is now closed -- bye!')


if __name__ == '__main__':
    PORT = 12099
    main(PORT)
