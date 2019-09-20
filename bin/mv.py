import os


def __main__(args):
	path = args[2]
	path2 = args[3]
	src_name = args[2].split("/")[-1]
	
	try:
		os.listdir(path2)
		path2 += "/" + src_name
	except OSError:
		pass
	print ("renaming {} to {}".format(path, path2))
	os.rename(path, path2)

