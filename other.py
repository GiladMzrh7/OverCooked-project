import pygame as pg
import time
from enteties import *

order_places = {1: [45], 2: [20, 70], 3: [20, 60, 100], 4: [20, 55, 90, 120], 5: [20, 50, 85, 120, 152]}


# This file is used to create a all of the informative sprites in the game.
# some of them will be sprite sheets,and some will be single images.

class Timer(pg.sprite.Sprite):

    # this is the timer sprite that will be used in the game.

    def __init__(self, pos, time, color=(0, 0, 0)):
        super().__init__()
        self.time = time
        self.font = pg.font.Font("fonts/Rubik-ExtraBoldItalic.ttf", 40) # timer font
        self.image = pg.image.load('imgs/clock.png').convert_alpha() # timer image

        self.red = pg.image.load('imgs/clock_last.png').convert_alpha() 
        self.norm = pg.image.load('imgs/clock.png').convert_alpha()

        self.pos = pos
        self.back = color
        self.rect = self.image.get_rect()
        self.rect.center = pos

        self.cnt = 1 # cnt to check if it is time to change the image when needed (20 sec left)
        self.update()

        self.hitbox = False # a non hitbox sprite
        self.who = False
        self.time_checker = 6 # time to check if it is time to change the image

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, self.rect) # simply drawing it on the screen

    def update(self):

        if self.cnt % 60 == 0:
            # transfering the time to minutes and rendering it
            text = self.font.render(f'{str(time.strftime("%M:%S", time.gmtime(self.time)))}', True, (255, 255, 255))
            if self.time > 18:
                self.image = self.norm.copy()

            else:
                if self.cnt % self.time_checker == 0:
                    self.image = self.red.copy() if self.who else self.norm.copy()
                    self.who = not self.who

            self.time -= 1 # decreasing by one second
            self.image.blit(text, (30, 25))
            self.cnt = 1
        else:
            self.cnt += 1

        if self.time <= -2:
            self.kill()


class Order(pg.sprite.Sprite):
    def __init__(self, ingridens):
        super().__init__()
        self.time_left = 60 * len(ingridens)
        self.org_time = self.time_left
        self.ingridens = ingridens
        self.cnt = 1
        self.hitbox = False

    #this will bring specific image from sprite sheet
    def image_at(self, rectangle:pg.Rect, colorkey=(int,int,int)):
        """
        Loads image from x,y,x+offset,y+offset to get the plate image
        input:
            rectangle: a tuple of (x, y, x+offset, y+offset)
            colorkey: the colorkey of the image(if there is)
        output:
            the image
        """
        rect = pg.Rect(rectangle)
        image = pg.Surface(rect.size).convert()
        image.blit(self.icons_pic, (0, 0), rect)
        if colorkey:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pg.RLEACCEL)
        return image

    def update(self):
        # updating the time left every second
        if not self.cnt % 60:
            self.cnt = 1
            self.time_left -= 1
        else:
            self.cnt += 1
        if self.time_left <= 0: # if the time is up the order is killed
            self.kill()

    def setup(self):
        # setting up the unpickleable objects
        self.plate_pic = pg.image.load('imgs/plates.png').convert_alpha()
        self.icons_pic = pg.image.load('imgs/ordered.png').convert_alpha()

    def draw(self, screen: pg.Surface, pos):
        x1 = pos[0] + 20
        y = pos[1] + 75

        img = pg.image.load(f'imgs/order{len(self.ingridens)}.png')
        temp_surface = pg.Surface(img.get_size()).convert_alpha()

        temp_surface.blit(img, (0, 0))

        for temp in range(len(self.ingridens)):
            image = self.image_at(icons[self.ingridens[temp]], colorkey=BLACK)
            image = pg.transform.scale(image, (27, 27))
            rect = image.get_rect(center=(order_places[len(self.ingridens)][temp], y))
            temp_surface.blit(image, rect)

        r = img.get_rect()
        s = pg.Surface((151, 100))
        s.blit(self.plate_pic, (0, 0), (*plate_kinds[tuple(self.ingridens)], 151, 100))
        s.set_colorkey(BLACK)

        s = pg.transform.scale(s, (110, 73))
        temp_surface.blit(s, (-10, 0))

        color = GREEN if self.time_left >= self.org_time * 2 / 3 else ORANGE if self.time_left >= self.org_time / 3 else RED
        pct = self.time_left / self.org_time * 100

        pg.draw.rect(temp_surface, color, (5, temp_surface.get_rect().bottom - 45, pct / 100 * img.get_rect().width, 7))

        temp_surface.set_colorkey(BLACK)

        screen.blit(temp_surface, (x1 - 10, 0))

        return x1 + r.width


