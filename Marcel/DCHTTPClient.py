#!/usr/bin/env python

import httplib
import sys
import json
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
		print "create request sent"
		url = encryptedPath
		headers = {'content-length':0, 
			'query':urlencode({Method:Create, File:isFile, Dir:isDir}),
			'url':url}
		# if encryptedContents != None:
		# 	headers['content-length'] = len(encryptedContents)
		print "headers: " + repr(headers)
		self.connection.request(PUT, '/', encryptedContents, headers)
		return self.connection.getresponse().read()

	# Read --> GET
	def sendReadRequest(self, encryptedPath):
		print "read request sent"
		url = encryptedPath
		headers = {'query-string':urlencode({Method:Read}), 'url':url}
		self.connection.request(GET, '/', None, headers)
		response = self.connection.getresponse().read()
		if response[:5] == 'file:':
			return response[5:]
		elif response[:4] == 'dir:':
			return json.loads(response[4:])
		else:
			raise ValueError('Server responded with a non-file, non-directory')
		

	# Write --> POST
	def sendWriteRequest(self, encryptedPath, newEncryptedContents):
		print "write request sent"
		url = encryptedPath
		headers = {'query-string':urlencode({Method:Write}),
		'url':url} # 'content-length':len(newEncryptedContents), 
		self.connection.request(POST, '/', newEncryptedContents, headers)
		return self.connection.getresponse().read()

	# Rename --> POST
	def sendRenameRequest(self, encryptedPath, newEncryptedPath):
		print "rename request sent"
		url = encryptedPath
		headers = {'query-string':urlencode({Method:Rename}), 'url':url}
		self.connection.request(POST, '/', newEncryptedPath, headers)
		return self.connection.getresponse().read()

	# Delete --> DELETE
	def sendDeleteRequest(self, encryptedPath):
		print "delete request sent"
		url = encryptedPath
		headers = {'query-string':urlencode({Method:Delete}), 'url':url}
		self.connection.request(DELETE, '/', None, headers)
		return self.connection.getresponse().read()

# ----------------------------------


# *** Run Dark Cloud Beta Client ***

def run():
	try:
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
	except EOFError:
		print '\nClient closed'

if __name__ == '__main__':
	run()
