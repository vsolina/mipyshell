from sh import human
import os


def __main__(args):
	path = ""
	if len(args) > 2:
		path = args[2]
	
	if len(path) == 0:
		path = os.getcwd()
	
	print ("d .")
	if path != "/":
		print ("d ..")
		if path.endswith("/"):
			path = path[:-1]
	
	path_pre = path + "/" if len(path) > 0 and path.endswith("/") == False else ""

	items = [pt for pt in os.ilistdir(path)]
	for pt in sorted(items):
		f = pt[0]
		type = pt[1]
		inode = pt[2]
		fsize = None
		if len(pt) > 3:
			fsize = pt[3]
		
		type = "f" if type == 32768 else "d"
		if fsize is None:
			type = "M"
		size = 0
		if type == "f":
#			print ("opening {}".format(path_pre + f))
			o = open(path_pre + f, "rb")
			size = human(o.seek(10000000))
			o.close()
		print ("{} {}	{}".format(type, size, f))

