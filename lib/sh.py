'''
Created by Valentin Solina, Part of mipyshell project
Super simple, MicroPython based, VT100 compatible POSIX shell imitation
'''

import uos
import os
import network
import micropython
import sys
import machine
import gc
import _thread
import time

next_thread_index = 1
_active_threads = {}
_active_threads_ksignal = {}

_vfses = {}

def root_info():
	info = uos.statvfs("/")
	block_size = info[0]
	fragment_size = info[1]
	fragment_count = info[2]
	free_block_count = info[3]
	
	print ("Root FS size {} Free {}".format(fragment_size * fragment_count, block_size * free_block_count))

def human(bytes):
	if bytes > 1024:
		if bytes > 1024 * 1024:
			return "{:.0f}MB".format(bytes / (1024 * 1024))
		else:
			return "{:.0f}KB".format(bytes / 1024)
	return "{}B".format(bytes)

def home_dir():
	return "/"

def abs_path(path):
	comp = path.split("/")
#	if comp[-1] != "":
#		path += "/"
	if comp[0] == "":
		return path
	if comp[0] == "~":
		return home_dir() + path[1:]
	cwd = os.getcwd()
	if cwd[0] != "/":
		cwd = "/" + cwd
	if cwd[-1] != "/" and path[0] != "/":
		cwd += "/"
	return cwd + path

def ls_imp(args):
	path = ""
	if len(args) > 1:
		path = args[1]
	
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

def mkdir_imp(args):
	path = args[1]
	print ("creating dir {}".format(abs_path(path)))
	os.mkdir(path)

def rmdir_imp(args):
	path = args[1]
	os.rmdir(path)

def mv_imp(args):
	path = args[1]
	path2 = args[2]
	src_name = args[1].split("/")[-1]
	
	try:
		os.listdir(path2)
		path2 += "/" + src_name
	except OSError:
		pass
	print ("renaming {} to {}".format(path, path2))
	os.rename(path, path2)

def cd_imp(args):
	path = args[1]
	os.chdir(path)

def pwd_imp(args):
	print(abs_path(os.getcwd()))

def rm_imp(args):
	path = args[1]
	os.remove(path)

def df_imp(args):
	_print_mount_stats("/")
	
	for pt in os.ilistdir("/"):
		f = pt[0]
		if len(pt) == 3:#Currently means vfs mount point
			print ("")
			_print_mount_stats("/"+f)

def _print_mount_stats(path):
	info = os.statvfs(path)
	block_size = info[0]
	fragment_size = info[1]
	fragment_count = info[2]
	free_block_count = info[3]
	
	print ("Filesystem '{}'	{}-blocks		total {}	free {}".format(path, block_size, fragment_count, free_block_count))
	used = (fragment_count - free_block_count) * block_size
	free = free_block_count * block_size
	print ("		USED {} bytes	{}".format(used, human(used)))
	print ("		FREE {} bytes	{}".format(free, human(free)))

def ps_imp(args):
	print ("TID		TIME		COMMAND")
	for tid in _active_threads.keys():
		t = _active_threads[tid]
		stime = t[1]
		running = (time.ticks_us() - stime) / 1000000
		print ("{}	{}s		{}".format(tid, round(running,2), t[0]))

def kill_imp(args):
	global _active_threads
	global _active_threads_ksignal
	tid = int(args[1])
	if tid not in _active_threads or tid not in _active_threads_ksignal:
		print ("No such thread {}".format(tid))
		print ("Available {}".format(_active_threads_ksignal.keys()))
	_active_threads_ksignal[tid] = 9

def cat_imp(args):
	if args[1] == ">" or args[1] == ">>":
		if args[1] == ">>":
			f = open(args[2], "a")
			f.seek(0, 2)
		else:
			f = open(args[2], "wt")
		
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
	
	f = open(args[1], "rt")
	for l in f:
		if l[-1] == '\n':
			l = l[:-1]
		print (l)
	f.close()

def uname_imp(args):
	uname = os.uname()
	print ("System {} release {} version {}".format(uname.sysname, uname.release, uname.version))
	print ("Machine type {}".format(uname.machine))

def free_imp(args):
	micropython.mem_info()

def reset_imp(args):
	machine.reset()

def ifconfig_imp(args):
	w = network.WLAN(network.STA_IF)
	ic = w.ifconfig()
	print ("WiFi: inet {} netmask {} broadcast {}".format(ic[0], ic[1], ic[2]))
	print ("	  status: {}".format("Active" if w.isconnected() else "Inactive"))
	print ("	  DNS {}".format(ic[3]))

def python_imp(args):
	if len(args) == 1:
		global alive
		alive = False
		return
	
	script_name = args[1]
	if len(script_name.split(".")) > 1:
		script_name = script_name[:-3]
	
	try:
		pys = __import__(script_name)
		if '__main__' in dir(pys):
			pys.__main__(args)
	except Exception as e:
		print ("Error executing script {}".format(script_name))
		sys.print_exception(e)
	
	# TODO: ovo moze exeptat "KeyError: /bin/pystone" ako je vec deletan; treba stavit if script_name in modules
	del sys.modules[script_name]
	
def help_imp(args):
	print ("Available commands:")
	for k in functions:
		print ("{}".format(k))
	
	print ("")
	print ("Available bins:")
	pybins, shbins = get_bins()
	for k in pybins:
		print ("{}".format(k))
	for k in shbins:
		print ("{}".format(k))
	print ("")
	
def quit_imp(args):
	global alive
	alive = False

def get_bins():
	pybins = {}
	shbins = {}
	for f, type, unknown_param, inode in os.ilistdir("/bin"):
		if f.endswith(".py"):
			fname = f[:-3]
			pybins[fname] = "/bin/"+f
		if f.endswith(".sh"):
			fname = f[:-3]
			shbins[fname] = "/bin/"+f
	return pybins, shbins

