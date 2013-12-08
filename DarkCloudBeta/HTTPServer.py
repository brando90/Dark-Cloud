#!/usr/bin/env python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os
import urllib
from urlparse import urlparse, parse_qs

class DCHTTPRequestHandler(BaseHTTPRequestHandler):
	
	# *** Methods ***
	Create = 'create'
	Read = 'read'
	Write = 'write'
	Rename = 'rename'
	Delete = 'delete'
	# ---------------

	# *** Query string keys ***
	Method = 'method'
	EncryptedKeyFile = 'keyfile'
	NewFile = 'file'
	NewDir = 'dir'
	# -------------------------


	# *** 'Overridden' methods ***

	def __init__(self, *args, **kwargs):
		BaseHTTPServer.HTTPServer.__init__(self, *args, **kwargs)
		self.url = None

	def setup(self):
		#TODO: Verify this gets called on a per-request basis
		BaseHTTPRequestHandler.setup(self)
		self.url = self.parseURL()

	# Create
	def do_PUT(self):
		path = self.url.path
		method = self.getQueryMethod()
		encryptedKeyFile = getEncryptedKeyFile()
		contents = getContents()
		signedParentDir = getSignedParentDir()

		if method != Create:
			self.send_error(405, "PUT requests must have method set to 'create'")

		if newFile():
			createFile(path)
		elif newDir():
			createDir(path)
		else:
			self.send_error(400, "must set either 'file' or 'dir' to 'true' in PUT requests (not both)")
		return

	# Read
	def do_GET(self):
		# Parse request
		path = self.url.path
		method = self.getQueryMethod()
		withKeyFile = self.getQueryArg(KeyFile)
		
		if method != Read:
			self.send_error(405, "GET requests must have method set to 'read'")

		if os.path.isfile(path):
			self.readFile(path, withKeyFile)
		elif os.path.isdir(path, withKeyFile):
			self.readDir(path)
		else:
			self.send_error(404, 'file/dir not found')

	# Write, Rename
	def do_POST(self):
		pass

	# Delete
	def do_DELETE(self):
		path = self.url.path
		method = self.getQueryMethod()


		if method != Delete:
			self.send_error(405, "Delete requests must have method set to 'delete'")

		if os.path.isfile(path):
			self.deleteFile(path)
		elif os.path.isdir(path):
			self.deleteDir(path)
		else:
			self.send_error(404, 'file/dir not found')
		return

	# ---------------


	# *** Helpers ***

	def parseURL(self):
		#TODO: sanitize path
		return urlparse(self.path)

	def getQueryArg(self, key):
		return parse_qs(self.url.query).get(key)

	def getMethod(self):
		return self.getQueryArg(Method)

	def newFile(self):
		return self.getQueryArg(NewFile)

	def newDir(self):
		return self.getQueryArg(NewDir)

	def getEncryptedKeyFile(self):
		return self.getQueryArg(EncryptedKeyFile)

	def getContents(self):
		pass

	def getSignedParentDir(self):
		pass

	def updateSignedParentDir(self, path):
		pass

	# ----------------------


	# *** Method helpers ***

	def createFile(self, path, encryptedContents):
		# create file, update parent directory signature
		fd = open(path, 'w+')
		os.write(fd, encryptedContents)
		updateSignedParentDir()

		self.send_response(200)

		fd.close()
		pass

	def createDir(self, path):
		# create dir, update parent directory signature
		pass

	def readFile(self, path, withKeyFile):
		# retrieve key file if asked to
		fd = open(path)

		self.send_response(200)
		#self.send_header('Content-type', 'text')
		#self.end_headers()

		self.wfile.write(fd.read())
		fd.close()
		return

	def readDir(self, path, withKeyFile):
		#TODO: send directory signature
		#TODO: retrieve keyfile if asked to
		ls = '\n'.join(os.listdir(path))

		self.send_response(200)
		#self.send_header('Content-type', 'text')
		#self.end_headers()

		self.wfile.write(ls)
		return

	def writeFile(self, path, newEncryptedContents):
		# write file contents
		fd = open(path)
		fd.seek(0)
		fd.write(newEncryptedContents)
		fd.truncate()

		self.send_response(200)

		fd.close()
		return

	def renameFileOrDir(self, path, newPath):
		# rename file or dir, update parent directory signature
		os.rename(path, newPath)
		updateSignedParentDir()

		self.send_response(200)
		return

	def deleteFile(self, path):
		# delete file, update parent directory signature
		os.remove(path)
		updateSignedParentDir()

		self.send_response(200)
		return

	def deleteDir(self, path):
		# delete dir, update parent directory signature
		os.rmdir(path)
		updateSignedParentDir()

		self.send_response(200)
		return

# ----------------------------------


# *** Run Dark Cloud Beta Server ***

def run():
	print('Dark Cloud Beta server is starting...')

	# ip and port
	server_address = ('127.0.0.1', 8080)
	httpd = HTTPServer(server_address, DCHTTPRequestHandler)
	print('Dark Cloud Beta server is now running...')
	httpd.serve_forever()

if __name__ == '__main__':
	run()