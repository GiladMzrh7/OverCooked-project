from distutils.log import error
from typing import Tuple
from camera import *
from hitbox import *
import pygame as pg
from enteties import *
from TcpEncryptedSocket import EncSocket
import string
from socket import timeout
import pickle
from other import *
import ctypes
from itertools import repeat
from typing import Tuple


# this will change the icon on the windows taskbar
myappid = 'mycompany.myproduct.subproduct.version'  # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

sock = EncSocket(("127.0.0.1", 51876), protocol=EncSocket.dh_aes)
sock.connect()

WIDTH, HEIGHT = 1280, 720
RED = (255, 0, 0)
BLACK = (0, 0, 0)

USER = None  # the name of the user the client is playing with

TAV_MAFRID = "#@@!?#%@"  # the string that splits messages in the protocol

clock = pg.time.Clock()
pg.init()
org_screen = pg.display.set_mode((WIDTH, HEIGHT), pg.DOUBLEBUF)
screen = pg.Surface((WIDTH, HEIGHT))

LEFT_BUTTON = 1
color_inactive = pg.Color('lightskyblue3')
color_active = pg.Color('dodgerblue2')

# region game icons and names
pg.mixer.init()
#pg.mixer.music.load('audio/back.wav')
#pg.mixer.music.play()
pg.display.set_icon(pg.image.load('imgs/trans_icon.png'))
pg.display.set_caption("DrChef", 'imgs/trans_icon.png')
# endregion

# the extended errors will be handled here
error_codes = {
    "Bad game code": 'The code you have entered is incorrect\nplease enter a correct one\nor create a new game',
}

# game code the player currently playing
CODE = None

# this will be the offset we will be drawing the screen to the orginal screen(org_screen)
offset = repeat((0, 0))


# this method will change the offset of screen drawing which will cause shake effect
def shake() -> Tuple[int, int]:
    s = -2
    for _ in range(0, 6):
        for x in range(0, 40, 5):
            yield (x * s, 0)
        for x in range(40, 0, 5):
            yield (x * s, 0)
        s *= -1
    while True:
        yield (0, 0)


# this method shows fadeout animation to screen
def fadeout(color:Tuple[int, int, int]=BLACK):
    fdout = pg.Surface((WIDTH, HEIGHT))
    fdout = fdout.convert()
    sub = screen.copy()
    fdout.fill(color)
    for i in range(255):
        screen.blit(sub, (0, 0))
        fdout.set_alpha(i)
        screen.blit(fdout, (0, 0))
        pg.display.flip()


# this method shows fadin animation to screen
def fadein(color:Tuple[int, int, int]=BLACK, start:int=255, shke:bool=False):
    global offset
    fdout = pg.Surface((WIDTH, HEIGHT))
    fdout = fdout.convert()
    sub = screen.copy()  # copies the last screen so we can fade it out
    fdout.fill(color)

    for i in range(start):
        screen.blit(sub, (0, 0))
        fdout.set_alpha(start - i)
        # fill the screen with the fadeout image

        a = next(offset)
        if shke and i == 3:
            offset = shake()
            # if shaking we change the offset to blit

        screen.blit(fdout, (0, 0))
        org_screen.blit(screen, a)
        pg.display.flip()


# this method is used to handle the effects the user sees when he/she is playing by string returned from player handles
# input:
#   s: the string that will be handled
#   chn: the channel that the sound will be played on
def handle_effects(s:str, chn:int):
    """
    :param s: the string that will be handled
    :param chn: the channel that the sound will be played on
    :return: audio to the screen by the string handled
    """

    if s == 'trash':
        pg.mixer.Channel(chn).play(pg.mixer.Sound('audio/trash.wav'))

    elif s == 'pick':
        pg.mixer.Channel(chn).play(pg.mixer.Sound('audio/pick.wav'))

    elif s == 'drop':
        pg.mixer.Channel(chn).play(pg.mixer.Sound('audio/drop.wav'))

    elif s == 'plate':
        pg.mixer.Channel(chn).play(pg.mixer.Sound('audio/plate.wav'))

    elif s == 'served':
        pg.mixer.Channel(chn).play(pg.mixer.Sound('audio/serve.mp3'))

    elif s == 'nope':
        pg.mixer.Channel(chn).play(pg.mixer.Sound('audio/fail.mp3'))
        global offset
        fadein(RED, 150, True)


# method that will return the distance between two rects
# input:
# rect1: first rect
# rect2: second rect
# output: distance between the two rects
def rect_distance(rect1: pg.Rect, rect2:pg.Rect) -> int:
    """
    :param rect1: first rect
    :param rect2: second rect
    :return: distance between the two rects
    """
    x1, y1 = rect1.topleft
    x1b, y1b = rect1.bottomright
    x2, y2 = rect2.topleft

    x2b, y2b = rect2.bottomright
    left = x2b < x1
    right = x1b < x2
    top = y2b < y1
    bottom = y1b < y2

    if bottom and left:
        return math.hypot(x2b - x1, y2 - y1b) # function returns the square root of the sum of squares of its arguments

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
        return 0.


