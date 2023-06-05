from tkinter import CENTER
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

myappid = 'mycompany.myproduct.subproduct.version'  # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

pg.init()

sock = EncSocket(("127.0.0.1", 57891), protocol=EncSocket.dh_aes)
sock.connect()

WIDTH, HEIGHT = 1280, 720
USER = None
RED = (255, 0, 0)
BLACK = (0, 0, 0)

TAV_MAFRID = "#@@!?#%@"

clock = pg.time.Clock()

screen = pg.display.set_mode((WIDTH, HEIGHT), pg.DOUBLEBUF)
crates = [ChikenCrate, LettuceCrate, CucumberCrate, TomatoCrate, BunCrate, RiceCrate, AlgaCrate]
LEFT_BUTTON = 1
color_inactive = pg.Color('lightskyblue3')
color_active = pg.Color('dodgerblue2')
pg.mixer.init()
pg.mixer.music.load('audio/start.wav')
pg.mixer.music.set_volume(0.2)
pg.mixer.Channel(0).set_volume(0.5)
pg.mixer.music.play()
pg.display.set_icon(pg.image.load('imgs/icon.png'))
pg.display.set_caption("DrChef", 'imgs/icon.png')

error_codes = {
    "Bad game code": 'The code you have entered is incorrect\nplease enter a correct one\nor create a new game',
}

CODE = None


def DrawArrow(x, y, color):
    surf = pg.Surface((350, 350))
    surf.fill(WHITE)
    surf.set_colorkey(WHITE)
    pg.draw.polygon(surf, color, ((0, 25), (0, 50), (50, 50), (50, 75), (75, 37), (50, 0), (50, 25)))
    surf = pg.transform.rotate(surf, -90)

    screen.blit(surf, (x, y))


def fadeout():
    fadeout = pg.Surface((WIDTH, HEIGHT))
    fadeout = fadeout.convert()
    sub = screen.copy()
    fadeout.fill(BLACK)
    for i in range(255):
        screen.blit(sub, (0, 0))
        fadeout.set_alpha(i)
        screen.blit(fadeout, (0, 0))
        pg.display.flip()


def fadein():
    fadeout = pg.Surface((WIDTH, HEIGHT))
    fadeout = fadeout.convert()
    sub = screen.copy()
    fadeout.fill(BLACK)
    for i in range(255):
        screen.blit(sub, (0, 0))
        fadeout.set_alpha(255 - i)
        screen.blit(fadeout, (0, 0))
        pg.display.flip()


def hanlde_audio(s, chn):
    if s == 'trash':
        pg.mixer.Channel(chn).play(pg.mixer.Sound('audio/trash.wav'))

    elif s == 'pick':
        pg.mixer.Channel(chn).play(pg.mixer.Sound('audio/pick.wav'))

    elif s == 'drop':
        pg.mixer.Channel(chn).play(pg.mixer.Sound('audio/drop.wav'))

    elif s == 'plate':
        pg.mixer.Channel(chn).play(pg.mixer.Sound('audio/plate.wav'))

    elif s == 'served':
        pg.mixer.Channel(chn).play(pg.mixer.Sound('audio/bell.wav'))


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
        return 0.


def main_menu():
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

    while True:
        screen.fill((128, 128, 128))
        screen.blit(log_img, log_rect)
        screen.blit(reg_img, reg_rect)

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

        pg.display.flip()


def after_login():
    # pg.mixer.Channel(0).play(pg.mixer.Sound('audio\song.wav'))
    global USER

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

    if create_image == create_button_on and was == create_button_off:
        pg.mixer.music.load('audio/click.wav')
        pg.mixer.music.play()

    join_image = join_button_on if join_image_rect.collidepoint((x, y)) else join_button_off
    if join_image == join_button_on and was == join_button_off:
        pg.mixer.music.load('audio/click.wav')
        pg.mixer.music.play()

    out_img = logout_on if logout_rect.collidepoint((x, y)) else logout
    if out_img == logout_on and was == logout:
        pg.mixer.music.load('audio/click.wav')
        pg.mixer.music.play()

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

        screen.blit(join_image, join_image_rect)

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

        pg.display.flip()


