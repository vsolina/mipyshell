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
import time


## Internal variables
next_thread_index = 1
_active_threads = {}
_active_threads_ksignal = {}

_vfses = {}

_threads_enabled = False
try:
    import _thread
    _threads_enabled = True
except:
    pass


## Utility functions
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
#    if comp[-1] != "":
#        path += "/"
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


## Commands
def mkdir_imp(args):
    path = args[1]
    print ("creating dir {}".format(abs_path(path)))
    os.mkdir(path)

def rmdir_imp(args):
    path = args[1]
    os.rmdir(path)

def cd_imp(args):
    path = args[1]
    os.chdir(path)

def pwd_imp(args):
    print(abs_path(os.getcwd()))

def rm_imp(args):
    path = args[1]
    os.remove(path)

def free_imp(args):
    micropython.mem_info()

def reset_imp(args):
    machine.reset()

def modules_imp(args):
    print (sys.modules)

def time_imp(args):
    s = time.ticks_ms()
#    print("Executing {}".format(
    execute_command(" ".join(args[1:]))
    ms = time.ticks_ms() - s
    minutes = ms // 60000
    seconds = (ms - minutes*60000) // 1000
    print ("{}m{}.{:0>3}".format(minutes, seconds, ms % 1000))


## Special commands
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

def quit_imp(args):
    global alive
    alive = False

alive = True

## Integrated command mapping
cmds_integrated = {
             "mkdir": mkdir_imp,
             "rmdir": rmdir_imp,
             "cd": cd_imp,
             "pwd": pwd_imp,
             "rm": rm_imp,
             "free": free_imp,
             "restart": reset_imp,
             "reboot": reset_imp,
             "reset": reset_imp,
             "python": python_imp,
             "time": time_imp,
             "quit": quit_imp}

def all_commands(start):
    py, sh = get_bins()
    cmds = list(cmds_integrated.keys()) + list(py.keys()) + list(sh.keys())
    if len(start) > 0:
        cmds = list(filter(lambda k: k.startswith(start), cmds))
    return sorted(cmds)

if _threads_enabled:
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
    #                raise Exception(msg)
    #             micropython.schedule(_quit, ("[{}] Kill thread signal {}".format(tid, _active_threads_ksignal[tid])))
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
        if not _threads_enabled:
            print ("Backgrounding (threading) is not available")
            return
        #global _active_threads
        #global _next_thread_index
        
        args = command[:-1].split(" ")
        #new_thread = 
        _thread.start_new_thread(_run_thread, (args, command, _exec_cmd))#TODO: ovo moze exceptat MemoryError: memory allocation failed
        #td = (new_thread, command)
        #_active_threads[_next_thread_index] = td
    else:
#        args = command.strip().split(" ")
        args = list(filter(lambda s: len(s) > 0, command.strip().split(" ")))
        _exec_cmd(args)

def _exec_cmd(args):
    cmd_name = args[0]
    py_bins, sh_bins = get_bins()
    if cmd_name in cmds_integrated:
        try:
            gc.collect()
            result = cmds_integrated[cmd_name](args)
            if result != None:
                print (result)
        except Exception as e:
            print ("Error executing command")
            sys.print_exception(e)
    elif cmd_name in py_bins:
        _args = ['python', py_bins[cmd_name]]
        _args.extend(args[1:])
        python_imp(_args)
    elif cmd_name in sh_bins:
        execute_script(sh_bins[cmd_name])
    else:
        print ("{}: command not found".format(cmd_name))

def execute_script(name):
    with open(name) as f:
        for line in f.readlines():
            line = line.rstrip()
            if len(line) > 0:
                execute_command(line)

'''
def shell(args):
    execute_command("init")
    while (alive):
    #    ip = w.ifconfig()[0]
        ip = "machine"
        prompt = "{}:{} upy$ ".format(ip, os.getcwd())
        command = input(prompt)
        try:
            execute_command(command)
        except KeyboardInterrupt:
            print ("Keyboard interrupt")
            pass
    
    del sys.modules["sh"]
'''

#_thread.start_new_thread(_run_thread, ([], "sh", shell))

##_run_thread([], "sh", shell)
from cmd import Cmd

#TODO: support for subpaths
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


