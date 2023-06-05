from turtle import pen
from enteties import *
from extended import *
from hitbox import *
from other import *

# here is where the magic happens


class Player(pg.sprite.Sprite):

    # This class is used to create the player.
    # it will represent any of the players that are in the game.

    def __init__(self, father: Player_Father):
        super().__init__()
        # father is the data got by the server
        # couldn't inherit because can't pickle sprite

        self.pos = father.pos 
        self.width = father.width 
        self.height = father.height
        self.image = pg.Surface((25, 100)) #TODO: change this to a sprite
        self.rect = self.image.get_rect()
        self.rect.center = father.pos
        self.directon = father.directon
        self.speed = father.speed
        self.holds = father.holds
        self.group = father.group
        self.hitbox = False
        self.last_d = pg.math.Vector2() # last direction of the player 
        self.facing = (0, 0) # facing direction of the player
        self.name = father.name # username of the player

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)

    def take_from(self, c:pg.sprite.Sprite):
        """
        This function is used to take a PickableObject from a hitboxed sprite.
        :param c: the sprite to take from
        """
        p = c.holds
        # if the object didn't finish cooking or chopping it cannot be picked up
        if type(p) in choppable or type(p) in cookable:
            if type(p) in choppable:
                if p.chop_progress > 0 and p.chop_progress < 299:
                    return
            else:
                if p.cook_progress > 0 and p.cook_progress < 299:
                    return

        c.holds = None
        p.picked = self
        self.holds = p
        if p.placed:
            p.placed.holds = None
        p.placed = None
        self.directon.y = -1

    def handle_create(self, c):
        """
        this function is used to take a PickableObject from his Crate
        from example: to take a cucumber from the cucumber crate
        :param c: the crate to take from
        """
        if c.holds:
            p = c.holds
            c.holds = None
            p.picked = self
            self.holds = p
            if p.placed:
                p.placed.holds = None
            p.placed = None
            self.directon.y = -1

        else:
            if type(c) != BunCrate:
                self.holds = c.type(self.pos)
            else:
                if type(c) == BunCrate:
                    self.holds = c.get_obj()(self.pos)
                else:
                    self.holds = c.type(c.bottom, self.pos)
                    c.bottom = not c.bottom
            self.group.add(self.holds)
            self.holds.picked = self

    def pick_up(self, c:PickableObject):
        """
        This function is used to pick up a PickableObject.
        :param c: the PickableObject to pick up
        """
        c.picked = self
        self.holds = c

        if c.placed:
            c.placed.holds = None

        c.placed = None

    def set_direction(self, x, y):
        self.directon.x = x
        self.directon.y = y

    def input(self):
        """
        This function is used to handle the input of the player.
        it will get all pressed keys, and move the player accordingly
        """
        keys = pg.key.get_pressed()
        moved = False
        if keys[pg.K_e] or keys[pg.K_f]:
            self.directon.x = 0
            self.directon.y = 0
            return True

        if keys[pg.K_w] or keys[pg.K_UP]:
            self.directon.y = -1
            moved = True

        elif keys[pg.K_s] or keys[pg.K_DOWN]:
            self.directon.y = 1
            moved = True
        else:

            self.directon.y = 0

        if keys[pg.K_d] or keys[pg.K_RIGHT]:
            self.directon.x = 1
            moved = True
        elif keys[pg.K_a] or keys[pg.K_LEFT]:
            self.directon.x = -1
            moved = True
        else:
            self.directon.x = 0

        if (self.directon.x > 0 or self.directon.x < 0) or (self.directon.y > 0 or self.directon.y < 0):
            self.facing = self.directon.xy

        self.check_collision()
        return moved

    def let_go(self, sprite: pg.sprite.Sprite):
        """
        This function is used to let go of a PickableObject.
        :param sprite: the closest hitboxed sprite to the player that the distance between them is smaller than 20
        """
        c: PickableObject = self.holds
        c.picked = None
        if not sprite:
            self.holds = None
            return

        if sprite.hitbox and type(c) in sprite.placeable_items:
            if sprite.rect.colliderect(c.rect) and not sprite.holds:
                sprite.holds = c
                c.placed = sprite
                c.update_side()

        self.holds = None

    def check_collision(self):
        """
        This function is used to check if the player is colliding with a hitboxed sprite.
        """

        hit = [s for s in self.group.sprites() if s != self and s.hitbox and self.rect.colliderect(s.hitbox_rect)]

        l = list(self.pos)

        if hit:
            for collision in hit:
                if self.directon.x > 0:
                    self.directon.x = 0
                    l[0] -= 7
                elif self.directon.x < 0:
                    self.directon.x = 0
                    l[0] += 7

            for collision in hit:
                if self.directon.y > 0:
                    self.directon.y = 0
                    l[1] -= 7
                elif self.directon.y < 0:
                    self.directon.y = 0
                    l[1] += 7
            self.rect.center = tuple(l)

    def serve(self, level):
        """
        this function is used to serve the plate to the order that belongs to her
        :param level: the level that the player is in
        """
        if not self.holds:
            return

        if type(self.holds) != Plate:
            return

        orde = next((x for x in level.orders if x.ingridens == self.holds.already), None)
        if orde != None:
            self.holds.kill()
            level.score.update_score(int(orde.time_left * 0.1))
            orde.kill()
            level.orders.remove(orde)
            level.group.add(Plate((300, 150)))
            self.holds = None
            return 'served'

        else:
            self.holds.kill()
            if level.score.score > 20:
                level.score.update_score(-20)

            else:
                level.score.score = 0

            level.group.add(Plate((300, 150)))
            self.holds = None
            return 'nope'

    def trash(self):
        """
        this function is used to delete the PickableObject that the player is holding
        or if it is a tool to clean it
        """
        if type(self.holds) in ALL_TOOLS:
            self.holds.trash()
            self.holds.picked = self
        else:
            self.holds.kill()
            self.holds = None
        return 'trash'

    def handle_e(self, level):
        """
        this function is used to handle all the input of the player when the e key is pressed
        :param level: the level that the player is in
        """

        dest, c = level.get_closest_sprite(self)

        if dest > 5:
            if self.holds:
                self.let_go(None)
                return 'drop'

        if type(c).__base__ == PickableObject and not c.hitbox and not self.holds:
            self.pick_up(c)
            return 'pick'

        elif type(c) == TrashBin and self.holds:
            if self.holds:
                return self.trash()

        elif type(c) == GetAway:
            return self.serve(level)

        elif c.hitbox and type(c.holds) in ALL_TOOLS and self.holds:
            if type(c.holds) == Pot and type(self.holds) in cookable:
                c.holds.place(self)
                self.holds = None
                return 'plate'

            if type(self.holds) in choppable:
                if self.holds.chopped and type(self.holds) not in c.holds.already:
                    c.holds.place(self)
                    self.holds = None
                    return 'plate'
            elif type(self.holds) in cookable:
                if self.holds.cooked and type(self.holds) not in c.holds.already:
                    c.holds.place(self)
                    self.holds = None
                    return 'plate'
            elif type(self.holds) == TopBun or type(self.holds) == BottomBun:
                c.holds.place(self)
                self.holds = None
                return 'plate'

            elif type(self.holds) == Pot and self.holds.already:
                c.holds.place_frompot(self.holds)
                self.holds.reset()
                return 'plate'

            else:
                c.holds.place(self)
                self.holds = None
                return 'plate'

        elif type(c) == Plate and c.placed:
           
            if type(self.holds) in choppable:
                if self.holds.chopped and type(self.holds) not in c.already:
                    c.place(self)
                    self.holds = None
                    return 'plate'
            elif type(self.holds) in cookable:

                if self.holds.cooked and type(self.holds) not in c.already:
                    c.place(self)
                    self.holds = None
                    return 'plate'
            
            elif type(self.holds) == TopBun or type(self.holds) == BottomBun:
                    c.place(self)
                    self.holds = None
                    return 'plate'

        elif type(c) == Pot and c.placed and self.holds:
            if type(c) == Pot and type(self.holds) in cookable:
                c.place(self)
                self.holds = None
                return 'plate'

        elif c.hitbox and type(c.holds) in ALL_INGRIDENS and type(self.holds) == Plate:
            pl: Plate = self.holds
            if type(c.holds) in choppable:
                if c.holds.chopped and type(c.holds) not in pl.already:
                    pl.place_from_crate(c)
                    pl.picked = None
                    pl.placed = c
                    c.holds = pl
                    self.holds = None

                    return 'plate'
            elif type(self.holds) in cookable:
                if c.holds.cooked and type(c.holds) not in pl.already:
                    pl.place_from_crate(c)
                    pl.picked = None
                    pl.placed = c
                    self.holds = None
                    c.holds
                    return 'plate'

            else:
                self.let_go(None)
                return 'drop'


        elif c.hitbox and c.holds and not self.holds:
            self.take_from(c)
            return 'pick'

        elif c.hitbox and type(c) in crates and not self.holds:
            self.handle_create(c)
            return 'pick'

        else:
            if self.holds:
                self.let_go(c)
                return 'drop'

    def handle_f(self, level):
        """
        this function is used to handle all the input of the player when the f key is pressed
        """
        dest, c = level.get_closest_sprite(self)
        cut = False
        if dest > 5 or type(c) == GetAway:
            return

        if type(c).__base__ == PickableObject:
            return

        p = c.holds
        if not p or not c.hitbox:
            return

        if type(c) == CuttingTable and not p.chopped:
            p.chop_progress += 3
            cut = True

        else:
            p.chop_progress = 0

        if p.chop_progress >= 300 and not p.chopped:
            p.chopped = True
            p.image = p.chopped_image
            cut = True

        return cut and p.chop_progress % 32 == 0

    def update(self):
        """
        this function is used to update the player sprite
        """
        self.rect.center += self.directon * self.speed
        self.pos = self.rect.center
        self.check_collision()


