from time import sleep
from TcpEncryptedSocket import EncSocket
import threading
import string
import random
from game import *
from extended import *
import pickle
from other import *
from hashlib import sha256

server = EncSocket(('', 51876), False)
threads = []
games = {}
USERS = {}
ONLINE_PLAYERS = {}
sock_th = []
lock = threading.Lock()
pg.init()


def generate_salt(len=6):
    return ''.join((random.choice(string.ascii_lowercase + string.ascii_uppercase) for x in range(len)))


# method that will closes any AFK players and any games that are not in progress
def thread_close():
    global threads
    while True:
        for t in threads:
            t.join(timeout=1)
            if not t.is_alive():
                print('disconnected', t)
                sock = sock_th[threads.index(t)]
                threads.remove(t)
                x = next((x for x in games if sock in games[x].players_sock), None)
                if x and games[x]:
                    games[x].players_sock.remove(sock)
                    if not games[x].players_sock:
                        games[x].played = False
                        games.pop(x)


# generate random string
# input: length of string
# output: random string
def generate_string(length=4):
    return str(random.randint(0,9999)).zfill(length)


# method for each game that will send them the orders in the game
# input: game code in dict
def handle_game_orders(code):
    sleep(5)
    try:
        while games[code].played:
            rec = random.choice(games[code].level.recpies[0])
            rec = Order(rec)
            for pl in games[code].players_sock:
                try:
                    server.send('order', pickle.dumps(rec), sock=pl)
                except ConnectionError:
                    continue
            time.sleep(random.randint(15, 30))
    except KeyError:
        return


# method that will process the message that was received
# input:
#   cmd: the command that was received
#   code: the code of the game created (before the games it will be blank)
#   data: the data that was received
# output:
#   ret: the message that will be sent back to the client
def handle_msg(cmd, code, data, sock):
    global threads

    cmd = cmd.upper()

    if cmd == "CREATE":
        code = generate_string()
        while code in games:
            code = generate_string()
        games[code] = Game()

        games[code].add_player(sock, data)

        return 'CODEG', code

    elif cmd == 'START':
        games[code].start()

        for i, v in enumerate(games[code].players_sock):
            server.send('starting', sock=v)
            server.send_pickle(games[code].level, sock=v)
            server.send_pickle(games[code].level.players[i], sock=v)

            server.send(str(i + 1).zfill(4), sock=v)
            t = threading.Thread(target=handle_game_orders, args=(code,))
            t.start()
            threads.append(t)
            sock_th.append(None)

        return None

    elif cmd == 'GETDA':
        return 'PICKLE', pickle.dumps(games[code].players_pos)

    elif cmd == 'CHAPOS':
        data = data.split("&")
        pos = data[0].split("|")
        vec = data[1].split("|")
        pos = (float(pos[0]), float(pos[1]))
        vec = (float(vec[0]), float(vec[1]))

        index = games[code].players_sock.index(sock)
        games[code].players_pos[index] = [pos, vec]

    elif cmd == 'JOING':
        if code not in games.keys():
            return 'ERROR', 'WRONG KEY'

        games[code].add_player(sock, data)

        return 'GOODK', 'GOODLUCK!'

    elif cmd == 'HANDE':
        index = games[code].players_sock.index(sock)
        for i in games[code].players_sock:
            if i == sock:
                continue
            server.send('HANDE', str(index), sock=i)

    elif cmd == 'HANDF':
        index = games[code].players_sock.index(sock)
        for i in games[code].players_sock:
            if i == sock:
                continue
            server.send('HANDF', str(index), sock=i)

    elif cmd == 'GAMOV':
        games[code].played = False
        games[code].score = data
        return 'gamov', data

    elif cmd == 'GETRESULT':
        server.send('ending', str(games[code].level.points_to_beat), sock=sock)
        return 'gamov', games[code].score

    elif cmd == 'REGISTER':
        if not data:
            return 'ERROR', 'NO DATA'
        user = code
        password = data
        if user in USERS:
            return 'ERROR', 'USER ALREADY EXISTS'
        s = generate_salt()
        USERS[user] = (sha256(f'{password}{s}'.encode()).hexdigest(), s)
        lock.acquire()
        with open('users.txt', 'a') as f:
            f.write(f'\n{user},{USERS[user][0]},{s}')

        lock.release()

        return 'SUCCESS', 'REGISTERED'

    elif cmd == 'LOGIN':
        if not data:
            return 'ERROR', 'NO DATA'
        user = code
        password = data
        if user not in USERS:
            return 'ERROR', 'USER NOT FOUND'

        if USERS[user][0] != sha256(f'{password}{USERS[user][1]}'.encode()).hexdigest():
            return 'ERROR', 'WRONG PASSWORD'

        ONLINE_PLAYERS[user] = sock
        return 'SUCCESS', 'LOGGED IN'

    elif cmd == 'continue':
        if code not in games.keys():
            return 'ERROR', 'WRONG KEY'
        
        games[code].next_level()
        i = games[code].players_sock.index(sock)
        return 'index',server.send(str(i + 1).zfill(4), sock=v)


# method that will handle the client receiveing and sending messages
def handle_client(sock, addr):
    while True:
        break

    while True:
        ret = None
        try:
            cmd, code, data = server.recieve(sock)
        except ConnectionError:
            return

        ret = handle_msg(cmd, code, data, sock=sock)
        try:
            if ret:
                server.send(*ret, sock=sock)

        except Exception as e:
            print(e)
            return


# main loop that will handle the clients
def main():
    global threads
    global USERS

    closer = threading.Thread(target=thread_close)
    closer.start()

    with open('users.txt', 'r') as f:
        data = f.read()
    data = data.split('\n')
    for i in data:
        i = i.split(',')
        USERS[i[0]] = (i[1], i[2])

    print('accepting')
    while True:
        print('before accept')
        sock, addr = server.accept()
        print('hello', addr)
        t = threading.Thread(target=handle_client, args=(sock, addr))
        t.start()
        threads.append(t)
        sock_th.append(sock)


if __name__ == "__main__":
    main()
