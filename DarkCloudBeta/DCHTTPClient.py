#!/usr/bin/env python

import httplib
import sys
from urllib import urlencode

# *** HTTP methods ***
PUT = 'PUT'
GET = 'GET'
POST = 'POST'
DELETE = 'DELETE'
# --------------------

# *** Methods ***
Create = 'create'
Read = 'read'
Write = 'write'
Rename = 'rename'
Delete = 'delete'
# ---------------

# *** Query string keys ***
Method = 'method'
File = 'file'
Dir = 'dir'
# -------------------------

class DCHTTPClient():
	def __init__(self, host, port):
		self.connection = httplib.HTTPConnection(host, port)

	# Request constructor: 
	# HTTPConnection.request(method, url[, body[, headers]])

	# Create --> PUT
	def sendCreateRequest(self, encryptedPath, isFile=False, isDir=False, encryptedContents=None):
		url = encryptedPath + '?' + urlencode({Method:Create, File:isFile, Dir:isDir})
		self.connection.request(PUT, url, encryptedContents)
		return self.connection.getresponse().read()

	# Read --> GET
	def sendReadRequest(self, encryptedPath):
		url = encryptedPath + '?' + urlencode({Method:Read})
		self.connection.request(GET, url)
		return self.connection.getresponse().read()

	# Write --> POST
	def sendWriteRequest(self, encryptedPath, newEncryptedContents):
		url = encryptedPath + '?' + urlencode({Method:Write})
		self.connection.request(POST, url, newEncryptedContents)
		return self.connection.getresponse().read()

	# Rename --> POST
	def sendRenameRequest(self, encryptedPath, newEncryptedPath):
		url = encryptedPath + '?' + urlencode({Method:Rename})
		self.connection.request(POST, url, newEncryptedPath)
		return self.connection.getresponse().read()

	# Delete --> DELETE
	def sendDeleteRequest(self, encryptedPath):
		url = encryptedPath + '?' + urlencode({Method:Delete})
		self.connection.request(DELETE, url)
		return self.connection.getresponse().read()

# ----------------------------------


# *** Run Dark Cloud Beta Client ***

def run():
	# ip & port
	client = DCHTTPClient(sys.argv[1], sys.argv[2])
	while True:
		method = raw_input('request DC method (create, read, write, rename, delete): \n $ ')
		path = raw_input('with path: \n $ ')
		if method == Create:
			isFile = raw_input("should a file be created here? ('yes' or 'no'): \n $ ")
			isDir = raw_input("should a directory be created here? ('yes' or 'no'): \n $ ")
			contents = None
			if isFile == 'yes':
				contents = raw_input("initial contents of file: \n $ ")
				print client.sendCreateRequest(path, isFile=True, isDir=False, encryptedContents=contents)
			elif isDir == 'yes':
				print client.sendCreateRequest(path, isFile=False, isDir=True)
			else:
				raise ValueError('can only create EITHER a file OR a directory')
		elif method == Read:
			print client.sendReadRequest(path)
		elif method == Write:
			newContents = raw_input('new contents: \n $ ')
			print client.sendWriteRequest(path, newContents)
		elif method == Rename:
			newName = raw_input('new name: \n $ ')
			print client.sendRenameRequest(path, newName)
		elif method == Delete:
			confirm = raw_input("are you sure you want do delete " + path + "? ('yes' or 'no'): \n $ ")
			if confirm == 'yes':
				print client.sendDeleteRequest(path)
			elif confirm == 'no':
				print path + ' not deleted'
			else:
				print path + " not deleted. Please say 'yes' or 'no' next time"
		else:
			raise ValueError('method must be one of: create, read, write, rename, delete')



if __name__ == '__main__':
	run()