class Camera(pg.sprite.Group):
    def __init__(self, screen):
        super().__init__()
        self.screen = screen
        self.offset = pg.math.Vector2()
        self.half_w = self.screen.get_size()[0] / 2
        self.half_h = self.screen.get_size()[1] / 2
        self.font = pg.font.Font('fonts/Oxygen-Bold.ttf', 15)

    def draw(self, me, pl, background=None, close=None):

        if background:
            self.screen.blit(background.image, background.rect)

        if close and type(close).__base__ == PickableObject:
            if close.placed:
                close = close.placed
            else:
                close = None

        mini = min(pl, key=lambda x: x.rect.bottom)
        orders_cache = []
        drawn = []
        a = list(filter(lambda x: type(x) != Order and x.rect.bottom < mini.rect.bottom and x not in pl and x.hitbox,
                        self.sprites()))
        hitbox = list(filter(lambda x: x not in a and x not in pl and x.hitbox, self.sprites()))
        b = list(filter(lambda x: x not in a and x not in pl and not x in hitbox, self.sprites()))

        for sprite in a:

            if type(sprite) == GetAway:
                sprite.draw(self.screen)
            else:
                if close and close == sprite:
                    im = sprite.image.copy()
                    im.fill((80, 80, 80), special_flags=pg.BLEND_RGB_ADD)
                    self.screen.blit(im, sprite.rect)

                else:
                    sprite.draw(self.screen)

                if sprite.holds:
                    sprite.holds.draw(self.screen)
                    drawn.append(sprite.holds)

        draw = None
        for x in pl:
            if x.facing[1] > 0:
                x.draw(self.screen)
                if x.holds:
                    draw = x.holds
            else:
                if x.holds:
                    x.holds.draw(self.screen)
                    drawn.append(x.holds)
                x.draw(self.screen)

            nam = self.font.render(x.name, True, WHITE)
            self.screen.blit(nam, nam.get_rect(centerx=x.rect.centerx, bottom=x.rect.top - 20))

        for sprite in hitbox:
            if type(sprite) == GetAway:
                sprite.draw(self.screen)
            else:
                if close and close == sprite:
                    im = sprite.image.copy()
                    im.fill((80, 80, 80), special_flags=pg.BLEND_RGB_ADD)
                    self.screen.blit(im, sprite.rect)
                else:
                    sprite.draw(self.screen)

        if draw:
            draw.draw(self.screen)
            drawn.append(draw)

        for sprite in b:
            if sprite in drawn:
                continue
            if type(sprite) == Order:
                orders_cache.append(sprite)
            else:
                sprite.draw(self.screen)

        x_pos, y_pos = 20, 20
        for x in orders_cache:
            x_pos = x.draw(self.screen, (x_pos, y_pos))
            x_pos += 10
