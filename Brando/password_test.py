from Crypto.Cipher import AES
import hashlib

password = 'kitty'
key = hashlib.sha256(password).digest()
IV = 16 * '\x00'           

mode = AES.MODE_CBC
encryptor = AES.new(key, mode, IV)

text = 'j' * 64 + 'i' * 128
ciphertext = encryptor.encrypt(text)



print ciphertext