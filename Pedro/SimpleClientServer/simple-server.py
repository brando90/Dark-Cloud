#!/usr/bin/env python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

	# handle GET method
	def do_GET(self):
		rootdir = '/Users/pedrocattori/DarkCloud/Pedro/SimpleClientServer/'
		try:
			print('requested path: ' + rootdir + self.path)
			f = open(rootdir + self.path) # open requested file

			# send code 200 response
			self.send_response(200)

			# send header first
			self.send_header('Content-type', 'text')
			self.end_headers()

			# send file content to client
			self.wfile.write(f.read())
			f.close()
			return

		except IOError:
			self.send_error(404, 'file not found')

def run():
	print('http server is starting...')

	# ip and port
	server_address = ('127.0.0.1', 8080)
	httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
	print('http server is running...')
	httpd.serve_forever()

if __name__ == '__main__':
	run()