# this method will hanle the login/register screen
def main_menu() -> Tuple[int,str]:
    login_button = pg.image.load('imgs/login_button.png')
    login_on = login_button.copy()
    login_on.fill((100, 100, 100), special_flags=pg.BLEND_MULT)
    log_img = login_button
    log_rect = login_button.get_rect(center=(WIDTH / 4, 500))

    register_button = pg.image.load('imgs/register_button.png')
    register_on = register_button.copy()
    register_on.fill((100, 100, 100), special_flags=pg.BLEND_MULT)
    reg_img = register_button
    reg_rect = register_button.get_rect(center=(WIDTH * 3 / 4, 500))

    img = pg.image.load('imgs/trans_icon.png')
    img_Rect = img.get_rect(center=(WIDTH / 2, 250))
    while True:
        screen.fill((128, 128, 128))
        screen.blit(log_img, log_rect)
        screen.blit(reg_img, reg_rect)
        screen.blit(img, img_Rect)
        org_screen.blit(screen, (0, 0))

        for event in pg.event.get():
            if event.type == pg.MOUSEMOTION:
                log_img = login_on if log_rect.collidepoint(pg.mouse.get_pos()) else login_button
                reg_img = register_on if reg_rect.collidepoint(pg.mouse.get_pos()) else register_button

            elif event.type == pg.QUIT:
                return -2, False

            elif event.type == pg.MOUSEBUTTONDOWN:
                if log_rect.collidepoint(pg.mouse.get_pos()):
                    return 0, False

                elif reg_rect.collidepoint(pg.mouse.get_pos()):
                    return -3, False

        clock.tick(60)
        pg.display.flip()


# this method will handle the main screen of the game after login
def after_login() -> Tuple[int,str]:
    # pg.mixer.Channel(0).play(pg.mixer.Sound('audio\song.wav'))
    global USER

    # loading images
    create_button_off = pg.image.load('imgs/create_button.png').convert_alpha()
    create_button_on = pg.image.load('imgs/create_button_on.png').convert_alpha()

    join_button_off = pg.image.load('imgs/join_button.png').convert_alpha()
    join_button_on = pg.image.load('imgs/join_button_on.png').convert_alpha()

    logout = pg.image.load('imgs/logout.png').convert_alpha()
    logout_on = logout.copy()
    logout_on.fill((100, 100, 100), None, pg.BLEND_RGBA_MULT)
    logout_rect = logout.get_rect(topleft=(15, 15))
    out_img = logout

    create_image = create_button_off
    create_image_rect = create_image.get_rect(center=(WIDTH / 4, 500))

    join_image = join_button_off
    join_image_rect = join_image.get_rect(center=(WIDTH * 3 / 4, 500))

    screen.fill((128, 128, 128))
    was = join_image

    x, y = pg.mouse.get_pos()
    create_image = create_button_on if create_image_rect.collidepoint((x, y)) else create_button_off
    screen.blit(create_image, create_image_rect)

    join_image = join_button_on if join_image_rect.collidepoint((x, y)) else join_button_off

    out_img = logout_on if logout_rect.collidepoint((x, y)) else logout

    screen.blit(join_image, join_image_rect)
    pg.display.flip()
    fadein()

    while True:
        screen.fill((128, 128, 128))
        screen.blit(out_img, logout_rect)
        x, y = pg.mouse.get_pos()
        was = create_image
        create_image = create_button_on if create_image_rect.collidepoint((x, y)) else create_button_off
        screen.blit(create_image, create_image_rect)
        screen.blit(join_image, join_image_rect)

        org_screen.blit(screen, (0, 0))

        # handle sfx if mouse over button
        if create_image == create_button_on and was == create_button_off:
            pg.mixer.music.load('audio/click.wav')
            pg.mixer.music.play()

        was = out_img
        out_img = logout_on if logout_rect.collidepoint((x, y)) else logout
        if out_img == logout_on and was == logout:
            pg.mixer.music.load('audio/click.wav')
            pg.mixer.music.play()

        was = join_image
        join_image = join_button_on if join_image_rect.collidepoint((x, y)) else join_button_off
        if join_image == join_button_on and was == join_button_off:
            pg.mixer.music.load('audio/click.wav')
            pg.mixer.music.play()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return -2, False

            if event.type == pg.MOUSEBUTTONDOWN and event.button == LEFT_BUTTON:
                if create_image_rect.collidepoint(pg.mouse.get_pos()):
                    sock.send('CREATE', "a", USER)
                    return 2, False

                elif join_image_rect.collidepoint(pg.mouse.get_pos()):
                    return 3, False

                if logout_rect.collidepoint(pg.mouse.get_pos()):
                    USER = None
                    return -4, False  # logout

        clock.tick(60)
        pg.display.flip()


