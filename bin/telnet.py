# Slightly modified version of https://github.com/rakeshsukla53/Socket-Programming-Python/blob/master/socket_telnet.py

import socket, select, sys

#if __name__ == "__main__":
def __main__(argv):
	
	if(len(argv) < 4):
		print ('Usage:')
		print ('telnet hostname port')
		print ('eg. telnet towel.blinkenlights.nl 23')
		return
	
	host = argv[2]
	port = int(argv[3])
	
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(2)
	
	# connect to remote host
	try :
		s.connect((host, port))
	except :
		print ('Unable to connect')
		sys.exit()
	
	print ('Connected to remote host')
	
	while 1:
		socket_list = [sys.stdin, s]
		
		# Get the list sockets which are readable
		read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
		
		for sock in read_sockets:
			#incoming message from remote server
			if sock == s:
				data = sock.recv(1920)
				if not data:
					print ('Connection closed')
					return
#					sys.exit()
				else :
					#print data
					sys.stdout.write(data)
			
			#user entered a message
			else :
				msg = sys.stdin.readline()
				s.send(msg)

