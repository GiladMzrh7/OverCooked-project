import socket
import random
import string
import pickle
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import logging
import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
from typing import Tuple
import datetime

class AESCipher(object):
    def __init__(self, key):
        self.block_size = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, plain_text):
        try:
            plain_text = plain_text.encode()
        except AttributeError:
            pass

        plain_text = self.__pad(plain_text)
        iv = Random.new().read(self.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        encrypted_text = cipher.encrypt(plain_text)
        return base64.b64encode(iv + encrypted_text)

    def decrypt(self, encrypted_text):
        encrypted_text = base64.b64decode(encrypted_text)
        iv = encrypted_text[:self.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        plain_text = cipher.decrypt(encrypted_text[AES.block_size:])
        return self.__unpad(plain_text)

    def __pad(self, plain_text):
        number_of_bytes_to_pad = self.block_size - len(plain_text) % self.block_size
        ascii_string = chr(number_of_bytes_to_pad)
        padding_str = number_of_bytes_to_pad * ascii_string
        padded_plain_text = plain_text + padding_str.encode()
        return padded_plain_text

    @staticmethod
    def __unpad(plain_text):
        last_character = plain_text[len(plain_text) - 1:]
        bytes_to_remove = ord(last_character)
        return plain_text[:-bytes_to_remove]


def key_gen(size=8, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size))


class EncSocket(socket.socket):
    dh_aes = 'dh_aes'
    rsa = 'rsa'

    def __init__(self, addr, client=True, protocol=dh_aes) -> None:
        super().__init__()
        logging.basicConfig(filename='server_log.log',level=logging.DEBUG)
        self.client = client
        self.addr = addr

        if protocol and protocol != self.dh_aes and protocol != self.rsa:
            raise ValueError(f"\nERROR:\nUnknown protocol: {protocol} \npls use Encsocket.rsa or dh_aes")

        self.prot = protocol

        if self.prot == self.dh_aes:
            self.my_key = int(key_gen(chars=string.digits))

        elif self.prot == self.rsa:
            self.key_pair = RSA.generate(2048)
            self.my_key = self.key_pair.publickey()

        if not client:
            self.public_codes = {}

            self.prime = 641928468969180888504879500549

            self.gen = int(key_gen(size=32, chars=string.digits))
            self.bind(self.addr)
            self.listen()
            self.protocols = {}

            self.my_key_dh_aes = int(key_gen(chars=string.digits))

            self.key_pair = RSA.generate(2048)
            self.my_key_rsa = self.key_pair.publickey()

    def accept(self) -> tuple:
        c, addr = super().accept()
        prot = self.__recieve_diffie(c) # recieving protocol
        self.protocols[c] = prot

        if prot == self.dh_aes:
            self.__diffie_accept(c)
        elif prot == self.rsa:
            self.__rsa_accept(c)
        return c, addr

    def connect(self):
        super().connect(self.addr)
        if not self.prot:
            return True
        elif self.prot == self.dh_aes:
            self.__send_diffie(self, self.prot)
            return self.__diffie_connect()
        elif self.prot == self.rsa:
            self.__send_diffie(self, self.prot)
            return self.__rsa_connect()

    def __diffie_accept(self, c):

        self.__send_diffie(c, str(self.prime).encode())

        self.__recieve_diffie(c)  # ack

        gen = random.randint(1, self.prime - 2)
        self.__send_diffie(c, str(gen).encode())

        self.__recieve_diffie(c)  # ack

        mynum = pow(gen, self.my_key, self.prime)

        msg = str(mynum).encode()
        self.__send_diffie(c, msg)

        other_num = int(self.__recieve_diffie(c))

        final_num = pow(other_num, self.my_key, self.prime)

        self.public_codes[c] = str(final_num)

    def __diffie_connect(self):

        prime = int(self.__recieve_diffie(self))

        self.__send_diffie(self, 'got!'.encode())
        gen = int(self.__recieve_diffie(self))

        self.__send_diffie(self, 'got!'.encode())
        data = int(self.__recieve_diffie(self))

        half_way = pow(gen, self.my_key, prime)
        self.__send_diffie(self, (str(half_way)).encode())

        end_way = pow(data, self.my_key, prime)

        self.public_key = str(end_way)

        return True

    def __rsa_accept(self, c):
        a = self.__revieve_pickle_normal(c)
        self.__send_pickle_normal(self.my_key_rsa.export_key(), c)
        self.public_codes[c] = RSA.import_key(a)

    def __rsa_connect(self):
        self.__send_pickle_normal(self.my_key.export_key())

        self.public_key = RSA.import_key(self.__revieve_pickle_normal())

    def __recieve_diffie(self, sock):

        leng = b''
        while len(leng) < 4:
            leng += sock.recv(1)

        data = b''
        while len(data) < int(leng):
            try:
                chunk = sock.recv(1)
                data += chunk

                if chunk == b'':  # if got nothing, that means that socket disconnected
                    return None, None, None

            except ConnectionResetError:
                return None, None, None  # socket was closed for some other reason

        data = data.decode()
        return data

    def __send_diffie(self, sock, cmd):
        try:
            cmd = cmd.encode()
        except AttributeError:
            pass
        if type(sock) == EncSocket:
            super().send(str(len(cmd)).zfill(4).encode() + cmd)
        else:
            sock.send(str(len(cmd)).zfill(4).encode() + cmd)

    def __send_normal(self, args, sock=None):

        msg = b''
        for i in args:
            try:
                i = i.encode()
            except AttributeError:
                pass
            msg += i + "#@@!?#%@".encode()
        msg += "##".encode()

        if not self.client:
            sock.send(str(len(msg)).zfill(4).encode() + msg)
        else:
            super().send(str(len(msg)).zfill(4).encode() + msg)

    def recieve(self, sock=None):
        if not self.client:
            prot = self.protocols[sock]
        else:
            prot = self.prot

        if not sock:
            sock = self

        if not prot:
            return self.__recieve_msg_normal(sock)

        elif prot == self.dh_aes:
            data = self.__recieve_dh_aes(sock)
        elif prot == self.rsa:
            data = self.__recieve_msg_rsa(sock)
        if not self.client:
            self.handle_logging(data.copy(),sock)
            return data
        return data

    def __recieve_dh_aes(self, sock: socket.socket):
        if self.client:
            aes = AESCipher(self.public_key)
        else:
            aes = AESCipher(self.public_codes[sock])

        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.settimeout(10000)

        data = self.__get_bdata(sock)

        data = data.split(b"#@@!?#%@")  # cleaning the data
        data = data[:-1]
        data = list(filter(None, data))
        to_ret = []
        for i in data:
            to_ret.append(aes.decrypt(i).decode())

        return to_ret

    def __send_msg_aes(self, args, sock=None):
        if self.client:
            aes = AESCipher(self.public_key)
        else:
            aes = AESCipher(self.public_codes[sock])

        msg = b''
        for i in args:
            msg += aes.encrypt(i) + "#@@!?#%@".encode()

        msg += "##".encode()
        if sock != self:
            sock.send(str(len(msg)).zfill(4).encode() + msg)
        else:
            super().send(str(len(msg)).zfill(4).encode() + msg)

    def __send_msg_rsa(self, args, sock=None):
        if not self.client:
            key = self.public_codes[sock]
        else:
            key = self.public_key

        msg = b''
        for i in args:
            encryptor = PKCS1_OAEP.new(key)
            try:
                i = i.encode()
            except AttributeError:
                pass
            d = encryptor.encrypt(i)
            msg += d + "#@@!?#%@".encode()
        msg += "##".encode()

        if not self.client:
            sock.send(str(len(msg)).zfill(4).encode() + msg)
        else:
            super().send(str(len(msg)).zfill(4).encode() + msg)

    def send(self, *args, sock=None):
        if self.client:
            prot = self.prot
        else:
            prot = self.protocols[sock]

        if not sock:
            sock = self

        if not prot:
            self.__send_normal(args)

        elif prot == self.dh_aes:
            self.__send_msg_aes(args, sock=sock)
        elif prot == self.rsa:
            self.__send_msg_rsa(args, sock=sock)
        
        if not self.client:
            self.handle_logging(list(args),self)


    def __recieve_msg_rsa(self, sock=None):
        key = self.key_pair

        dec = PKCS1_OAEP.new(key)

        data = self.__get_bdata(sock)

        # write_to_log(sock.getpeername(),data)
        data = data.split("#@@!?#%@".encode())  # cleaning the data
        data = data[:-1]
        data = list(filter(None, data))

        to_ret = []
        for i in data:
            to_ret.append(dec.decrypt(i).decode())

        return to_ret

    def __recieve_msg_normal(self, sock=None):

        data = self.__get_bdata(sock)

        # write_to_log(sock.getpeername(),data)
        data = data.split("#@@!?#%@".encode())  # cleaning the data
        data = data[:-1]
        data = list(filter(None, data))

        to_ret = []
        for i in data:
            to_ret.append(i.decode())

        return to_ret

    def __send_pickle_dh_aes(self, obj=None, sock=None):
        if self.prot == self.dh_aes:
            if self.client:
                aes = AESCipher(self.public_key)
            else:
                aes = AESCipher(self.public_codes[sock])

        bdata = pickle.dumps(obj)
        msg = aes.encrypt(bdata)

        if not self.client:
            sock.send(str(len(msg)).zfill(4).encode() + msg)
        else:
            super().send(str(len(msg)).zfill(4).encode() + msg)

    def __recieve_pickle_dh_aes(self, s):
        if self.prot == self.dh_aes:
            if self.client:
                aes = AESCipher(self.public_key)
            else:
                aes = AESCipher(self.public_codes[s])
        if not s:
            s = self
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.settimeout(10000)

        leng = b''
        while len(leng) < 4:
            leng += s.recv(1)

        data = b''
        while len(data) < int(leng):
            data += s.recv(1)

        bdata = aes.decrypt(data)

        return pickle.loads(bdata)

    def __recieve_pickle_rsa(self, s):

        key = self.key_pair

        dec = PKCS1_OAEP.new(key)

        leng = b''
        while len(leng) < 4:
            leng += s.recv(1)

        data = b''
        while len(data) < int(leng):
            data += s.recv(1)

        bdata = dec.decrypt(data)

        return pickle.loads(bdata)

    def __send_pickle_rsa(self, obj, sock=None):
        bdata = pickle.dumps(obj)
        if not self.client:
            key = self.public_codes[sock]
        else:
            key = self.public_key
        dec = PKCS1_OAEP.new(key)

        msg = dec.encrypt(bdata)
        if not self.client:
            sock.send(str(len(msg)).zfill(4).encode() + msg)
        else:
            self.send(str(len(msg)).zfill(4).encode() + msg)

    def __send_pickle_normal(self, obj, sock=None):
        msg = pickle.dumps(obj)

        if not self.client:
            sock.send(str(len(msg)).zfill(4).encode() + msg)
        else:
            super().send(str(len(msg)).zfill(4).encode() + msg)

    def __revieve_pickle_normal(self, s=None):
        if not s:
            s = self

        leng = b''
        while len(leng) < 4:
            leng += s.recv(1)

        data = b''
        while len(data) < int(leng):
            data += s.recv(1)

        return pickle.loads(data)

    def recieve_pickle(self, sock=None):
        if self.client:
            prot = self.prot
        else:
            prot = self.protocols[sock]
        if prot == self.dh_aes:
            return self.__recieve_pickle_dh_aes(sock)
        elif prot == self.rsa:
            return self.__recieve_pickle_rsa(sock)

    def send_pickle(self, obj, sock=None):
        prot = self.prot if self.client else self.protocols[sock]

        if prot == self.dh_aes:
            return self.__send_pickle_dh_aes(obj, sock)
        elif prot == self.rsa:
            return self.__send_pickle_rsa(obj, sock)

    def __get_bdata(self, sock):
        leng = b''
        while len(leng) < 4:
            leng += sock.recv(1)

        data = b''
        while len(data) < int(leng):
            try:
                chunk = sock.recv(1)
                data += chunk

                if "#@@!?#%@##".encode() in data:
                    break

            except ConnectionResetError:
                return None, None, None  # socket was closed for some other reason
            except socket.timeout:
                return None, None, None

            except Exception:
                continue
        return data

    def timed_recieve(self, sock=None, time=0.001):
        prot = self.prot if self.client else self.protocols[sock]

        if not sock:
            sock = self

        if not prot:
            return self.__timed_recieve_normal(sock, time)

        elif prot == self.dh_aes:
            return self.__timed_recieve_dh_aes(sock, time)
        elif prot == self.rsa:
            return self.__timed_recieve_rsa(sock, time)

    def __timed_recieve_dh_aes(self, sock, time):
        if self.client:
            aes = AESCipher(self.public_key)
        else:
            aes = AESCipher(self.public_codes[sock])

        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.settimeout(time)

        data = self.__get_bdata(sock)

        data = data.split(b"#@@!?#%@")  # cleaning the data
        data = data[:-1]
        data = list(filter(None, data))

        to_ret = []
        for i in data:
            to_ret.append(aes.decrypt(i))

        return to_ret

    def __timed_recieve_rsa(self, sock, time):
        key = self.key_pair

        dec = PKCS1_OAEP.new(key)
        sock.settimeout(time)
        data = self.__get_bdata(sock)

        # write_to_log(sock.getpeername(),data)
        data = data.split("#@@!?#%@".encode())  # cleaning the data
        data = data[:-1]
        data = list(filter(None, data))

        to_ret = []
        for i in data:
            to_ret.append(dec.decrypt(i))

        return to_ret

    def __timed_recieve_normal(self, sock, time):
        sock.settimeout(time)
        data = self.__get_bdata(sock)

        data = data.split("#@@!?#%@".encode())  # cleaning the data
        data = data[:-1]
        data = list(filter(None, data))

        to_ret = []
        for i in data:
            to_ret.append(i)

        return to_ret

    def handle_logging(self,data=list[str,str,str],sock:socket.socket=None):
        sender = sock.getpeername() if sock != self else 'SERVER'
        cmd = data.pop(0)
        if cmd == 'ERROR':
            logging.error(f'{datetime.datetime.now()}-{sender}: {cmd} {str(data)[1:-2]}')
        else:
            logging.debug(f'{datetime.datetime.now()}-{sender}: {cmd} {str(data)[1:-2]}')