# this method will handle login screen
def login() -> Tuple[int,str]:
    global USER

    # region loading images
    font = pg.font.SysFont('Verdana', 20)
    name_data = 'username:'
    name_rect = pg.rect.Rect(500, 360, 180, 32)
    name_rect.centerx = 640
    name_active = False

    pass_data = 'password:'
    pass_rect = pg.rect.Rect(500, 400, 180, 32)
    pass_rect.centerx = 640
    pass_active = False

    home_button = pg.image.load('imgs/home_button.png')
    home_on = home_button.copy()
    home_on.fill((100, 100, 100), special_flags=pg.BLEND_MULT)
    home_img = home_button
    home_rect = home_button.get_rect(center=(40, 40))

    name_text = font.render(name_data, True, (50, 50, 50))
    pass_text = font.render(pass_data, True, (50, 50, 50))

    img = pg.image.load('imgs/trans_icon.png')
    img_Rect = img.get_rect(center=(WIDTH / 2, 150))
    #endregion loading images

    # region FadeIn
    screen.fill((128, 128, 128))

    pg.draw.rect(screen, color_active if name_active else color_inactive, name_rect, border_radius=10)
    pg.draw.rect(screen, color_active if pass_active else color_inactive, pass_rect, border_radius=10)

    screen.blit(name_text, name_rect)
    screen.blit(pass_text, pass_rect)
    screen.blit(home_img, home_rect)
    screen.blit(img, img_Rect)

    pg.display.flip()
    fadein()
    # endregion Fadein

    # region login button
    login_button = pg.image.load('imgs/login_button.png').convert_alpha()
    login_button_rect = login_button.get_rect(center=(640, 540))
    darken_login = login_button.copy()
    darken_login.set_colorkey(WHITE)
    darken_login.fill((120, 120, 120), special_flags=pg.BLEND_RGBA_MULT)

    image = login_button
    was = login_button
    # endregion login

    cnt = 1
    sent = False
    error = None
    error_font = pg.font.Font('fonts/VarelaRound-Regular.ttf', 20)
    while True:
        screen.fill((128, 128, 128))
        screen.blit(image, login_button_rect)

        pg.draw.rect(screen, color_active if name_active else color_inactive, name_rect, border_radius=10)
        pg.draw.rect(screen, color_active if pass_active else color_inactive, pass_rect, border_radius=10)
        screen.blit(img, img_Rect)
        screen.blit(name_text, name_rect)
        screen.blit(pass_text, pass_rect)
        screen.blit(home_img, home_rect)

        if error:
            rec = error.get_rect(center=(640, 460))
            screen.blit(error, rec)

        org_screen.blit(screen, (0, 0))
        if sent:
            try:
                cmd, data = sock.timed_recieve()

                if cmd.decode() == 'SUCCESS':
                    USER = name_data
                    return 1, data

                else:
                    error = error_font.render(data.decode(), True, (255, 0, 0))
                    sent = False

            except timeout:
                pass

        for event in pg.event.get():

            image = darken_login if login_button_rect.collidepoint(pg.mouse.get_pos()) else login_button
            if image == darken_login and was == login_button:
                pg.mixer.music.load('audio/click.wav')
                pg.mixer.music.play()
            was = image

            if event.type == pg.QUIT:
                return -2, False

            elif event.type == pg.MOUSEBUTTONDOWN and event.button == LEFT_BUTTON:
                mouse_pos = pg.mouse.get_pos()
                if login_button_rect.collidepoint(mouse_pos):
                    sock.send('LOGIN', name_data, pass_data)
                    error = None
                    sent = True

                elif home_rect.collidepoint(pg.mouse.get_pos()):
                    return -4, False

                name_active = name_rect.collidepoint(mouse_pos)
                pass_active = pass_rect.collidepoint(mouse_pos)

            elif event.type == pg.KEYDOWN:
                if name_active:
                    name_data = handle_text(name_data, 'username:', keys)

                    name_rect = pg.rect.Rect(500, 360,
                                             180 if len(name_data) < 12 else 180 + (10 * (len(name_data) - 12)), 32)
                    name_rect.centerx = 640

                    color = BLACK if name_data != 'username:' else (50, 50, 50)
                    name_text = font.render(name_data, True, color)

                elif pass_active:

                    pass_data = handle_text(pass_data, 'password:', keys)

                    pass_rect = pg.rect.Rect(500, 400,
                                             180 if len(pass_data) < 12 else 180 + (10 * (len(pass_data) - 12)), 32)
                    pass_rect.centerx = 640

                    color = BLACK if name_data != 'password:' else (50, 50, 50)
                    pass_text = font.render(
                        "".join(["*" for i in pass_data]) if pass_data != 'password:' else "password:", True, color)

        keys = pg.key.get_pressed()
        if cnt % 7 == 0:
            if name_active:
                if keys[pg.K_TAB]:
                    pass_active = True
                    name_active = False
                name_data = handle_text(name_data, 'username:', keys)

                name_rect = pg.rect.Rect(500, 360, 180 if len(name_data) < 12 else 180 + (10 * (len(name_data) - 12)),
                                         32)
                name_rect.centerx = 640

                color = BLACK if name_data != 'username:' else (50, 50, 50)
                name_text = font.render(name_data, True, color)

            elif pass_active:
                if keys[pg.K_TAB]:
                    pass_active = False
                    name_active = True

                pass_data = handle_text(pass_data, 'password:', keys)

                pass_rect = pg.rect.Rect(500, 400, 180 if len(pass_data) < 12 else 180 + (10 * (len(pass_data) - 12)),
                                         32)
                pass_rect.centerx = 640
                color = BLACK if name_data != 'password:' else (50, 50, 50)
                pass_text = font.render(pass_data, True, color)

            cnt = 1
        else:
            cnt += 1

        clock.tick(60)
        pg.display.flip()