class GetAway(pg.sprite.Sprite):
    def __init__(self, pos, side=0) -> None:
        super().__init__()
        self.sprite_sheet = pg.image.load('imgs/sprite.png').convert_alpha()
        self.width = 133.33
        self.height = 100
        self.index = 0
        self.image = self.get_image()
        self.rect = self.image.get_rect(topleft=(pos))
        self.hitbox = True
        self.side = side

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

    def get_image(self):
        image = pg.Surface((self.width, self.height)).convert_alpha()
        image.blit(self.sprite_sheet, (0, 0), (0, (self.height * (164 - self.index)), self.width, self.height))
        return image

    def update(self):
        self.index = self.index + 1 if self.index < 164 else 0
        self.image = self.get_image()
        if self.side == 0:
            pass

        elif self.side == 1:
            self.image = pg.transform.rotate(self.image, 90)

        else:
            self.image = pg.transform.flip(self.image, True, False)

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)


class OnFire(pg.sprite.Sprite):
    def __init__(self, pos) -> None:
        super().__init__()
        self.sprite_sheet = pg.image.load('imgs/on_fire.png')
        self.width = 100
        self.height = 100
        self.index = 0
        self.image = self.get_image()
        self.rect = self.image.get_rect(center=(pos))
        self.hitbox = False
        self.cnt = 1

    def get_image(self):
        image = pg.Surface((self.width, self.height)).convert_alpha()
        image.blit(self.sprite_sheet, (0, 0), (self.width * self.index, 0, self.width, self.height))
        image.set_colorkey(BLACK)
        return image

    def update(self):
        if self.cnt % 2 == 0:
            self.index = self.index + 1 if self.index < 55 else 0
            self.image = self.get_image()
            self.cnt = 1
        else:
            self.cnt += 1

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)


class Score_sprite(pg.sprite.Sprite):
    def __init__(self, pos) -> None:
        super().__init__()
        self.score = 0
        self.image = pg.image.load('imgs/score.png')
        self.rect = self.image.get_rect(center=pos)
        self.font = pg.font.Font('fonts/Ubuntu-Bold.ttf', 50)
        self.hitbox = False
        self.on_fire = False

        self.on_fire_sheet = OnFire(self.rect.topleft)
        self.fire_sprite = pg.image.load('imgs/score_onfire.png')

    def update_score(self, score):
        self.score += score
        if not self.on_fire and self.score > 120:
            self.on_fire = True
            self.image = self.fire_sprite

    def draw(self, screen: pg.Surface):
        if not self.on_fire:
            screen.blit(self.image, self.rect)
            text = self.font.render(str(self.score), True, BLACK)
            screen.blit(text, (self.rect.x + 140 - len(str(self.score)) * 10, self.rect.centery - 30))
        else:
            screen.blit(self.image, self.rect)
            text = self.font.render(str(self.score), True, BLACK)
            screen.blit(text, (self.rect.x + 140 - len(str(self.score)) * 10, self.rect.centery - 30))
            self.on_fire_sheet.draw(screen)
            self.on_fire_sheet.update()


class Loading(pg.sprite.Sprite):
    def __init__(self, pos) -> None:
        super().__init__()
        self.sprite_sheet = pg.image.load('imgs/loading_sprite.png')
        self.width = 16800 / 84
        self.height = 200
        self.index = 0
        self.image = self.get_image()
        self.rect = self.image.get_rect(center=(pos))
        self.hitbox = False
        self.cnt = 1

    def get_image(self):
        image = pg.Surface((self.width, self.height))
        image.fill(BLACK)
        image.blit(self.sprite_sheet, (0, 0), (self.width * self.index, 0, self.width, self.height))
        image.set_colorkey(BLACK)
        return image

    def update(self):
        self.index = self.index + 1 if self.index < 83 else 0
        self.image = self.get_image()
        self.cnt = 1

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)
