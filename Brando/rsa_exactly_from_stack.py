from Crypto.Protocol.KDF import PBKDF2
from Crypto.PublicKey import RSA
import DarkCloudCryptoLib as dcCryptoLib

password = "swordfish"   # for testing
salt = "yourAppName"     # replace with random salt if you can store one

master_key = PBKDF2(password, salt, count=10000)  # bigger count = better

def my_rand(n):
    # PBKDF2 with count=1 and a variable salt makes a handy key-expander
    my_rand.counter += 1
    #return PBKDF2(master_key, salt, dkLen=n, count=1)
    return PBKDF2(master_key, "my_rand:%d" % my_rand.counter, dkLen=n, count=1)

my_rand.counter = 0
RSA_key1 = RSA.generate(2048, randfunc=my_rand)
my_rand.counter = 0
RSA_key2 = RSA.generate(2048, randfunc=my_rand)
print dcCryptoLib.equalRSAKeys(RSA_key1, RSA_key2)