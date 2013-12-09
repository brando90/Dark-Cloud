
from Crypto.PublicKey import RSA
from Crypto.Hash import MD5
from Crypto import Random

#Generate a key object that holds the RSA keys.
random_generator = Random.new().read #crypto's random generator
key = RSA.generate(1024, random_generator)

#Some methods of keys
# key.can_encrypt()
# True
# >>> key.can_sign()
# True
# >>> key.has_private()
# True

#ENCRYPTION
public_key = key.publickey()
print "TYPE: ", public_key
text = 'abcdefgh'
enc_data = public_key.encrypt(text, 32)
print "<------------RSA Scrypt started running------------>"
print
print "encrypted data:",enc_data
print

#DECRYPTION
decrypted_data = key.decrypt(enc_data)
print
print "original data: ",text
print
print "decrypted data: ",decrypted_data
print
print "data equal: ",text == decrypted_data
print

#SIGNING
hash_val = MD5.new(text).digest()
signature = key.sign(hash_val, '')
print
print "signature: ",signature

#VERIFYING
print
print "Verfification result: ",public_key.verify(hash_val, signature)