# this method will handle create screen
def create() -> Tuple[int,str]:
    global CODE
    cmd, CODE = sock.recieve()
    if cmd != 'CODEG':
        return -1, 'CODE ERROR'

    font = pg.font.Font('fonts/FredokaOne-Regular.ttf', 60)
    text = font.render(str(CODE), True, BLACK)
    start_on = pg.image.load('imgs/Start_button.png').convert_alpha()
    start_shade = pg.image.load('imgs/Start_button_off.png').convert_alpha()
    start_image = start_on
    start_rect = start_image.get_rect()
    start_rect.center = (500, 500)
    was = start_image

    screen.fill((128, 128, 128))

    screen.blit(text, (500, 20))

    start_image = start_shade if start_rect.collidepoint(pg.mouse.get_pos()) else start_on
    if start_image == start_shade and was == start_on:
        pg.mixer.music.load('audio/click.wav')
        pg.mixer.music.play()
    was = start_image
    screen.blit(start_image, start_rect)
    pg.display.flip()

    fadein()

    while True:
        screen.fill((128, 128, 128))

        screen.blit(text, (500, 20))

        start_image = start_shade if start_rect.collidepoint(pg.mouse.get_pos()) else start_on
        if start_image == start_shade and was == start_on:
            pg.mixer.music.load('audio/click.wav')
            pg.mixer.music.play()
        was = start_image
        screen.blit(start_image, start_rect)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return -2, False

            elif event.type == pg.MOUSEBUTTONDOWN and event.button == LEFT_BUTTON:
                sock.send('START', CODE, USER)

        try:
            data = sock.timed_recieve()
            if data[0].decode() == 'starting':
                return 4, False

        except timeout:
            pass

        org_screen.blit(screen, next(offset))
        clock.tick(60)
        pg.display.flip()


# this method will show the waiting screen until game host will start the game
def waiting_room() -> Tuple[int,str]:
    waiting_font = pg.font.Font('fonts/FredokaOne-Regular.ttf', 30)
    waiting_text = waiting_font.render('Waiting for other players...', True, BLACK)
    waiting_rect = waiting_text.get_rect(center=(WIDTH / 2, 500))
    loading = Loading((WIDTH / 2, 600))

    code_font = pg.font.Font('fonts/Oxygen-Regular.ttf', 40)
    code_text = code_font.render(str(CODE), True, BLACK)
    code_rect = code_text.get_rect(center=(WIDTH / 2, 400))

    while True:
        screen.fill((128, 128, 128))
        loading.draw(screen)
        screen.blit(waiting_text, waiting_rect)
        screen.blit(code_text, code_rect)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return -2, False

        try:
            data = sock.timed_recieve()
            if data[0].decode() == 'starting':
                return 4, False

        except timeout:
            pass

        loading.update()
        org_screen.blit(screen, (0, 0))
        clock.tick(60)
        pg.display.flip()


