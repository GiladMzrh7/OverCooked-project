import pygame as pg
from enteties import *

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
ANGLE_W = 10
ANGLE_H = 0.3


class CuttingTable(pg.sprite.Sprite):
    def __init__(self, pos, side=0, bottom=False):
        super().__init__()
        self.image = pg.image.load('imgs/chopping_crate.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.side = side
        if side == 0:
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top, self.rect.width, self.rect.height * 2 // 3)

        elif side == 1:
            self.image = pg.transform.rotate(self.image, 90)
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top + self.rect.height // 2, self.rect.width,
                                            self.rect.height * 2 // 3)


        elif side == -2:
            self.image = pg.transform.flip(self.image, False, True)
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top + self.rect.height // 2, self.rect.width,
                                            self.rect.height * 2 // 3)

        else:
            self.image = pg.transform.rotate(self.image, 270)
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top, self.rect.width * 2 // 3, self.rect.height)

        self.hitbox = True
        self.placeable_items = ALL_INGRIDENS
        self.holds = None

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)


class Stove(pg.sprite.Sprite):
    def __init__(self, pos, side=0, bottom=False):
        super().__init__()
        self.side = side
        if side == 0:
            self.image = pg.image.load('imgs/stove.png').convert_alpha()

        elif side == 1:
            self.image = pg.image.load('imgs/stove.png').convert_alpha()
            self.image = pg.transform.rotate(self.image, 90)

        else:
            self.image = pg.image.load('imgs/stove.png').convert_alpha()
            self.image = pg.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.pos = pos
        self.hitbox = True
        self.placeable_items = ALL_PICKABLE
        self.holds = None

        if side != -2 and side != 2:
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top, self.rect.width, self.rect.height * 3 // 5)
        else:
            self.hitbox_rect = self.rect

    def update(self) -> None:
        if type(self.holds) == Pot and type(self.holds.already) == Rice:
            if self.holds.already.cook_progress < 300:
                self.holds.already.cook_progress += 0.2

            elif not self.holds.already.cooked:
                self.holds.already.cooked = True

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)


class Crate(pg.sprite.Sprite):
    def __init__(self, pos, side=0, bottom=False) -> None:
        super().__init__()
        self.type = Chicken
        self.side = side

        if side == 0:
            self.image = pg.image.load('imgs/crate.jpg').convert_alpha()
            self.rect = self.image.get_rect()
            self.rect.topleft = pos
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top, self.rect.width, self.rect.height * 2 // 3)

        elif side == 1:
            self.image = pg.image.load('imgs/crate.jpg').convert_alpha()
            self.image = pg.transform.rotate(self.image, 90)
            self.rect = self.image.get_rect()
            self.rect.topleft = pos
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top, self.rect.width, self.rect.height * 2 // 3)

        else:
            self.image = pg.image.load('imgs/crate.jpg').convert_alpha()
            self.image = pg.transform.flip(self.image, True, False)
            self.rect = self.image.get_rect()
            self.rect.topleft = pos
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top + self.image.get_rect().height // 2,
                                            self.rect.width, self.rect.height * 2 // 3)

        self.pos = pos
        self.hitbox = True

        self.placeable_items = ALL_PICKABLE
        self.holds = None

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)


class ChikenCrate(pg.sprite.Sprite):
    def __init__(self, pos, side=0, bottom=False) -> None:
        super().__init__()
        self.type = Chicken
        self.side = side

        self.is_last_under = bottom

        if side == 0:
            self.image = pg.image.load('imgs/chicken_box.png').convert_alpha()
            self.rect = self.image.get_rect()
            self.rect.topleft = pos
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top, self.rect.width, self.rect.height * 2 // 3)

        elif side == 1:
            self.image = pg.image.load('imgs/chicken_box.png').convert_alpha()
            self.rect = self.image.get_rect()
            self.rect.topleft = pos
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top, self.rect.width, self.rect.height * 2 // 3)

        else:
            self.image = pg.image.load('imgs/chicken_box.png').convert_alpha()
            self.rect = self.image.get_rect()
            self.rect.topleft = pos
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top + self.image.get_rect().height // 2,
                                            self.rect.width, self.rect.height * 2 // 3)

        self.pos = pos
        self.hitbox = True

        self.placeable_items = ALL_PICKABLE
        self.holds = None

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)


class LettuceCrate(pg.sprite.Sprite):
    def __init__(self, pos, side=0, bottom=False) -> None:
        super().__init__()
        self.type = Lettuce
        self.side = side

        if side == 0:
            self.image = pg.image.load('imgs/lettuce_box.png').convert_alpha()
            self.rect = self.image.get_rect()
            self.rect.topleft = pos
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top, self.rect.width, self.rect.height * 2 // 3)

        elif side == 1:
            self.image = pg.image.load('imgs/lettuce_box.png').convert_alpha()
            self.rect = self.image.get_rect()
            self.rect.topleft = pos
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top, self.rect.width, self.rect.height * 2 // 3)

        else:
            self.image = pg.image.load('imgs/lettuce_box.png').convert_alpha()
            self.rect = self.image.get_rect()
            self.rect.topleft = pos
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top + self.image.get_rect().height // 2,
                                            self.rect.width, self.rect.height * 2 // 3)

        self.pos = pos
        self.hitbox = True
        self.placeable_items = ALL_PICKABLE
        self.holds = None

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)


