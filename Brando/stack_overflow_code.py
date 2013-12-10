from Crypto.Protocol.KDF import PBKDF2
from Crypto.PublicKey import RSA
import DarkCloudCryptoLib as dcCryptoLib

def makeRSAkey(password, salt):
    master_key = PBKDF2(password, salt, count=10000)  # bigger count = better
    def my_rand(n):
    	# PBKDF2 with count=1 and a variable salt makes a handy key-expander
    	my_rand.counter += 1
    	#return PBKDF2(master_key, salt, dkLen=n, count=1)
    	return PBKDF2(master_key, "my_rand:%d" % my_rand.counter, dkLen=n, count=1)
    my_rand.counter = 0
    RSA_key = RSA.generate(2048, randfunc=my_rand)
    return RSA_key


password = "swordfish"   # for testing
salt = "yourAppName"     # replace with random salt if you can store one

key1 = makeRSAkey(password, salt)
key2 = makeRSAkey(password, salt)

print dcCryptoLib.equalRSAKeys(key1, key2)
