from re import L
from enteties import *
import pygame as pg
import random
from camera import *
from hitbox import *
from other import *

DISTANCEX = 104
DISTANCEY = 102

SALADS = [[Cucumber, Tomato], [Cucumber, Lettuce], [Cucumber], [Tomato], [Lettuce, Tomato], [Lettuce],
          [Cucumber, Lettuce, Tomato]]
SANDWICHES = [[BottomBun, Cucumber, TopBun], [BottomBun, Tomato, TopBun],
              [BottomBun, Lettuce, TopBun], [BottomBun, Cucumber, Tomato, TopBun],
              [BottomBun, Lettuce, Tomato, TopBun], [BottomBun, Cucumber, Lettuce, TopBun],
              [BottomBun, Cucumber, Lettuce, Tomato, TopBun]]

class Level:
    def __init__(self, players):
        self.blocks = []
        self.map = []
        self.players = players
        self.recpies = []
        self.orders = []
        self.score = 0

    def set_up(self, index, screen):
        self.time = Timer((140, 650), 300)
        self.group = Camera(screen)
        self.floor = pg.sprite.Sprite()
        self.floor.image = pg.image.load('imgs/floor.png').convert()
        self.floor.rect = self.floor.image.get_rect()
        self.floor.rect.topleft = (0, 0)
        self.group.add(self.time)
        self.players = [Player(i) for i in self.players]
        self.score = Score_sprite((1000, 650))
        self.group.add(self.score)
        self.me = self.players[index]
        for i in self.players:
            i.group = self.group
            self.group.add(i)
        self.set_all()

    def generate_order(self):
        self.orders.append(random.choice(self.possible_recpies))

    def draw(self, index):
        dest, c = self.get_closest_sprite(self.players[index])
        if dest > 5:
            c = None
        self.group.draw(self.me, self.players, self.floor, c)

    def update(self):
        self.group.update()
        if self.time.time <= -2:
            return 'done'
        elif self.time.time == 8:
            return 'time'

    def set_all(self):
        row_count = 0
        x, y = 170, 120
        for rnum, row in enumerate(self.map):
            col_cnt = 0
            self.blocks.append([])
            for tnum, tile in enumerate(row):

                if True:
                    if col_cnt == 0:
                        side = 1
                    elif col_cnt == len(row) - 1:
                        side = -1

                    elif row_count == len(self.map) - 1:
                        side = -2

                    else:
                        side = 0

                bottom, left, right = False, False, False

                if tile == 1:
                    ov = Stove((col_cnt * DISTANCEX + x, DISTANCEY * row_count + y), side, bottom)

                    po = Pot((-123, 0))
                    po.placed = ov
                    ov.holds = po
                    self.group.add(po)

                    self.blocks[-1].append(ov)
                    self.group.add(ov)

                elif tile == 2:
                    cu = CuttingTable((col_cnt * DISTANCEX + x, row_count * DISTANCEY + y), side, bottom)
                    self.blocks[-1].append(cu)
                    self.group.add(cu)


                elif tile == 4:

                    cbox = ChikenCrate((col_cnt * DISTANCEX + x, row_count * DISTANCEY + y), side, bottom)
                    self.group.add(cbox)
                    self.blocks[-1].append(cbox)

                elif tile == 5:
                    cbox = Plate((col_cnt * DISTANCEX + x, row_count * DISTANCEY + y))
                    self.group.add(cbox)
                    self.blocks[-1].append(cbox)

                elif tile == 6:
                    cbox = LettuceCrate((col_cnt * DISTANCEX + x, row_count * DISTANCEY + y), side, bottom)
                    self.group.add(cbox)
                    self.blocks[-1].append(cbox)

                elif tile == 7:
                    cbox = CucumberCrate((col_cnt * DISTANCEX + x, row_count * DISTANCEY + y), side, bottom)
                    self.group.add(cbox)
                    self.blocks[-1].append(cbox)

                elif tile == 8:
                    cbox = TrashBin((col_cnt * DISTANCEX + x, row_count * DISTANCEY + y), side)
                    self.group.add(cbox)
                    self.blocks[-1].append(cbox)

                elif tile == 9:
                    cbox = TomatoCrate((col_cnt * DISTANCEX + x, row_count * DISTANCEY + y), side, bottom, left, right)
                    self.group.add(cbox)
                    self.blocks[-1].append(cbox)

                elif tile == 10:
                    cbox = GetAway((col_cnt * DISTANCEX + x, row_count * DISTANCEY + y), side)
                    self.group.add(cbox)
                    self.blocks[-1].append(cbox)

                elif tile == 11:
                    cbox = BunCrate((col_cnt * DISTANCEX + x, row_count * DISTANCEY + y), side, bottom)
                    self.group.add(cbox)
                    self.blocks[-1].append(cbox)

                elif tile == 12:
                    cbox = RiceCrate((col_cnt * DISTANCEX + x, row_count * DISTANCEY + y), side, bottom)
                    self.group.add(cbox)
                    self.blocks[-1].append(cbox)

                elif tile == 13:
                    cbox = AlgaCrate((col_cnt * DISTANCEX + x, row_count * DISTANCEY + y), side, bottom)
                    self.group.add(cbox)
                    self.blocks[-1].append(cbox)

                elif tile == 14:
                    cbox = Crate((col_cnt * DISTANCEX + x, row_count * DISTANCEY + y), side, bottom)
                    pl = Plate((-123, 1))
                    cbox.holds = pl
                    pl.placed = cbox

                    self.group.add(cbox.holds)
                    self.group.add(cbox)
                    self.blocks[-1].append(cbox)

                elif tile == -1:
                    cbox = Crate((col_cnt * DISTANCEX + x, row_count * DISTANCEY + y), side, bottom)
                    self.group.add(cbox)
                    self.blocks[-1].append(cbox)

                else:
                    self.blocks[-1].append(None)

                col_cnt += 1

            col_cnt = 0
            row_count += 1

        for i in self.players:
            self.group.add(i)

    def get_closest_sprite(self, player):
        min = (9999999, None)
        for sprite in self.group.sprites():
            if sprite == player or sprite == player.holds or type(sprite) == Timer or type(sprite) == Order:
                continue
            dest = rect_distance(player.rect, sprite.rect)
            if dest < min[0]:
                min = (dest, sprite)

        return min

class Level1(Level):
    def __init__(self,players) -> None:
        super().__init__(players)
        self.map = [[-1,7,8,9,14,14,6,8,7,-1],
                    [9,0,0,0,0,0,0,0,0,9],
                    [2,0,0,0,0,0,0,0,0,2],
                    [-1,0,0,0,0,0,0,0,0,-1],
                    [-1,7,8,9,10,0,6,8,7,-1]]


        self.score_to_beat = 500
        self.score_to_pass = 200
        self.recpies = [SALADS]

class Level2(Level):
    def __init__(self,players) -> None:
        super().__init__(players)
        self.map = [[-1,9,11,14,14,7,8,6,-1,0],
                    [2,0,0,0,0,0,0,0,0,-1],
                    [2,0,0,0,0,0,0,0.0,0,-1],
                    [-1,0,0,0,0,0,0,0,0,-1],
                    [-1,7,8,9,10,0,6,11,7,-1]]

        self.score_to_beat = 650
        self.score_to_pass = 300
        self.recpies = [SALADS + SANDWICHES]
