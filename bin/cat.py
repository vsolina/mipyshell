import sys


def __main__(args):
	if len(args) < 3:
		return

	if args[2] == ">" or args[2] == ">>":
		if args[2] == ">>":
			f = open(args[2], "a")
			f.seek(0, 2)
		else:
			f = open(args[3], "wt")
		
		wrote = 0
		try:
			while True:
				k = sys.stdin.read(1)
#				print (k)
				wrote += sys.stdout.write(k)
				if k == '\x1b':
					break
				f.write(k)
		except KeyboardInterrupt:
			pass
		f.close()
		print ("Wrote {}".format(wrote))
		return
	
	f = open(args[2], "rt")
	for l in f:
		if l[-1] == '\n':
			l = l[:-1]
		print (l)
	f.close()