class CucumberCrate(pg.sprite.Sprite):
    def __init__(self, pos, side=0, bottom=False) -> None:
        super().__init__()
        self.type = Cucumber
        self.side = side

        if side == 0:
            self.image = pg.image.load('imgs/cucumber_box.png').convert_alpha()
            self.rect = self.image.get_rect()
            self.rect.topleft = pos
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top, self.rect.width, self.rect.height * 2 // 3)


        elif side == 1:
            self.image = pg.image.load('imgs/cucumber_box.png').convert_alpha()
            self.rect = self.image.get_rect()
            self.rect.topleft = pos
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top, self.rect.width, self.rect.height * 2 // 3)


        else:
            self.image = pg.image.load('imgs/cucumber_box.png').convert_alpha()
            self.rect = self.image.get_rect()
            self.rect.topleft = pos
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top + self.image.get_rect().height // 2,
                                            self.rect.width, self.rect.height * 2 // 3)

        self.pos = pos
        self.hitbox = True
        self.placeable_items = ALL_PICKABLE
        self.holds = None

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)


class TomatoCrate(pg.sprite.Sprite):
    def __init__(self, pos, side=0, bottom=False, left=False, right=False) -> None:
        super().__init__()
        self.type = Tomato
        self.side = side
        self.is_last_under = bottom
        self.image = pg.image.load('imgs/tomato_box.png').convert_alpha()
        self.rect= self.image.get_rect(topleft=pos)
        if side == 0:
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top, self.rect.width, self.rect.height * 2 // 3)

        elif side == 1:
            self.image = pg.transform.rotate(self.image, 90)
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top, self.rect.width * 2 // 3, self.rect.height)

        elif side == -2:
            self.image = pg.transform.flip(self.image, False, True)
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top + self.rect.height // 2, self.rect.width,
                                            self.rect.height * 2 // 3)

        else:
            self.image = pg.transform.rotate(self.image, 270)
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top + self.rect.height // 2, self.rect.width,
                                            self.rect.height * 2 // 3)

        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.pos = pos
        self.hitbox = True
        self.placeable_items = ALL_PICKABLE
        self.holds = None
        self.left = left
        self.right = right

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)


class TrashBin(pg.sprite.Sprite):
    def __init__(self, pos, side=0) -> None:
        super().__init__()
        self.type = Cucumber
        self.side = side
        self.image = pg.image.load('imgs/trash.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        if side == 0:

            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top, self.rect.width, self.rect.height * 2 // 3)

        elif side == 1:

            self.image = pg.transform.rotate(self.image, 90)
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top, self.rect.width * 2 // 3, self.rect.height)
        
        elif side == -2:
            self.image = pg.transform.flip(self.image, False, True)
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top + self.rect.height // 2, self.rect.width,
                                            self.rect.height * 2 // 3)

        else:
            self.image = pg.transform.flip(self.image, True, False)
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top, self.rect.width * 2 // 3, self.rect.height)

        self.pos = pos
        self.hitbox = True
        self.placeable_items = ALL_PICKABLE
        self.holds = None

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)


class BunCrate(pg.sprite.Sprite):
    def __init__(self, pos, side=0, bottom=False) -> None:
        super().__init__()
        self.type = (TopBun, BottomBun)
        self.side = side


        self.image = pg.image.load('imgs/bun_crate.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

        if side == 0:

            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top, self.rect.width, self.rect.height * 2 // 3)

        elif side == 1:

            self.image = pg.transform.rotate(self.image, 90)
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top, self.rect.width * 2 // 3, self.rect.height)
        
        elif side == -2:
            self.image = pg.transform.flip(self.image, False, True)
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top + self.rect.height // 2, self.rect.width,
                                            self.rect.height * 2 // 3)

        else:
            self.image = pg.transform.flip(self.image, True, False)
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top, self.rect.width * 2 // 3, self.rect.height)


        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.pos = pos
        self.hitbox = True

        self.placeable_items = ALL_PICKABLE
        self.holds = None
        self.bottom = False

    def get_obj(self):
        self.side = 1 if self.side != 1 else 0
        return self.type[self.side]

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)


class RiceCrate(pg.sprite.Sprite):
    def __init__(self, pos, side=0, bottom=False) -> None:
        super().__init__()
        self.type = Rice
        self.image = pg.image.load('imgs/rice_box.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)

        
        if side == 0:
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top, self.rect.width, self.rect.height * 2 // 3)

        elif side == 1:

            self.image = pg.transform.rotate(self.image, 90)
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top, self.rect.width * 2 // 3, self.rect.height)
        
        elif side == -2:
            self.image = pg.transform.flip(self.image, False, True)
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top + self.rect.height // 2, self.rect.width,
                                            self.rect.height * 2 // 3)

        else:
            self.image = pg.transform.flip(self.image, True, False)
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top, self.rect.width * 2 // 3, self.rect.height)


        self.pos = pos
        self.hitbox = True
        self.placeable_items = ALL_PICKABLE
        self.holds = None

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)


class AlgaCrate(pg.sprite.Sprite):
    def __init__(self, pos, side=0, bottom=0) -> None:
        super().__init__()
        self.type = Alga
        self.image = pg.image.load('imgs/alga_crate.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

        if side == 0:
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top, self.rect.width, self.rect.height * 2 // 3)

        elif side == 1:

            self.image = pg.transform.rotate(self.image, 90)
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top, self.rect.width * 2 // 3, self.rect.height)
        
        elif side == -2:
            self.image = pg.transform.flip(self.image, False, True)
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top + self.rect.height // 2, self.rect.width,
                                            self.rect.height * 2 // 3)

        else:
            self.image = pg.transform.flip(self.image, True, False)
            self.hitbox_rect = pg.rect.Rect(self.rect.left, self.rect.top, self.rect.width * 2 // 3, self.rect.height)

        self.side = side
        self.pos = pos
        self.hitbox = True
        self.placeable_items = ALL_PICKABLE
        self.holds = None

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)


crates = [ChikenCrate, LettuceCrate, CucumberCrate, TomatoCrate, BunCrate, RiceCrate, AlgaCrate]
