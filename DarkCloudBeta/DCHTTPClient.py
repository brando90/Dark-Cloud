#!/usr/bin/env python

import httplib
import sys
from urllib import urlencode

# http server ip addr & port

class DCHTTPClient():

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

	def __init__(self, host, port):
		self.connection = httplib.HTTPConnection(host, port)

	# Request constructor: 
	# HTTPConnection.request(method, url[, body[, headers]])

	# Create
	def sendCreateRequest(self, encryptedPath, isFile=False, isDir=False, encryptedContents=None):
		url = encryptedPath + urlencode({Method:Create, File:isFile, Dir:isDir})
		self.connection.request(PUT, url, encryptedContents)
		return self.connection.getresponse().read()

	# Read
	def sendReadRequest(self, encryptedPath):
		url = encryptedPath + urlencode({Method:Read})
		self.connection.request(GET, url)
		return self.connection.getresponse().read()

	# Write
	def sendWriteRequest(self, encryptedPath, newEncryptedContents):
		url = encryptedPath + urlencode({Method:Write})
		self.connection.request(POST, url, newEncryptedContents)
		return self.connection.getresponse().read()

	# Rename
	def sendRenameRequest(self, encryptedPath, newEncryptedPath):
		url = encryptedPath + urlencode({Method:Rename})
		self.connection.request(POST, url, newEncryptedPath)
		return self.connection.getresponse().read()

	# Delete
	def sendDeleteRequest(self, encryptedPath):
		url = encryptedPath + urlencode({Method:Delete})
		self.connection.request(DELETE, url)
		return self.connection.getresponse().read()
