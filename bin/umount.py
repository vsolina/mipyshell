import uos
from sh import _vfses
import gc

def __main__(args):
	if len(args) < 3:
		print ("Usage:")
		print ("umount <path>")
		print ("umount /ram0")
		return
	path = args[2]
	if path in _vfses:
		vfs, bdev = _vfses[path]
		uos.umount(vfs)
		del _vfses[path]
		gc.collect()
	else:
		uos.umount(args[2])
