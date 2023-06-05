from enteties import *
from levels import *
from extended import *


class Game:
    levels = [Level1,Level2]
    # This class is used to create the game.
    # this is the class that the server will use in order to handle games
    def __init__(self):
        self.level_index = 0
        self.level = self.levels[self.level_index]
        self.players_sock = []
        self.players_pos = []
        self.played = False
        self.current_orders = []
        self.names = []
        self.players = []
        self.score = 0

    def add_player(self, sock, name):
        self.players_sock.append(sock)
        self.players.append(Player_Father((400, 400), None, name))

    def start(self):
        self.played = True
        self.players_pos = [[p.pos, (0.0, 0.0)] for p in self.players]
        self.level = self.level(self.players)
