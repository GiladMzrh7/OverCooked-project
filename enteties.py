import pygame as pg
import math
from extended import *
import time

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
ANGLE_W = 10
ANGLE_H = 0.3


def rect_distance(rect1, rect2):
    x1, y1 = rect1.topleft
    x1b, y1b = rect1.bottomright
    x2, y2 = rect2.topleft
    x2b, y2b = rect2.bottomright
    left = x2b < x1
    right = x1b < x2
    top = y2b < y1
    bottom = y1b < y2
    if bottom and left:
        return math.hypot(x2b - x1, y2 - y1b)
    elif left and top:
        return math.hypot(x2b - x1, y2b - y1)
    elif top and right:
        return math.hypot(x2 - x1b, y2b - y1)
    elif right and bottom:
        return math.hypot(x2 - x1b, y2 - y1b)
    elif left:
        return x1 - x2b
    elif right:
        return x2 - x1b
    elif top:
        return y1 - y2b
    elif bottom:
        return y2 - y1b
    else:  # rectangles intersect
        return 0


# This will be the Father class of all Pickable objects
class PickableObject(pg.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()
        self.picked = None
        self.hitbox = False
        self.placed = None
        self.rotated = 0
        self.usable = [Plate, Pot, Pan]

    def update_side(self):
        if type(self) == Plate:
            return

        if self.placed:
            side = self.placed.side
            if side == 0 and self.rotated != 0:
                if type(self) in self.usable:
                    self.image = self.base_image
                    self.rotated = 0
                else:
                    self.image = self.def_image if not self.chopped else self.chopped_image
                    self.rotated = 0

            elif side == 1 and self.rotated != 1:
                self.image = pg.transform.rotate(self.image, 90)
                self.rotated = 1

            elif side == -1 and self.rotated != -1:
                self.image = pg.transform.rotate(self.image, 270)
                self.rotated = -1
        else:
            if type(self) in self.usable:
                self.image = self.base_image
                self.rotated = 0
            else:
                self.image = self.def_image if not self.chopped else self.chopped_image
                self.rotated = 0

    def update(self):
        self.update_side()
        if self.picked:
            self.pos = self.picked.pos
            x, y = self.picked.facing
            self.rect.center = self.picked.rect.center

            if x > 0:
                if y > 0:
                    self.rect.top = self.pos[1]
                elif y < 0:
                    self.rect.bottom = self.pos[1]

                else:
                    self.rect.centery = self.pos[1]

                self.rect.left = self.pos[0]

            elif x < 0:
                if y > 0:
                    self.rect.top = self.pos[1]
                elif y < 0:
                    self.rect.bottom = self.pos[1]
                else:
                    self.rect.centery = self.pos[1]

                self.rect.right = self.pos[0]

            else:
                if y > 0:
                    self.rect.top = self.pos[1]
                    self.rect.centerx = self.pos[0]
                elif y < 0:
                    self.rect.bottom = self.pos[1]
                    self.rect.centerx = self.pos[0]

        elif self.placed:
            self.rect.center = self.placed.rect.center
            if type(self) == Tomato:
                self.rect.bottom -= 10
                self.rect.left -= 10

            elif type(self) != Plate and type(self) != Lettuce and type(self) != Pot and type(
                    self) != BottomBun and type(self) != Rice:
                self.rect.bottom += 20

        self.pos = self.rect.center


# region ingridens
class Chicken(PickableObject):
    def __init__(self, pos):
        super().__init__()
        self.image = pg.image.load('imgs/c.png').convert_alpha()
        self.def_image = pg.image.load('imgs/c.png').convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.chopped = False
        self.chop_progress = 0
        self.chopped_image = pg.Surface((30, 30))

    def update(self):
        super().update()

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)
        if self.chop_progress and not self.chopped:
            color = GREEN if self.chop_progress >= 160 else ORANGE if self.chop_progress >= 80 else RED
            r = pg.Rect(self.rect.x, self.rect.y - 20, 0.25 * self.chop_progress, 10, )
            pg.draw.rect(screen, color, r)
            pg.draw.rect(screen, BLACK, pg.Rect(self.rect.x, self.rect.y - 20, 75, 12), 2)


