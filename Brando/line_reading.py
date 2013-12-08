
with open("text.txt", 'r') as file:
	line = file.readline()
	while len(line) != 0:
		print line
		line = file.readline()