# this method will handle the errors that occur in the code
def show_error(error) -> Tuple[int,str]:
    # region home button
    home_button = pg.image.load('imgs/home_button.png').convert_alpha()
    home_button_dark = home_button.copy()
    home_button_dark.fill((80, 80, 80), special_flags=pg.BLEND_RGBA_MULT)
    home_button_rect = home_button.get_rect(topleft=(50, 50))
    home_img = home_button
    # endregion

    # region error rectangle
    error_rect = pg.rect.Rect(500, 500, 500, 500)
    error_rect.center = (580, 360)
    error_font = pg.font.SysFont('Verdana', 50)
    word = pg.font.SysFont('Verdana', 25)
    # endregion

    # region error message
    if error in error_codes:
        text = error_codes[error]
    else:
        text = error
    text = text.split('\n')
    text_surf = [word.render(i, True, RED) for i in text]
    text_header = error_font.render(error, True, RED)
    header_Rect = text_header.get_rect(center=(error_rect.centerx, 150))
    # endregion

    while True:

        screen.fill((128, 128, 128))
        pg.draw.rect(screen, (30, 30, 30), error_rect, 2)
        screen.blit(text_header, header_Rect)
        screen.blit(home_img, home_button_rect)

        x, y = error_rect.centerx, 330
        for word in text_surf:
            rec = word.get_rect(center=(x, y))
            screen.blit(word, rec)
            y += 30

        org_screen.blit(screen, (0, 0))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return -2, False

            elif event.type == pg.MOUSEMOTION:
                home_img = home_button_dark if home_button_rect.collidepoint(pg.mouse.get_pos()) else home_button

            elif event.type == pg.MOUSEBUTTONDOWN and event.button == LEFT_BUTTON:
                if home_button_rect.collidepoint(pg.mouse.get_pos()):
                    if USER:
                        return 1, False
                    return -4, False

        clock.tick(60)
        pg.display.flip()


# this method will handle the join screen
def join() -> Tuple[int,str]:
    global CODE

    font = pg.font.SysFont('Verdana', 20)

    code_data = 'enter code:'
    code_rect = pg.rect.Rect(500, 360, 180, 32)
    code_rect.centerx = 640
    code_active = False
    text = font.render(code_data, True, (50, 50, 50))

    home_button = pg.image.load('imgs/home_button.png').convert_alpha()
    home_shade = home_button.copy()
    home_shade.fill((50, 50, 50), special_flags=pg.BLEND_RGBA_MULT)
    home_image = home_button
    home_rect = home_image.get_rect()
    home_rect.topleft = (50, 50)

    # region login button staff
    login_button_normal = pg.image.load('imgs/join.png').convert_alpha()
    login_button_shade = pg.image.load('imgs/join_dark.png').convert_alpha()
    rect = login_button_normal.get_rect()
    rect.center = (640, 540)
    current_login = login_button_normal
    was = current_login
    # endregion

    # region FadeIn
    screen.fill((128, 128, 128))

    # region Handle Button drawing
    current_login = login_button_shade if rect.collidepoint(pg.mouse.get_pos()) else login_button_normal
    if was != current_login and current_login == login_button_normal:
        pg.mixer.music.load('audio/click.wav')
        pg.mixer.music.play()
    was = current_login
    screen.blit(current_login, rect)
    # endregion

    pg.draw.rect(screen, color_active if code_active else color_inactive, code_rect, border_radius=10)
    screen.blit(text, code_rect)

    pg.display.flip()
    fadein()
    # endregion Fadein

    while True:
        screen.fill((128, 128, 128))

        # region Handle Button drawing
        current_login = login_button_shade if rect.collidepoint(pg.mouse.get_pos()) else login_button_normal
        if was != current_login and current_login == login_button_normal:
            pg.mixer.music.load('audio/click.wav')
            pg.mixer.music.play()
        was = current_login
        screen.blit(current_login, rect)
        # endregion

        pg.draw.rect(screen, color_active if code_active else color_inactive, code_rect, border_radius=10)
        screen.blit(text, code_rect)

        org_screen.blit(screen, (0, 0))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return -2, False

            elif event.type == pg.MOUSEBUTTONDOWN and event.button == LEFT_BUTTON:
                mouse_pos = pg.mouse.get_pos()
                if rect.collidepoint(mouse_pos):
                    sock.send('JOING', code_data, USER)
                    cmd, data = sock.recieve()
                    if cmd == 'GOODK':
                        if TAV_MAFRID not in code_data:
                            CODE = code_data
                            return -5, False
                    else:
                        return -1, 'Bad game code'

                elif home_rect.collidepoint(mouse_pos):
                    return -4, False

                code_active = code_rect.collidepoint(mouse_pos)

            elif event.type == pg.KEYDOWN:
                if code_active:

                    if event.key == pg.K_BACKSPACE:
                        if code_data == 'enter code:':
                            code_data = ''
                        else:
                            code_data = code_data[:-1]
                    elif event.unicode in string.digits :
                        if code_data == 'enter code:':
                            code_data = event.unicode
                        else:
                            code_data += event.unicode

                    if not code_data:
                        code_data = 'enter code:'

                    code_rect = pg.rect.Rect(500, 360,
                                             180 if len(code_data) < 12 else 180 + (10 * (len(code_data) - 12)), 32)
                    code_rect.centerx = 640

                    color = BLACK if code_data != 'enter code:' else (50, 50, 50)
                    text = font.render(code_data, True, color)

        clock.tick(60)
        pg.display.flip()