def login():
    global USER
    # region login
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

    # region FadeIn
    screen.fill((128, 128, 128))

    pg.draw.rect(screen, color_active if name_active else color_inactive, name_rect, border_radius=10)
    pg.draw.rect(screen, color_active if pass_active else color_inactive, pass_rect, border_radius=10)

    screen.blit(name_text, name_rect)
    screen.blit(pass_text, pass_rect)
    screen.blit(home_img, home_rect)

    pg.display.flip()
    fadein()
    # endregion Fadein

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

        screen.blit(name_text, name_rect)
        screen.blit(pass_text, pass_rect)
        screen.blit(home_img, home_rect)

        if error:
            rec = error.get_rect(center=(640, 460))
            screen.blit(error, rec)

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
                    if event.key == pg.K_TAB:
                        pass_active = True
                        name_active = False

                    elif event.key == pg.K_BACKSPACE:
                        if name_data == 'username:':
                            name_data = ''
                        else:
                            name_data = name_data[:-1]
                    elif event.unicode in string.ascii_letters or event.unicode == " " or event.unicode in string.digits:
                        if name_data == 'username:':
                            name_data = event.unicode
                        else:
                            name_data += event.unicode

                    if not name_data:
                        name_data = 'username:'

                    name_rect = pg.rect.Rect(500, 360,
                                             180 if len(name_data) < 12 else 180 + (10 * (len(name_data) - 12)), 32)
                    name_rect.centerx = 640

                    color = BLACK if name_data != 'username:' else (50, 50, 50)
                    name_text = font.render(name_data, True, color)

                elif pass_active:
                    if event.key == pg.K_TAB:
                        pass_active = False
                        name_active = True

                    elif event.key == pg.K_BACKSPACE:
                        if pass_data == 'password:':
                            pass_data = ''
                        else:
                            pass_data = pass_data[:-1]
                    elif event.unicode in string.ascii_letters or event.unicode == " " or event.unicode in string.digits:
                        if pass_data == 'password:':
                            pass_data = event.unicode
                        else:
                            pass_data += event.unicode

                    if not pass_data:
                        pass_data = 'password:'

                    pass_rect = pg.rect.Rect(500, 400,
                                             180 if len(pass_data) < 12 else 180 + (10 * (len(pass_data) - 12)), 32)
                    pass_rect.centerx = 640

                    color = BLACK if name_data != 'password:' else (50, 50, 50)
                    pass_text = font.render(pass_data, True, color)

        keys = pg.key.get_pressed()
        if cnt % 150 == 0:
            if keys[pg.K_BACKSPACE]:
                if name_active:
                    if name_data == 'username:':
                        name_data = ''
                    else:
                        name_data = name_data[:-1]
                        if not name_data:
                            name_data = 'username:'

                    if not name_data:
                        name_data = 'username:'

                    name_rect = pg.rect.Rect(500, 360,
                                             180 if len(name_data) < 12 else 180 + (10 * (len(name_data) - 12)), 32)
                    name_rect.centerx = 640

                    color = BLACK if name_data != 'username:' else (50, 50, 50)
                    name_text = font.render(name_data, True, color)

                elif pass_active:
                    if pass_data == 'password:':
                        pass_data = ''
                    else:
                        if pass_data:
                            pass_data = pass_data[:-1]
                        else:
                            pass_data = 'password:'

                    if not pass_data:
                        pass_data = 'password:'

                    pass_rect = pg.rect.Rect(500, 400,
                                             180 if len(pass_data) < 12 else 180 + (10 * (len(pass_data) - 12)), 32)
                    pass_rect.centerx = 640
                    color = BLACK if name_data != 'password:' else (50, 50, 50)
                    pass_text = font.render(pass_data, True, color)

            cnt = 1
        else:
            cnt += 1

        pg.display.flip()


def create():
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
                return 4, False

        pg.display.flip()


def show_error(error):
    error_rect = pg.rect.Rect(500, 500, 500, 500)
    error_rect.center = (580, 360)
    error_font = pg.font.SysFont('Verdana', 50)
    word = pg.font.SysFont('Verdana', 25)

    text = error_codes[error]
    text = text.split('\n')
    text_surf = [word.render(i, True, RED) for i in text]
    text_header = error_font.render(error, True, RED)
    header_Rect = text_header.get_rect(center=(error_rect.centerx, 150))
    while True:

        screen.fill((128, 128, 128))
        pg.draw.rect(screen, (30, 30, 30), error_rect, 2)
        screen.blit(text_header, header_Rect)
        x, y = error_rect.centerx, 330
        for word in text_surf:
            rec = word.get_rect(center=(x, y))
            screen.blit(word, rec)
            y += 30

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return -2, False

        pg.display.flip()


def join():
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
                            return 4, False
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
                    elif event.unicode in string.ascii_letters:
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

        pg.display.flip()


def handle_text(text, event, base_text):
    if event.key == pg.K_BACKSPACE:
        if text == base_text:
            text = ''
        else:
            text = text[:-1]
    elif event.unicode in string.ascii_letters or event.unicode == " " or event.unicode in string.digits:
        if text == base_text:
            text = event.unicode
        else:
            text += event.unicode

    if not text:
        text = base_text

    return text


