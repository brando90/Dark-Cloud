#!/usr/bin/env python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

	# handle GET method
	def do_GET(self):
		rootdir = '/Users/pedrocattori/DarkCloud/Pedro/SimpleClientServer/'
		try:
			absolute_path = rootdir + self.path
			print('requested path: ' + absolute_path)
			if os.path.isfile(absolute_path):
				self.getFile(absolute_path)
			elif os.path.isdir(absolute_path):
				self.getDir(absolute_path)
			else:
				self.send_error(404, 'file/dir not found')
			return
		except IOError:
			self.send_error(404, 'file/dir not found')


	# *** HELPERS ***
	def getFile(self, absolute_path):
		f = open(absolute_path)
		# send code 200 response
		self.send_response(200)

		# send header first
		self.send_header('Content-type', 'text')
		self.end_headers()

		# send file content to client
		self.wfile.write(f.read())
		f.close()
		return

	def getDir(self, absolute_path):
		ls = '\n'.join(os.listdir(absolute_path))

		# send code 200 response
		self.send_response(200)

		# send header first
		self.send_header('Content-type', 'text')
		self.end_headers()

		self.wfile.write(ls)
		return


def run():
	print('http server is starting...')

	# ip and port
	server_address = ('127.0.0.1', 8080)
	httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
	print('http server is running...')
	httpd.serve_forever()

if __name__ == '__main__':
	run()