class Cucumber(PickableObject):
    def __init__(self, pos):
        super().__init__()
        self.image = pg.image.load('imgs/cucumber.png').convert_alpha()
        self.def_image = pg.image.load('imgs/cucumber.png').convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.chopped = False
        self.chop_progress = 0
        self.chopped_image = pg.image.load('imgs/chopped_cucumber.png').convert_alpha()

    def update(self):
        super().update()

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)
        if self.chop_progress and not self.chopped:
            color = GREEN if self.chop_progress >= 160 else ORANGE if self.chop_progress >= 80 else RED
            r = pg.Rect(self.rect.x, self.rect.y - 20, 0.25 * self.chop_progress, 10, )
            pg.draw.rect(screen, color, r)
            pg.draw.rect(screen, BLACK, pg.Rect(self.rect.x, self.rect.y - 20, 75, 12), 2)


class TopBun(PickableObject):
    def __init__(self, pos) -> None:
        super().__init__()
        self.width = 84
        self.height = 84
        image = pg.Surface((self.width, self.height)).convert_alpha()
        img = pg.image.load('imgs/bun.png')

        image.blit(img, (0, 0), (0, 0, self.width, self.height))
        self.image = image

        self.rect = self.image.get_rect(center=(pos))
        self.hitbox = False
        self.chopped = True

    def draw(self, screen):
        self.image.set_colorkey(BLACK)
        screen.blit(self.image, self.rect)

    def update_side(self):
        return


class BottomBun(PickableObject):
    def __init__(self, pos) -> None:
        super().__init__()
        self.width = 84
        self.height = 84
        image = pg.Surface((self.width, self.height)).convert_alpha()
        img = pg.image.load('imgs/bun.png')
        image.blit(img, (0, 0), (self.width, 0, self.width, self.height))
        self.image = image

        self.rect = self.image.get_rect(center=(pos))
        self.hitbox = False
        self.chopped = True

    def draw(self, screen):
        self.image.set_colorkey(BLACK)
        screen.blit(self.image, self.rect)

    def update_side(self):
        return


class Lettuce(PickableObject):
    def __init__(self, pos):
        super().__init__()
        self.image = pg.image.load('imgs/lettuce.png').convert_alpha()
        self.def_image = pg.image.load('imgs/lettuce.png').convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.chopped = False
        self.chop_progress = 0
        self.chopped_image = pg.image.load('imgs/chopped_lettuce.png').convert_alpha()

    def update(self):
        super().update()

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)
        if self.chop_progress and not self.chopped:
            color = GREEN if self.chop_progress >= 160 else ORANGE if self.chop_progress >= 80 else RED
            r = pg.Rect(self.rect.x, self.rect.y - 20, 0.25 * self.chop_progress, 10, )
            pg.draw.rect(screen, color, r)
            pg.draw.rect(screen, BLACK, pg.Rect(self.rect.x, self.rect.y - 20, 75, 12), 2)


class Tomato(PickableObject):
    def __init__(self, pos):
        super().__init__()
        self.image = pg.image.load('imgs/tomato.png').convert_alpha()
        self.def_image = pg.image.load('imgs/tomato.png').convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.chopped = False
        self.chop_progress = 0
        self.chopped_image = pg.image.load('imgs/chopped_tomato.png').convert_alpha()

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)
        if self.chop_progress and not self.chopped:
            color = GREEN if self.chop_progress >= 160 else ORANGE if self.chop_progress >= 80 else RED
            r = pg.Rect(self.rect.x, self.rect.y - 20, 0.25 * self.chop_progress, 10, )
            pg.draw.rect(screen, color, r)
            pg.draw.rect(screen, BLACK, pg.Rect(self.rect.x, self.rect.y - 20, 75, 12), 2)

    def update(self):
        super().update()