def register():
    global USER

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

    # region FadeIn
    screen.fill((128, 128, 128))

    pg.draw.rect(screen, color_active if name_active else color_inactive, name_rect, border_radius=10)
    pg.draw.rect(screen, color_active if pass_active else color_inactive, pass_rect, border_radius=10)

    screen.blit(name_text, name_rect)
    screen.blit(pass_text, pass_rect)

    pg.display.flip()
    fadein()
    # endregion Fadein

    register_button = pg.image.load('imgs/register_button.png').convert_alpha()
    register_button_rect = register_button.get_rect(center=(640, 540))
    darken_register = register_button.copy()
    darken_register.set_colorkey(WHITE)
    darken_register.fill((120, 120, 120), special_flags=pg.BLEND_RGBA_MULT)
    error_font = pg.font.Font('fonts/VarelaRound-Regular.ttf', 20)
    image = register_button
    error = None
    cnt = 1
    sent = False
    while True:
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

        for event in pg.event.get():
            mouse_pos = pg.mouse.get_pos()

            if event.type == pg.QUIT:
                return -2, False

            elif event.type == pg.MOUSEBUTTONDOWN and event.button == LEFT_BUTTON:

                if register_button_rect.collidepoint(mouse_pos):
                    if not sent:
                        sock.send('REGISTER', name_data, pass_data)
                        sent = True
                elif home_rect.collidepoint(mouse_pos):
                    return -4, False

            elif event.type == pg.MOUSEMOTION:
                image = darken_register if register_button_rect.collidepoint(pg.mouse.get_pos()) else register_button
                home_img = home_on if home_rect.collidepoint(pg.mouse.get_pos()) else home_button

                name_active = name_rect.collidepoint(mouse_pos)
                pass_active = pass_rect.collidepoint(mouse_pos)

            elif event.type == pg.KEYDOWN:
                if name_active:
                    if event.key == pg.K_TAB:
                        pass_active = True
                        name_active = False

                    name_data = handle_text(name_data, event, 'username:')

                    name_rect = pg.rect.Rect(500, 360,
                                             180 if len(name_data) < 12 else 180 + (10 * (len(name_data) - 12)), 32)
                    name_rect.centerx = 640

                    color = BLACK if name_data != 'username:' else (50, 50, 50)
                    name_text = font.render(name_data, True, color)

                elif pass_active:
                    if event.key == pg.K_TAB:
                        pass_active = False
                        name_active = True

                    pass_data = handle_text(pass_data, event, 'password:')

                    pass_rect = pg.rect.Rect(500, 400,
                                             180 if len(pass_data) < 12 else 180 + (10 * (len(pass_data) - 12)), 32)
                    pass_rect.centerx = 640

                    color = BLACK if name_data != 'password:' else (50, 50, 50)
                    pass_text = font.render(
                        "".join(["*" for i in pass_data]) if pass_data != 'password:' else "password:", True, color)

        keys = pg.key.get_pressed()
        if cnt % 220 == 0:
            if keys[pg.K_BACKSPACE]:
                if name_active:
                    if name_data == 'username:':
                        name_data = ''
                    else:
                        name_data = name_data[:-1]
                        if not name_data:
                            name_data = 'username:'

                    name_rect = pg.rect.Rect(500, 360,
                                             180 if len(name_data) < 12 else 180 + (10 * (len(name_data) - 12)), 32)
                    name_rect.centerx = 640

                    color = BLACK if name_data != 'username:' else (50, 50, 50)
                    name_text = font.render(name_data, True, color)

                elif pass_active:
                    if pass_data == 'password:':
                        pass_data = ''
                    else:
                        pass_data = pass_data[:-1]
                        if not pass_data:
                            pass_data = 'password:'

                    pass_rect = pg.rect.Rect(500, 400,
                                             180 if len(pass_data) < 12 else 180 + (10 * (len(pass_data) - 12)), 32)
                    pass_rect.centerx = 640
                    color = BLACK if name_data != 'password:' else (50, 50, 50)
                    pass_text = font.render(
                        "".join(["*" for i in pass_data]) if pass_data != 'password:' else "password:", True, color)

            cnt = 1
        else:
            cnt += 1

        pg.display.flip()


def handle_player():
    state = -4
    while True:
        if state == -4:
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