# this method is used to handle text input
def handle_text(text:str, base_text:str, pressed:list[bool]=pg.key.get_pressed()) -> str:
    if pressed[pg.K_BACKSPACE]:
        if text == base_text:
            return ''
        else:
            return text[:-1]
    else:
        ls = list(filter(lambda x: pressed[ord(x)], string.ascii_letters + string.digits))
        for i in ls:
            if text == base_text:
                return i
            else:
                return text + i
        return text


# this method will handle the register screen
def register() -> Tuple[int,str]:
    global USER

    font = pg.font.SysFont('Verdana', 20)

    # region name text
    name_data = 'username:'
    name_rect = pg.rect.Rect(500, 360, 180, 32)
    name_rect.centerx = 640
    name_active = False
    # endregion

    # region password text
    pass_data = 'password:'
    pass_rect = pg.rect.Rect(500, 400, 180, 32)
    pass_rect.centerx = 640
    pass_active = False
    # endregion

    # region home button
    home_button = pg.image.load('imgs/home_button.png')
    home_on = home_button.copy()
    home_on.fill((100, 100, 100), special_flags=pg.BLEND_MULT)
    home_img = home_button
    home_rect = home_button.get_rect(center=(40, 40))
    # endregion

    name_text = font.render(name_data, True, (50, 50, 50))
    pass_text = font.render(pass_data, True, (50, 50, 50))

    # region FadeIn
    screen.fill((128, 128, 128))

    pg.draw.rect(screen, color_active if name_active else color_inactive, name_rect, border_radius=10)
    pg.draw.rect(screen, color_active if pass_active else color_inactive, pass_rect, border_radius=10)

    screen.blit(name_text, name_rect)
    screen.blit(pass_text, pass_rect)

    pg.display.flip()
    fadein()
    # endregion Fadein

    # region register buttin
    register_button = pg.image.load('imgs/register_button.png').convert_alpha()
    register_button_rect = register_button.get_rect(center=(640, 540))
    darken_register = register_button.copy()
    darken_register.set_colorkey(WHITE)
    darken_register.fill((120, 120, 120), special_flags=pg.BLEND_RGBA_MULT)
    # endregion

    error_font = pg.font.Font('fonts/VarelaRound-Regular.ttf', 20)
    image = register_button
    error = None
    cnt = 1
    sent = False

    while True:

        # region bliting
        screen.fill((128, 128, 128))
        screen.blit(image, register_button_rect)
        screen.blit(home_img, home_rect)

        if error:
            rec = error.get_rect(center=(640, 320))
            screen.blit(error, rec)

        pg.draw.rect(screen, color_active if name_active else color_inactive, name_rect, border_radius=10)
        pg.draw.rect(screen, color_active if pass_active else color_inactive, pass_rect, border_radius=10)

        screen.blit(name_text, name_rect)
        screen.blit(pass_text, pass_rect)

        org_screen.blit(screen, (0, 0))
        # endregion

        if sent:
            try:
                cmd, data = sock.timed_recieve(time=0.001)

                if not cmd.decode():
                    error = error_font.render("Internal Error", True, (255, 0, 0))
                    sent = False

                elif cmd.decode() == "SUCCESS":
                    USER = name_data
                    return 1, False
                else:
                    error = error_font.render(data, True, (255, 0, 0))
                    sent = False

            except timeout:
                pass

        keys = pg.key.get_pressed()
        for event in pg.event.get():
            mouse_pos = pg.mouse.get_pos()

            if event.type == pg.QUIT:
                return -2, False

            elif event.type == pg.MOUSEBUTTONDOWN and event.button == LEFT_BUTTON:

                name_active = name_rect.collidepoint(mouse_pos)
                pass_active = pass_rect.collidepoint(mouse_pos)

                if register_button_rect.collidepoint(mouse_pos):
                    if not sent:
                        sock.send('REGISTER', name_data, pass_data)
                        sent = True
                elif home_rect.collidepoint(mouse_pos):
                    return -4, False

            elif event.type == pg.MOUSEMOTION:
                image = darken_register if register_button_rect.collidepoint(pg.mouse.get_pos()) else register_button
                home_img = home_on if home_rect.collidepoint(pg.mouse.get_pos()) else home_button

            elif event.type == pg.KEYDOWN:
                if name_active:
                    if event.key == pg.K_TAB:
                        pass_active = True
                        name_active = False

                    name_data = handle_text(name_data, 'username:', keys)

                    name_rect = pg.rect.Rect(500, 360,
                                             180 if len(name_data) < 12 else 180 + (10 * (len(name_data) - 12)), 32)
                    name_rect.centerx = 640

                    color = BLACK if name_data != 'username:' else (50, 50, 50)
                    name_text = font.render(name_data, True, color)

                elif pass_active:
                    if event.key == pg.K_TAB:
                        pass_active = False
                        name_active = True

                    pass_data = handle_text(pass_data, 'password:', keys)

                    pass_rect = pg.rect.Rect(500, 400,
                                             180 if len(pass_data) < 12 else 180 + (10 * (len(pass_data) - 12)), 32)
                    pass_rect.centerx = 640

                    color = BLACK if name_data != 'password:' else (50, 50, 50)
                    pass_text = font.render(
                        "".join(["*" for i in pass_data]) if pass_data != 'password:' else "password:", True, color)

        keys = pg.key.get_pressed()
        if cnt % 8 == 0:
            if name_active:
                name_data = handle_text(name_data, 'username:', keys)

                name_rect = pg.rect.Rect(500, 360, 180 if len(name_data) < 12 else 180 + (10 * (len(name_data) - 12)),
                                         32)
                name_rect.centerx = 640

                color = BLACK if name_data != 'username:' else (50, 50, 50)
                name_text = font.render(name_data, True, color)

            elif pass_active:
                pass_data = handle_text(pass_data, 'password:', keys)

                pass_rect = pg.rect.Rect(500, 400, 180 if len(pass_data) < 12 else 180 + (10 * (len(pass_data) - 12)),
                                         32)
                pass_rect.centerx = 640
                color = BLACK if name_data != 'password:' else (50, 50, 50)
                pass_text = font.render("".join(['*' for x in pass_data]) if pass_data != 'password:' else 'password:', True, color)

            cnt = 1
        else:
            cnt += 1

        clock.tick(60)
        pg.display.flip()


