from Crypto.PublicKey import RSA
from Crypto import Random
import hashlib
import sys
import os


random_generator = Random.new().read
key = RSA.generate(1024, random_generator)
exportedKey = key.exportKey('DER', os.urandom(32), pkcs=1)
key = RSA.importKey(exportedKey)
print key