def show_result():
    sock.send('GETRESULT', CODE, 'thanks')
    if 1:
        try:
            cmd, data = sock.timed_recieve()
        except:
            cmd = ''
        while cmd != b"ending":
            cmd = None
            try:
                cmd, data = sock.timed_recieve(time=1)
            except timeout:
                continue
    to_beat = data
    cmd, data = sock.recieve()

    if cmd == 'gamov':
        score = data
    else:
        return -2, data

    score = 500
    clock = pg.time.Clock()
    colored_star = pg.image.load('imgs/starts.png').convert_alpha()

    blacked_star = colored_star.copy()
    blacked_star.fill((200, 200, 200), special_flags=pg.BLEND_RGB_ADD)
    index = 10
    x, y = screen.get_size()
    s = pg.Surface((index, colored_star.get_height()))
    font = pg.font.SysFont('Verdana', 50)
    text = font.render('Your score is: ' + str(score), True, (50, 50, 50))
    text_rect = text.get_rect(center=(640, 600))
    s.blit(colored_star, (0, 0))
    stopped = False
    pg.mixer.Channel(0).play(pg.mixer.Sound('audio/loading.mp3'))
    while True:
        screen.fill((128, 128, 128))
        screen.blit(blacked_star, (x / 2 - blacked_star.get_width() / 2, y / 2 - blacked_star.get_height() / 2))
        screen.blit(s, (x / 2 - blacked_star.get_width() / 2, y / 2 - blacked_star.get_height() / 2))
        screen.blit(text, text_rect)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return -2, False

        clock.tick(60)
        pg.display.flip()
        pct = index / int(to_beat) * 100

        if pct < 100:
            index += 2
        else:
            if not stopped:
                pg.mixer.Channel(0).stop()
                stopped = True

        s = pg.Surface((pct / 100 * colored_star.get_width(), colored_star.get_height()))
        s.blit(colored_star, (0, 0))
        s.set_colorkey(BLACK)


def handle_game():
    level = sock.recieve_pickle()
    pl = sock.recieve_pickle()
    index = int(sock.recieve()[0]) - 1

    level.set_up(index, screen)
    pl: Player = level.players[index]

    screen.fill(GREEN)
    level.draw(index)
    fadein()
    # pg.mixer.Channel(7).play(pg.mixer.Sound('audio/back1.wav'))

    while True:
        screen.fill(GREEN)
        level.draw(index)
        try:
            sock.send('GETDA', CODE, 'aa')
        except timeout:
            pass

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_e:
                    s = pl.handle_e(level, crates)
                    hanlde_audio(s, index + 1)
                    sock.send('HANDE', CODE, 'temp')

        keys = pg.key.get_pressed()
        if keys[pg.K_f]:
            sock.send('HANDF', CODE, 'temp')
            if pl.handle_f(level):
                pg.mixer.Channel(1).play(pg.mixer.Sound('audio/chop.wav'))

        for x in range(4):
            try:
                cmd, data = sock.timed_recieve(time=0.001)
                if cmd.decode() == 'HANDE':
                    s = level.players[int(data)].handle_e(level, crates)
                    hanlde_audio(s, int(data) + 1)

                elif cmd.decode() == 'HANDF':
                    if level.players[int(data)].handle_f(level):
                        pg.mixer.Channel(int(data) + 1).play(pg.mixer.Sound('audio/chop.wav'))

                elif cmd.decode() == 'PICKLE':
                    players_pos = pickle.loads(data)
                    for i in range(len(players_pos)):
                        if i == index:
                            continue
                        level.players[i].pos = players_pos[i][0]
                        level.players[i].rect.center = players_pos[i][0]
                        if players_pos[i][1] != (0.0, 0.0):
                            level.players[i].facing = players_pos[i][1]

                elif cmd.decode() == 'order':
                    order = pickle.loads(data)
                    order.setup()
                    level.orders.append(order)
                    level.group.add(order)
                    pg.mixer.Channel(0).play(pg.mixer.Sound('audio/order.wav'))

                elif cmd.decode() == 'gamov':
                    return 5, False

            except timeout:
                pass

        if pl.input():
            try:
                sock.send('CHAPOS', CODE, f'{pl.pos[0]}|{pl.pos[1]}&{pl.directon.x}|{pl.directon.y}')
            except timeout:
                pass
            # we won't care if one msg is out because it will be overwritten by the next frame anyway

        m = level.update()
        if m == 'done':
            sock.send('GAMOV', CODE, f'{level.score.score}')

        elif m == 'time':
            if not pg.mixer.Channel(7).get_busy():
                pg.mixer.Channel(7).play(pg.mixer.Sound('audio/cnt.wav'))

        print(clock.get_fps())
        pg.display.flip()
        clock.tick()


if __name__ == "__main__":
    handle_player()