# this method will is used to handle user's screen
def handle_player():
    state = -4
    while True:
        if state == -5:
            state, error = waiting_room()

        elif state == -4:
            state, error = main_menu()

        elif state == -3:
            state, error = register()

        elif state == -2:
            break

        elif state == -1:
            state, error = show_error(error)

        elif state == 0:
            state, error = login()

        elif state == 1:
            state, error = after_login()

        elif state == 2:
            state, error = create()

        elif state == 3:
            state, error = join()

        elif state == 4:
            state, error = handle_game()

        elif state == 5:
            state, error = show_result()

    pg.quit()


# this method will handle end game screen
def show_result() -> Tuple[int,str]:
    """
    sock.send('GETRESULT', CODE, 'thanks') # getting the score we needed to beat the level

    if 1:
        try:
            cmd, data = sock.timed_recieve()
        except timeout:
            cmd = ''
        while cmd != b"ending":
            cmd = None
            try:
                cmd, data = sock.timed_recieve(time=1) # cleaning the data if any messages from  the game are still waiting
            except timeout:
                continue

    to_beat = data
    cmd, data = sock.recieve() # getting the score we made

    if cmd == 'gamov': # if there isn't an error we will show the score
        score = data
    else:
        return -2, data
    """
    score = 500
    to_beat = 500
    colored_star = pg.image.load('imgs/starts.png').convert_alpha()
    blacked_star = colored_star.copy() # copying the pervious image to make a new one with white color
    blacked_star.fill((200, 200, 200), special_flags=pg.BLEND_RGB_ADD) # filling the colored stars with white

    score_handled = 10 # the score we loaded in the player's score animation

    x, y = screen.get_size()
    s = pg.Surface((score_handled, colored_star.get_height()))

    font = pg.font.SysFont('Verdana', 50)
    text = font.render(f'Your score is: {str(score)}', True, (50, 50, 50))
    text_rect = text.get_rect(center=(640, 550))

    continue_img_a = pg.image.load('imgs/continue.png').convert_alpha()
    continue_rect = continue_img_a.get_rect(center=(640, 650))
    continue_img_black = continue_img_a.copy()
    continue_img_black.fill((80, 80, 80), special_flags=pg.BLEND_RGB_MULT)
    continue_img = continue_img_a 

    s.blit(colored_star, (0, 0))
    stopped = False
    pg.mixer.Channel(0).play(pg.mixer.Sound('audio/loading.mp3'))

    while True:
        screen.fill((128, 128, 128))
        screen.blit(blacked_star, (x / 2 - blacked_star.get_width() / 2, y / 2 - blacked_star.get_height() / 2))
        screen.blit(s, (x / 2 - blacked_star.get_width() / 2, y / 2 - blacked_star.get_height() / 2))
        screen.blit(text, text_rect)


        pct = score_handled / int(to_beat) * 100

        if pct < 95:
            score_handled += 2
        else:
            screen.blit(continue_img, continue_rect)
            if not stopped:
                pg.mixer.Channel(0).stop()
                stopped = True

        s = pg.Surface((pct / 100 * colored_star.get_width(), colored_star.get_height()))
        s.blit(colored_star, (0, 0))
        s.set_colorkey(BLACK)


        for event in pg.event.get():
            if event.type == pg.QUIT:
                return -2, False
            
            elif event.type == pg.MOUSEMOTION:
                continue_img = continue_img_black if continue_rect.collidepoint(event.pos) else continue_img_a
            
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == LEFT_BUTTON: 
                if continue_rect.collidepoint(event.pos):
                    sock.send('continue', CODE, 'thanks')
                    cmd,data = sock.recieve()
                    if cmd == 'index':
                        if int(data) == 1:
                            return 1, False

        org_screen.blit(screen, (0, 0))
        clock.tick(60)
        pg.display.flip()

