#!/usr/bin/env python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os
import sys
import urllib
import json
from urlparse import urlparse, parse_qs

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

class DCHTTPRequestHandler(BaseHTTPRequestHandler):
	# *** 'Overridden' methods ***

	def __init__(self, *args):
		BaseHTTPRequestHandler.__init__(self, *args)
		self.encryptedURL = None
		self.root = os.getcwd()

	# Create
	def do_PUT(self):
		self.encryptedURL = self.parseURL()
		encryptedPath = self.encryptedURL.path
		method = self.getMethod()
		encryptedContents = self.getEncryptedBody()
		isFile = self.toBoolean(self.newFile())
		isDir = self.toBoolean(self.newDir())

		if method != Create:
			self.send_error(405, "PUT requests must have method set to 'create'")

		if os.path.isfile(encryptedPath) or os.path.isdir(encryptedPath):
			self.send_error(403, "A file or directory already exists at given path")

		if isFile:
			self.createFile(encryptedPath, encryptedContents)
		elif isDir:
			self.createDir(encryptedPath, encryptedContents)
		else:
			self.send_error(400, "must set either 'file' or 'dir' to 'true' in PUT requests (not both)")
		return

	# Read
	def do_GET(self):
		self.encryptedURL = self.parseURL()
		encryptedPath = self.encryptedURL.path
		method = self.getMethod()
		
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
		self.encryptedURL = self.parseURL()
		encryptedPath = self.encryptedURL.path
		method = self.getMethod()
		newEncryptedContents = None # initialized if method is Write
		newEncryptedPath = None # initialized if method is Rename

		if method == Write:
			newEncryptedContents = self.getEncryptedBody()
			if os.path.isfile(encryptedPath):
				self.writeFile(encryptedPath, newEncryptedContents)
			else:
				self.send_error(405, "Path for POST request with 'write' method must point to a file")
		elif method == Rename:
			newEncryptedPath = self.getEncryptedBody()
			self.renameFileOrDir(encryptedPath, newEncryptedPath)
		else:
			self.send_error(405, "POST requests must have method set to 'write' or 'rename'")
		return

	# Delete
	def do_DELETE(self):
		self.encryptedURL = self.parseURL()
		encryptedPath = self.encryptedURL.path
		method = self.getMethod()

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

	def toBoolean(self, string):
		if string == 'True':
			return True
		elif string == 'False':
			return False
		else:
			self.send_error(405, "Cannot convert '" + string + "' to a boolean")
			return

	def parseURL(self):
		return self.root + '/' + urlparse(self.path)

	def getQueryArg(self, key):
		print key + " : " + repr(parse_qs(self.encryptedURL.query).get(key)[0])
		return parse_qs(self.encryptedURL.query).get(key)[0]

	def getMethod(self):
		return self.getQueryArg(Method)

	def newFile(self):
		return self.getQueryArg(File)

	def newDir(self):
		return self.getQueryArg(Dir)

	def getEncryptedBody(self):
		encryptedContentLength = int(self.headers.getheader('content-length'))
		return self.rfile.read(encryptedContentLength)

	# ----------------------


	# *** Method helpers ***

	def createFile(self, encryptedPath, encryptedContents):
		# create file
		fd = open(encryptedPath, 'w+')
		fd.write(encryptedContents)

		self.send_response(200)

		fd.close()
		return

	def createDir(self, encryptedPath):
		# create dir
		os.mkdir(encryptedPath)

		self.send_response(200)
		return

	def readFile(self, encryptedPath):
		fd = open(encryptedPath, 'r')

		self.send_response(200)
		self.send_header('Content-type', 'text')
		self.end_headers()

		self.wfile.write('file:'+fd.read())
		fd.close()
		return

	def readDir(self, encryptedPath):
		ls = os.listdir(encryptedPath)

		self.send_response(200)
		self.send_header('Content-type', 'text')
		self.end_headers()

		self.wfile.write('dir:'+json.dumps(ls))
		return

	def writeFile(self, encryptedPath, newEncryptedContents):
		# overwrite file contents
		fd = open(encryptedPath, 'w')
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
	try:
		# ip and port
		host = '127.0.0.1'
		port = 8080
		if len(sys.argv) == 3:
			host = sys.argv[1]
			port = int(sys.argv[2])
		server_address = (host, port)
		print('Dark Cloud Beta server is starting at host:%s & port:%s' % server_address)
		httpd = HTTPServer(server_address, DCHTTPRequestHandler)
		print('Dark Cloud Beta server is now running...')
		httpd.serve_forever()
	except EOFError:
		print '\nServer closed'

if __name__ == '__main__':
	run()