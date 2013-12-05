#!/usr/bin/env python

import httplib
import sys

# get http server ip
server_host = sys.argv[1]
server_port = sys.argv[2]

# create connection
conn = httplib.HTTPConnection(server_host, server_port)

while True:
	cmd = raw_input('input command (ex. GET hello-world.txt): ')
	cmd = cmd.split()

	if cmd[0] == 'exit': # type exit to end connection
		break

	# request command to server
	conn.request(cmd[0], cmd[1])

	# get response from server
	rsp = conn.getresponse()

	# print server response and data
	print(rsp.status, rsp.reason)
	data_received = rsp.read()
	print(data_received)

conn.close()