class Fish(PickableObject):
    def __init__(self, pos) -> None:
        super().__init__()
        self.image = pg.image.load('imgs/fish.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)

        self.hitbox = False
        self.chopped = False
        self.chop_progress = 0
        self.chopped_image = pg.image.load('imgs/chopped_fish.png').convert_alpha()

    def update(self):
        super().update()

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        if self.chop_progress and not self.chopped:
            color = GREEN if self.chop_progress >= 160 else ORANGE if self.chop_progress >= 80 else RED
            r = pg.Rect(self.rect.x, self.rect.y - 20, 0.25 * self.chop_progress, 10, )
            pg.draw.rect(screen, color, r)
            pg.draw.rect(screen, BLACK, pg.Rect(self.rect.x, self.rect.y - 20, 75, 12), 2)


class Rice(PickableObject):
    def __init__(self, pos) -> None:
        super().__init__()
        self.image = pg.image.load('imgs/rice.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.hitbox = False
        self.rect.topleft = pos

        self.cooked = False
        self.cook_progress = 0

    def update_side(self):
        return

    def draw(self, screen):
        if not self.placed:
            screen.blit(self.image, self.rect)
        elif type(self.placed) == Pot:
            if self.cook_progress and not self.cooked:
                color = GREEN if self.cook_progress >= 160 else ORANGE if self.cook_progress >= 80 else RED
                r = pg.Rect(self.rect.x + 5, self.rect.y - 20, 0.25 * self.cook_progress, 10, )
                pg.draw.rect(screen, color, r)
                pg.draw.rect(screen, BLACK, pg.Rect(self.rect.x + 5, self.rect.y - 20, 75, 12), 2)
            elif self.cooked:
                pg.draw.circle(screen, GREEN, (self.rect.x + self.rect.width / 2 - 7.5, self.rect.y - 15), 8)
        else:
            screen.blit(self.image, self.rect)


class Alga(PickableObject):
    def __init__(self, pos):
        super().__init__()
        self.image = pg.image.load('imgs/alga.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = False
        self.chopped = True
        self.chop_progress = 300

    def update_side(self):
        return

    def draw(self, screen):
        screen.blit(self.image, self.rect)


# will have to be chopped before cooked
class Potato(PickableObject):
    def __init__(self, pos) -> None:
        super().__init__()
        self.image = pg.image.load('imgs/potato.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = False
        self.chopped = False
        self.chop_progress = 0
        self.chopped_image = pg.image.load('imgs/chopped_potato.png').convert_alpha()

        self.cooked = False
        self.cook_progress = 0

    def update(self):
        return super().update()

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        if self.chop_progress and not self.chopped:
            color = GREEN if self.chop_progress >= 160 else ORANGE if self.chop_progress >= 80 else RED
            r = pg.Rect(self.rect.x, self.rect.y - 20, 0.25 * self.chop_progress, 10, )
            pg.draw.rect(screen, color, r)
            pg.draw.rect(screen, BLACK, pg.Rect(self.rect.x, self.rect.y - 20, 75, 12), 2)

        elif self.cook_progress and not self.cooked and self.chopped:
            color = GREEN if self.cook_progress >= 160 else ORANGE if self.cook_progress >= 80 else RED
            r = pg.Rect(self.rect.x, self.rect.y - 20, 0.25 * self.cook_progress, 10, )
            pg.draw.rect(screen, color, r)
            pg.draw.rect(screen, BLACK, pg.Rect(self.rect.x, self.rect.y - 20, 75, 12), 2)


# endregion

choppable = [Cucumber, Tomato, Lettuce, Potato, Chicken, Alga]
cookable = [Potato, Rice]

icons = {Tomato: (0, 0, 60, 60), Lettuce: (162, 0, 64, 85), TopBun: (240, 0, 87, 87), BottomBun: (240 + 90, 0, 87, 87),
        Cucumber: (60, 0, 89, 109), 
        Rice: (240 + 190, 0, 87, 50), Potato: (240 + 40, 0, 87, 87), Chicken: (240 + 360, 0, 87, 87),
        Alga: (240 + 285, 0, 88, 100)}
        
plate_kinds = {
    (): (0, 0),
    tuple([Tomato]): (302, 0), tuple([Cucumber]): (151, 0), tuple([Cucumber, Tomato]): (604, 0),
    tuple([Lettuce, Tomato]): (906, 0), tuple([Cucumber, Lettuce]): (755, 0), tuple([Lettuce]): (453, 0),
    tuple([Cucumber, Lettuce, Tomato]): (1057, 0),

    tuple([BottomBun]): (1208, 0), tuple([BottomBun, Tomato]): (1661, 0), tuple([BottomBun, Lettuce]): (1612, 0),
    tuple([BottomBun, Lettuce]): (1510, 0),
    tuple([BottomBun, Tomato]): (1661, 0), tuple([BottomBun, Cucumber]): (1359, 0),
    tuple([BottomBun, Cucumber, Tomato]): (1963, 0),
    tuple([BottomBun, Lettuce, Tomato]): (1812, 0),
    tuple([BottomBun, Cucumber, Lettuce]): (2114, 0), tuple([BottomBun, Cucumber, Lettuce, Tomato]): (2265, 0),

    tuple([BottomBun, Cucumber, TopBun]): (2416, 0), tuple([BottomBun, Tomato, TopBun]): (2567, 0),
    tuple([BottomBun, Lettuce, TopBun]): (2718, 0), tuple([BottomBun, Cucumber, Tomato, TopBun]): (2869, 0),
    tuple([BottomBun, Lettuce, Tomato, TopBun]): (3020, 0), tuple([BottomBun, Cucumber, Lettuce, TopBun]): (3171, 0),
    tuple([BottomBun, Cucumber, Lettuce, Tomato, TopBun]): (3322, 0),
    tuple([Rice]): (3322 + 151, 0), tuple([Alga]): (3322 + 302, 0),

}

pot_kinds = {Rice: 'imgs/rice_pot.png'}


class Plate(PickableObject):
    def __init__(self, pos):
        super().__init__()
        self.def_image = pg.image.load('imgs/plate.png').convert_alpha()
        self.pos = pos
        self.already = []

        self.icons = pg.image.load('imgs/ordered.png').convert_alpha()
        image = pg.Surface((151, 100))
        mg = pg.image.load('imgs/plates.png')
        image.blit(mg, (0, 0), (*plate_kinds[tuple(self.already)], 151, 100))
        image.set_colorkey(BLACK)
        # self.image= image
        self.image = self.def_image
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

    def reset(self):
        self.image = pg.image.load('imgs/plate.png').convert_alpha()
        self.def_image = pg.image.load('imgs/plate.png').convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        self.already = []

    def image_at(self, rectangle, colorkey=None):
        rect = pg.Rect(rectangle)
        image = pg.Surface(rect.size).convert()
        image.blit(self.icons, (0, 0), rect)
        if colorkey:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pg.RLEACCEL)
        return image

    def trash(self):
        self.reset()

    def place_frompot(self, pot):
        c = pot.already
        if type(c) not in cookable and type(c) not in choppable:
            return

        self.already.append(type(c))
        self.already = sorted(self.already, key=lambda x: x.__name__)
        pot.already = None
        c.kill()
        if tuple(self.already) in plate_kinds:
            image = pg.Surface((151, 100))
            mg = pg.image.load('imgs/plates.png')
            image.blit(mg, (0, 0), (*plate_kinds[tuple(self.already)], 151, 100))
            image.set_colorkey(BLACK)
            self.image = image

    def place(self, pl):
        if type(pl.holds) == Plate:
            return
            
        c = pl.holds

        self.already.append(type(c))
        self.already = sorted(self.already, key=lambda x: x.__name__)
        pl.holds = None
        c.kill()
        if tuple(self.already) in plate_kinds:
            image = pg.Surface((151, 100))
            mg = pg.image.load('imgs/plates.png')
            image.blit(mg, (0, 0), (*plate_kinds[tuple(self.already)], 151, 100))
            image.set_colorkey(BLACK)
            self.image = image

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)
        if (len(self.already)) > 0:
            x = self.rect.width / (len(self.already) + 1)
            x += self.rect.left - self.rect.width // 4
            y = self.rect.top
            for s in self.already:
                image = self.image_at(icons[s], BLACK)
                image = pg.transform.scale(image, (27, 25))
                d = pg.draw.circle(screen, WHITE, (x + 30, y), 15)
                screen.blit(image, d.topleft)
                x += 40

    def place_from_crate(self, crate):
        c = crate.holds

        self.already.append(type(c))
        self.already = sorted(self.already, key=lambda x: x.__name__)
        crate.already = None
        c.kill()
        if tuple(self.already) in plate_kinds:
            image = pg.Surface((151, 100))
            mg = pg.image.load('imgs/plates.png')
            image.blit(mg, (0, 0), (*plate_kinds[tuple(self.already)], 151, 100))
            image.set_colorkey(BLACK)
            self.image = image

    def update(self):
        return super().update()


class Pot(PickableObject):
    def __init__(self, pos) -> None:
        super().__init__()
        self.image = pg.image.load('imgs/pot.png')
        self.rect = self.image.get_rect(topleft=pos)
        self.pos = pos
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.already = []

    def reset(self):
        self.image = pg.image.load('imgs/pot.png').convert_alpha()
        self.def_image = pg.image.load('imgs/pot.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        self.already = None

    def trash(self):
        if self.already:
            self.already.kill()

        self.reset()

    def place(self, pl):
        c = pl.holds
        if not self.already:
            self.already = c
            pl.holds = None
            c.placed = self
            c.picked = None
            if type(self.already) in pot_kinds:
                self.image = pg.image.load(pot_kinds[type(self.already)]).convert_alpha()

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)
        if self.already:
            x = self.rect.width / 2
            x += self.rect.left - self.rect.width // 4
            y = self.rect.top
            image = type(self.already)((0, 0)).image
            image = pg.transform.scale(image, (27, 25))
            d = pg.draw.circle(screen, WHITE, (x + 30, y - 25), 15)
            screen.blit(image, d.topleft)

    def update_side(self):
        return

    def update(self):
        return super().update()


class Pan(PickableObject):
    def __init__(self, pos, side=0) -> None:
        super().__init__()
        self.image = pg.image.load('imgs/pan.png')
        self.base_image = pg.image.load('imgs/pan.png')

        self.rect = self.image.get_rect(topleft=pos)
        self.pos = pos
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.already = []
        self.side = side
        if side == 0:
            self.image = pg.image.load('imgs/pan.png').convert_alpha()

        elif side == 1:
            self.image = pg.image.load('imgs/pan.png').convert_alpha()
            self.image = pg.transform.rotate(self.image, 90)

        else:
            self.image = pg.image.load('imgs/pan.png').convert_alpha()
            self.image = pg.transform.flip(self.image, True, False)

    def reset(self):
        self.image = pg.image.load('imgs/pan.png').convert_alpha()
        self.def_image = pg.image.load('imgs/pan.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        self.already = []

    def place(self, pl):
        c = pl.holds
        self.already.append(type(c))
        self.already = sorted(self.already, key=lambda x: x.__name__)
        pl.holds = None
        c.kill()
        if tuple(self.already) in plate_kinds:
            self.image = pg.image.load(f'imgs/pot.png')

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)
        if (len(self.already)) > 0:
            x = self.rect.width / (len(self.already) + 1)
            x += self.rect.left - self.rect.width // 4
            y = self.rect.top
            for s in self.already:
                image = s((0, 0)).image
                image = pg.transform.scale(image, (27, 25))
                d = pg.draw.circle(screen, WHITE, (x + 30, y), 15)
                screen.blit(image, d.topleft)
                x += 40

    def update(self):
        return super().update()


ALL_INGRIDENS = [Chicken, Lettuce, Cucumber, Tomato, TopBun, BottomBun, Potato, Rice, Alga]
ALL_TOOLS = [Plate, Pot, Pan]
ALL_PICKABLE = ALL_INGRIDENS + ALL_TOOLS
