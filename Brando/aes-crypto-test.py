from Crypto.Cipher import AES

key = "This is a key123"
iv = "This is an IV456"
mode = AES.MODE_CBC

obj = AES.new(key, mode, iv)

plaintext = "The answer is no"
ciphertext = obj.encrypt(plaintext)

obj2 = AES.new('This is a key123', AES.MODE_CBC, 'This is an IV456')
p = obj2.decrypt(ciphertext)

print ciphertext
print plaintext
print p
print plaintext == p