# this method will handle the game
def handle_game() -> Tuple[int,str]:
    global offset

    # recieveing the game's data
    level = sock.recieve_pickle()
    pl = sock.recieve_pickle()
    index = int(sock.recieve()[0]) - 1

    level.set_up(index, screen)  # setting up the level sprites and images
    pl: Player = level.players[index]  # getting our client's player

    level.draw(index)
    fadein()
    # pg.mixer.Channel(7).play(pg.mixer.Sound('audio/back1.wav'))

    while True:
        level.draw(index)

        # the idea is every frame we will ask for data, the data is the loaction of every player and the direction he faces rigth now
        try:
            sock.send('GETDA', CODE, 'aa')
        except timeout:
            pass # we don't care if we missed one because it 

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_e:
                    s = pl.handle_e(level)
                    handle_effects(s, index + 1) # handling the effects after player's action
                    sock.send('HANDE', CODE, 'temp')    # informing all players about the action
        try:
            keys = pg.key.get_pressed()
        except pg.error:
            return -2, 'Keyboard error'

        if keys[pg.K_f]:    # checking if the player is pressing the f key
            sock.send('HANDF', CODE, 'temp')   # informing all players about the action
            if pl.handle_f(level):
                pg.mixer.Channel(1).play(pg.mixer.Sound('audio/chop.wav'))  # if player is chopping, play the chop sound


        for x in range(3):
            try:
                cmd, data = sock.timed_recieve(time=0.000001) # we will recieve all players actions
                if cmd.decode() == 'HANDE':
                    s = level.players[int(data)].handle_e(level)    # we will process the player's action
                    handle_effects(s, int(data) + 1)    # handling the effects after player's action

                elif cmd.decode() == 'HANDF':
                    if level.players[int(data)].handle_f(level): 
                        pg.mixer.Channel(int(data) + 1).play(pg.mixer.Sound('audio/chop.wav'))

                elif cmd.decode() == 'PICKLE':  # recieving all players positions and faces
                    players_pos = pickle.loads(data)    # unpickling the data
                    for i in range(len(players_pos)):
                        if i == index:
                            continue # we already have our own position so no need to process it

                        level.players[i].pos = players_pos[i][0] # setting the player's position
                        level.players[i].rect.center = players_pos[i][0] 
                        if players_pos[i][1] != (0.0, 0.0):
                            level.players[i].facing = players_pos[i][1] # setting the player's facing direction

                elif cmd.decode() == 'order':
                    order = pickle.loads(data)  # unpickling the order object
                    order.setup() # setting up the order's sprites
                    level.orders.append(order) 
                    level.group.add(order) # adding the order to the group of all sprites
                    pg.mixer.Channel(0).play(pg.mixer.Sound('audio/order.wav')) # playing the recieved order sound

                elif cmd.decode() == 'gamov': # if game is over we will return to end screen, and recieve the score
                    return 5, False

            except timeout:
                pass

        pl.input() # getting the player's input and handling it

        sock.send('CHAPOS', CODE, f'{pl.pos[0]}|{pl.pos[1]}&{pl.directon.x}|{pl.directon.y}')
        # sending the player's position and facing direction to all players

        m = level.update()
        
        if m == 'done':
            sock.send('GAMOV', CODE, f'{level.score.score}')

        elif m == 'time':
            if not pg.mixer.Channel(7).get_busy():
                pg.mixer.Channel(7).play(pg.mixer.Sound('audio/cnt.wav'))

        org_screen.blit(screen, next(offset)) # blitting the screen to the original screen
        pg.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    handle_player()
