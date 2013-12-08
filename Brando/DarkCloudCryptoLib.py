import os, random, struct, sys
import filecmp
from Crypto.Cipher import AES

class Key:
    def __init__(self, password, key_filename):
        kf = open(key_filename)


def makeKeyFile(password, key_filename, dir_name):
    

def encrypt_file(password, key_filename, file_name):
    iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(file_name)

    with open(file_name, 'r') as f:
        file_data = f.read()
        delta = 0
        if len(file_data) % 16 != 0:
            delta = (16 - len(file_data)) % 16
            file_data += (' ' * delta)
        meta_data = str(filesize)+"\n"+str(iv)+"\n"+str(delta)
        return encryptor.encrypt(file_data)

def decrypt_file(key, file_name):
    with open(file_name, 'r') as f:
        origsize = struct.unpack('<Q', f.read(struct.calcsize('Q')))[0]
        iv = f.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)
        while True:
            file_data = f.read()
            outfile.write(decryptor.decrypt(chunk))

        outfile.truncate(origsize)


