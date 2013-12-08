#!/usr/bin/env python

import httplib
import sys

# http server ip addr & port

class DCHTTPClient():

	# *** Methods ***
	Create = 'create'
	Read = 'read'
	Write = 'write'
	Rename = 'rename'
	Delete = 'delete'
	# ---------------

	def __init__(self, host, port):
		self.connection = httplib.HTTPConnection(host, port)

	# Request constructor: 
	# HTTPConnection.request(method, url[, body[, headers]])

	# Create
	def sendCreateRequest(self, encryptedPath, encryptedContents=None):
		self.connection.request(Create, encryptedPath, encryptedContents)
		return self.connection.getresponse().read()

	# Read
	def sendReadRequest(self, encryptedPath):
		self.connection.request(Read, encryptedPath)
		return self.connection.getresponse().read()

	# Write
	def sendWriteRequest(self, encryptedPath, newEncryptedContents):
		self.connection.request(Write, encryptedPath, newEncryptedContents)
		return self.connection.getresponse().read()

	# Rename
	def sendRenameRequest(self, encryptedPath, newEncryptedPath):
		self.connection.request(Rename, encryptedPath, newEncryptedPath)
		return self.connection.getresponse().read()

	# Delete
	def sendDeleteRequest(self, encryptedPath):
		self.connection.request(Delete, encryptedPath)
		return self.connection.getresponse().read()
