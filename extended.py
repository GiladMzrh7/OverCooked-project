import pygame as pg


class Player_Father():
    def __init__(self, pos, group, name):
        super().__init__()
        self.pos = pos
        self.width = 10
        self.height = 10
        self.directon = pg.math.Vector2()
        self.speed = 7
        self.holds = None
        self.group = group
        self.name = name
