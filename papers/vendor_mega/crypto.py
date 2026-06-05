import pyaes
import json
import base64
import struct
import binascii
import random
import sys

if sys.version_info < (3, ):
    def makebyte(x):
        return x
    def makestring(x):
        return x
else:
    import codecs
    def makebyte(x):
        return codecs.latin_1_encode(x)[0]
    def makestring(x):
        return codecs.latin_1_decode(x)[0]


def aes_cbc_encrypt(data, key):
    iv = b'\x00' * 16
    cipher = pyaes.AESModeOfOperationCBC(key, iv)
    return cipher.encrypt(data)


def aes_cbc_decrypt(data, key):
    iv = b'\x00' * 16
    aes = pyaes.AES(key)
    plaintext = b''
    prev = iv
    for i in range(0, len(data), 16):
        block = data[i:i+16]
        decrypted = aes.decrypt(block)
        plaintext += bytes(a ^ b for a, b in zip(decrypted, prev))
        prev = block
    return plaintext


def aes_cbc_encrypt_a32(data, key):
    return str_to_a32(aes_cbc_encrypt(a32_to_str(data), a32_to_str(key)))


def aes_cbc_decrypt_a32(data, key):
    return str_to_a32(aes_cbc_decrypt(a32_to_str(data), a32_to_str(key)))


class Counter128:
    def __init__(self, initial_value=0):
        self._counter = initial_value.to_bytes(16, 'big')
    def __call__(self):
        result = self._counter
        val = int.from_bytes(self._counter, 'big') + 1
        if val >= 2**128:
            val = 0
        self._counter = val.to_bytes(16, 'big')
        return result


def new_aes_ctr(key, initial_counter):
    counter = Counter128(initial_counter)
    return pyaes.AESModeOfOperationCTR(key, counter=counter)


def new_aes_cbc(key, iv):
    return pyaes.AESModeOfOperationCBC(key, iv)


class ECB:
    def __init__(self, key):
        self._ecb = pyaes.AESModeOfOperationECB(key)
    def encrypt(self, data):
        result = b''
        for i in range(0, len(data), 16):
            result += self._ecb.encrypt(data[i:i+16])
        return result

def new_aes_ecb(key):
    return ECB(key)


def stringhash(str, aeskey):
    s32 = str_to_a32(str)
    h32 = [0, 0, 0, 0]
    for i in range(len(s32)):
        h32[i % 4] ^= s32[i]
    for r in range(0x4000):
        h32 = aes_cbc_encrypt_a32(h32, aeskey)
    return a32_to_base64((h32[0], h32[2]))


def prepare_key(arr):
    pkey = [0x93C467E3, 0x7DB0C7A4, 0xD1BE3F81, 0x0152CB56]
    for r in range(0x10000):
        for j in range(0, len(arr), 4):
            key = [0, 0, 0, 0]
            for i in range(4):
                if i + j < len(arr):
                    key[i] = arr[i + j]
            pkey = aes_cbc_encrypt_a32(pkey, key)
    return pkey


def encrypt_key(a, key):
    return sum((aes_cbc_encrypt_a32(a[i:i + 4], key)
                for i in range(0, len(a), 4)), ())


def decrypt_key(a, key):
    return sum((aes_cbc_decrypt_a32(a[i:i + 4], key)
                for i in range(0, len(a), 4)), ())


def encrypt_attr(attr, key):
    attr = makebyte('MEGA' + json.dumps(attr))
    if len(attr) % 16:
        attr += b'\0' * (16 - len(attr) % 16)
    return aes_cbc_encrypt(attr, a32_to_str(key))


def decrypt_attr(attr, key):
    attr = aes_cbc_decrypt(attr, a32_to_str(key))
    attr = makestring(attr)
    attr = attr.rstrip('\0')
    return json.loads(attr[4:]) if attr[:6] == 'MEGA{"' else False


def a32_to_str(a):
    return struct.pack('>%dI' % len(a), *a)


def str_to_a32(b):
    if isinstance(b, str):
        b = makebyte(b)
    if len(b) % 4:
        b += b'\0' * (4 - len(b) % 4)
    return struct.unpack('>%dI' % (len(b) / 4), b)


def mpi_to_int(s):
    return int(binascii.hexlify(s[2:]), 16)


def extended_gcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = extended_gcd(b % a, a)
        return (g, x - (b // a) * y, y)


def modular_inverse(a, m):
    g, x, y = extended_gcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m


def base64_url_decode(data):
    data += '=='[(2 - len(data) * 3) % 4:]
    for search, replace in (('-', '+'), ('_', '/'), (',', '')):
        data = data.replace(search, replace)
    return base64.b64decode(data)


def base64_to_a32(s):
    return str_to_a32(base64_url_decode(s))


def base64_url_encode(data):
    data = base64.b64encode(data)
    data = makestring(data)
    for search, replace in (('+', '-'), ('/', '_'), ('=', '')):
        data = data.replace(search, replace)
    return data


def a32_to_base64(a):
    return base64_url_encode(a32_to_str(a))


def get_chunks(size):
    p = 0
    s = 0x20000
    while p + s < size:
        yield (p, s)
        p += s
        if s < 0x100000:
            s += 0x20000
    yield (p, size - p)


def make_id(length):
    text = ''
    possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    for i in range(length):
        text += random.choice(possible)
    return text
