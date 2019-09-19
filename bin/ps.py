from sh import _active_threads
import time


def __main__(args):
	print ("TID		TIME		COMMAND")
	for tid in _active_threads.keys():
		t = _active_threads[tid]
		stime = t[1]
		running = (time.ticks_us() - stime) / 1000000
		print ("{}	{}s		{}".format(tid, round(running,2), t[0]))

