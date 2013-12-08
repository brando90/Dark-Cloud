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
	NewFile = 'file'
	NewDir = 'dir'
	# -------------------------


	# *** 'Overridden' methods ***

	def __init__(self, *args, **kwargs):
		BaseHTTPServer.HTTPServer.__init__(self, *args, **kwargs)
		self.encryptedURL = None

	def setup(self):
		#TODO: Verify this gets called on a per-request basis
		BaseHTTPRequestHandler.setup(self)
		self.url = self.parseURL()

	# Create
	def do_PUT(self):
		encryptedPath = self.url.path
		method = self.getQueryMethod()
		encryptedContents = self.getEncryptedContents()

		if method != Create:
			self.send_error(405, "PUT requests must have method set to 'create'")

		if os.path.isfile(encryptedPath) or os.path.isdir(encryptedPath):
			self.send_error(403, "A file or directory already exists at given path")

		if newFile():
			self.createFile(encryptedPath, encryptedContents)
		elif newDir():
			self.createDir(encryptedPath, encryptedContents)
		else:
			self.send_error(400, "must set either 'file' or 'dir' to 'true' in PUT requests (not both)")
		return

	# Read
	def do_GET(self):
		encryptedPath = self.url.path
		method = self.getQueryMethod()
		
		if method != Read:
			self.send_error(405, "GET requests must have method set to 'read'")

		if os.path.isfile(encryptedPath):
			self.readFile(encryptedPath)
		elif os.path.isdir(encryptedPath):
			self.readDir(encryptedPath)
		else:
			self.send_error(404, 'file/dir not found')
		return

	# Write, Rename
	def do_POST(self):
		encryptedPath = self.url.path
		method = self.getQueryMethod()
		newEncryptedContents = self.getEncryptedContents()
		newEncryptedPath = self.getEncryptedPath

		if method == Write:
			if os.path.isfile(encryptedPath):
				self.writeFile(encryptedPath, newEncryptedContents)
			else:
				self.send_error(405, "Path for POST request with 'write' method must point to a file")
		elif method == Rename:
			self.renameFileOrDir(encryptedPath, newEncryptedPath)
		else:
			self.send_error(405, "POST requests must have method set to 'write' or 'rename'")
		return

	# Delete
	def do_DELETE(self):
		encryptedPath = self.url.path
		method = self.getQueryMethod()

		if method != Delete:
			self.send_error(405, "Delete requests must have method set to 'delete'")

		if os.path.isfile(encryptedPath):
			self.deleteFile(encryptedPath)
		elif os.path.isdir(encryptedPath):
			self.deleteDir(encryptedPath)
		else:
			self.send_error(404, 'file/dir not found')
		return

	# ---------------


	# *** Helpers ***

	def parseURL(self):
		return urlparse(self.path)

	def getQueryArg(self, key):
		return parse_qs(self.encryptedURL.query).get(key)

	def getMethod(self):
		return self.getQueryArg(Method)

	def newFile(self):
		return self.getQueryArg(NewFile)

	def newDir(self):
		return self.getQueryArg(NewDir)

	def getEncryptedContents(self):
		encryptedContentLength = int(self.headers.getheader('content-length'))
		return self.rfile.read(encryptedContentLength)

	# ----------------------


	# *** Method helpers ***

	def createFile(self, encryptedPath, encryptedContents):
		# create file
		fd = open(encryptedPath, 'w+')
		os.write(fd, encryptedContents)

		self.send_response(200)

		fd.close()
		return

	def createDir(self, encryptedPath):
		# create dir
		os.mkdir(encryptedPath)

		self.send_response(200)
		return

	def readFile(self, encryptedPath):
		fd = open(encryptedPath)

		self.send_response(200)
		self.send_header('Content-type', 'text')
		self.end_headers()

		self.wfile.write(fd.read())
		fd.close()
		return

	def readDir(self, encryptedPath):
		ls = os.listdir(encryptedPath)

		self.send_response(200)
		self.send_header('Content-type', 'text')
		self.end_headers()

		self.wfile.write(repr(ls))
		return

	def writeFile(self, encryptedPath, newEncryptedContents):
		# overwrite file contents
		fd = open(encryptedPath)
		fd.seek(0)
		fd.write(newEncryptedContents)
		fd.truncate()

		self.send_response(200)

		fd.close()
		return

	def renameFileOrDir(self, encryptedPath, newPath):
		# rename file or dir
		os.rename(encryptedPath, newPath)

		self.send_response(200)
		return

	def deleteFile(self, encryptedPath):
		# delete file
		os.remove(encryptedPath)

		self.send_response(200)
		return

	def deleteDir(self, encryptedPath):
		# delete dir
		os.rmdir(encryptedPath)

		self.send_response(200)
		return

# ----------------------------------


# *** Run Dark Cloud Beta Server ***

def run():
	# ip and port
	server_address = ('127.0.0.1', 8080)
	print('Dark Cloud Beta server is starting at: ' + repr(server_address))
	httpd = HTTPServer(server_address, DCHTTPRequestHandler)
	print('Dark Cloud Beta server is now running...')
	httpd.serve_forever()

if __name__ == '__main__':
	run()