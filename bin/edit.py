import pye
import sys

def __main__(args):
	if len(args) < 3:
		print ("Usage:")
		print ("edit <path>")
		return
	
	pth = args[2]
	pye.pye(pth)
	del sys.modules['pye']

