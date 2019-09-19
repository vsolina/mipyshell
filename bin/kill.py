from sh import _active_threads, _active_threads_ksignal


def __main__(args):
	global _active_threads
	global _active_threads_ksignal
	if len(args) < 3:
		print ("Thread ID is required")
		return

	tid = int(args[2])
	if tid not in _active_threads or tid not in _active_threads_ksignal:
		print ("No such thread {}".format(tid))
		print ("Available {}".format(_active_threads_ksignal.keys()))
	_active_threads_ksignal[tid] = 9