alive = True

functions = {"ls": ls_imp,
			 "mkdir": mkdir_imp,
			 "rmdir": rmdir_imp,
			 "mv": mv_imp,
			 "cd": cd_imp,
			 "pwd": pwd_imp,
			 "rm": rm_imp,
			 "cat": cat_imp,
			 "uname": uname_imp,
			 "free": free_imp,
			 "df": df_imp,
			 "ps": ps_imp,
			 "kill": kill_imp,
			 "ifconfig": ifconfig_imp,
			 "restart": reset_imp,
			 "reboot": reset_imp,
			 "reset": reset_imp,
			 "python": python_imp,
			 "help": help_imp,
			 "quit": quit_imp}

def all_commands(start):
	py, sh = get_bins()
	cmds = list(functions.keys()) + list(py.keys()) + list(sh.keys())
	if len(start) > 0:
		cmds = list(filter(lambda k: k.startswith(start), cmds))
	return sorted(cmds)

#uncomment do enable wifi
#import network
#w = network.WLAN(network.STA_IF)

def execute_script(name):
	with open(name) as f:
		for line in f.readlines():
			line = line.rstrip()
			if len(line) > 0:
				execute_command(line)

def _run_thread(args, command, _func):
	global _active_threads
	global _active_threads_ksignal
	
	tid = _thread.get_ident()
	_active_threads_ksignal[tid] = -1
	def _thread_watchdog(timer):
		if _active_threads_ksignal[tid] != -1:
			timer.deinit()
			def _quit(msg):
				print ("Quitting from {}".format(_thread.get_ident()))
				_thread.exit()
#				raise Exception(msg)
# 			micropython.schedule(_quit, ("[{}] Kill thread signal {}".format(tid, _active_threads_ksignal[tid])))
			print ("Quitting from {}".format(_thread.get_ident()))
			_thread.exit()
			_thread.exit()
	
	_active_threads[tid] = (command, time.ticks_us())
	print ("[1] {}".format(tid))
	try:
		timer = machine.Timer(-1)
		#timer.init(period=100, mode=machine.Timer.PERIODIC, callback=_thread_watchdog)
		
		_func(args)
		timer.deinit()
		del _active_threads[tid]
		print ("Exited [{}] {}".format(tid, command))
		gc.collect()
	except Exception as e:
		timer.deinit()
		del _active_threads[tid]
		print ("Exited [{}] {}".format(tid, command))
		gc.collect()
		raise e

def execute_command(command):
	if command.endswith("&"):
		#global _active_threads
		#global _next_thread_index
		
		args = command[:-1].split(" ")
		#new_thread = 
		_thread.start_new_thread(_run_thread, (args, command, _execute_command))#TODO: ovo moze exceptat MemoryError: memory allocation failed
		#td = (new_thread, command)
		#_active_threads[_next_thread_index] = td
	else:
		args = command.split(" ")
		_execute_command(args)
	
	#sys.stdin.read(1) '\t'

def _execute_command(args):
	prog_name = args[0]
	py_bins, sh_bins = get_bins()
	if prog_name in functions:
		try:
			gc.collect()
			result = functions[prog_name](args)
			if result != None:
				print (result)
		except Exception as e:
			print ("Error executing command")
			sys.print_exception(e)
	elif prog_name in py_bins:
		_args = ['python', py_bins[prog_name]]
		_args.extend(args[1:])
		python_imp(_args)
	elif prog_name in sh_bins:
		execute_script(sh_bins[prog_name])
	else:
		print ("{}: command not found".format(prog_name))

def shell(args):
	execute_command("init")
	while (alive):
	#	ip = w.ifconfig()[0]
		ip = "machine"
		prompt = "{}:{} upy$ ".format(ip, os.getcwd())
		command = input(prompt)
		try:
			execute_command(command)
		except KeyboardInterrupt:
			print ("Keyboard interrupt")
			pass
	
	del sys.modules["sh"]

#_thread.start_new_thread(_run_thread, ([], "sh", shell))

##_run_thread([], "sh", shell)
from cmd import Cmd


def complete_dir(start):
#    cmps = start.split("/")
	if start.startswith("/"):
		start = start[1:]
	cwd = os.getcwd()
	files = os.listdir(cwd)
	if len(start) > 0:
		files = list(filter(lambda k: k.startswith(start), files))
	return files


class Shell(Cmd):
	def __init__(self):
		super().__init__()
		self.update_prompt()
		execute_command("init")

	def update_prompt(self):
		ip = "machine"
		prompt = "{}:{} upy$ ".format(ip, os.getcwd())
		self.prompt = prompt

	def complete(self, line):
		seg = line.split(" ")
		if len(seg) == 1:
			cmds = all_commands(seg[0])
			if len(cmds) == 1:
				return cmds[0]+" ", True
			if len(cmds) == 0:
				return line, False
			print ('')
			for cmd in cmds:
				sys.stdout.write(cmd+'\t')
			print ('')
		if len(seg) > 1:
			files = complete_dir(seg[-1])
			if len(files) == 1:
				preline = "/".join(seg[:-1])
				return preline + " " + files[0]+" ", True
			if len(files) == 0:
				return line, False
			print ('')
			for file in files:
				sys.stdout.write(file+'\t')
			print ('')
		return line, True

	def execute_command(self, cmd):
		try:
			execute_command(cmd)
		except KeyboardInterrupt:
			print ("Keyboard interrupt")
			pass
		self.update_prompt()

s = Shell()
s.cmdloop()

#shell()

def clear():
	if "sh" in sys.modules:
		del sys.modules["sh"]


