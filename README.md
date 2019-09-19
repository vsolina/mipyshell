MicroPython Shell
=================

MicroControllers are great  
ESP32 controllers are even better  
MicroPython on ESP32 is empowering  
Adding shell on top basically transforms your ESP32 into a computer on the network  


This is a simple shell implementation that enables you to use your ESP almost as a normal *nix computer  
If you have an ESP32 version with external PSRAM and SD card support, you can do some serious sh...stuff  
Should work with other MicroPython-supported controllers like pyboard, but did not test so far  

![MicroPython Shell Demo](media/demo.gif)

Installation
------------

1. Flash a recent version of MicroPython to your Controller (http://micropython.org/download)
2. Copy lib/sh.py and lib/cmd.py to the root of Controller's file system.
3. Create /bin directory on the file system

Everything else is optional, but if you copy entire contents of /bin and /lib
directories you'll get a complete experience.

    $ cd mipyshell  
    $ ampy --port /dev/ttyUSB0 put bin /bin  
    $ ampy --port /dev/ttyUSB0 put lib /lib  


Running
-------

Just >>> import sh

Write help to list available commands, very basic ones are integrated into sh.py, others provided as separate scripts  
Everything you add to /bin will be available as a command  
You can pass arguments to invoked commands, but there is a non-standard way of declaring __main__ functionality within a python script because of some MicroPython limitations. To be explained further  

Standard commands integrated in sh.py:  
- ls, pwd, cd, cp, mv, mkdir, rmdir - Filesystem commands
- cat - Print or write contents of a file
- reboot, restart, reset - Hard reset
- ps - List running threads
- ifconfig - Network connection details
- free - Memory information
- df - List mounted file systems
- help - Print available commands
- uname - Details about MCU and MicroPython
- kill - Does not work, should stop a background thread listed in ps

Keep in mind: those commands are quite basic and don't support almost any switches for now  
    don't expect 'ls -alh' to work


Lots of useful scripts are provided with the project, eg.:
- wifi - WiFi management
- telnet - A telnet client
- edit - On board file editor, wrapper around Micropython-Editor
- httpd - Wrapper around microWebSrv that starts a web server in background, serving contents of /www directory
- telnetd - Wrapper around utelnetserver that starts a telnet server Wi-Fi interface
- wget - Spartanic version of wget that only supports downloading file from a url to current directory
- umount - Unmount a mounted file system; Don't try to unmount root because you'll succeed
- burn - Load your CPU to test stability
- memtest - Flawed memory testing utility that kind of shows memory bandwidth
- upip - Wrapper around upip module, use to install aditional libraries
- pystone - Python benchmark
- uptime - Print time in seconds since boot
- wait - Waits for a specified number of seconds
- temperature - Reads ESP32's integrated temperature sensor and outputs Degreees
- freq - Modify and read CPU frequency on ESP32/8266
- print - Draw text on ssd1306 OLED display
- ramdisk - Create a temporary file system stored in RAM that dinamically allocates memory on demand
- scani2c - Scans for i2c devices attached on ports sda = 4 and scl = 5
- clear - Clears the screen


Some features
-------------

Add & at the end of command to run it in a background thread (processes are not supported on MicroPython)  
Press Tab to complete current command  
Commands added to /bin can be a .py or .sh files. SH files are not real shell scripts, just sequences of commands that shell should invoke  


Few advices
-----------

Use picocom to connect to your board via serial connection  
Use ampy to copy entire directory to your MCU  
Add 'import sh' to boot.py if you want to run shell with every boot  
If you want to establish a Wi-Fi connection on every boot, just add 'wifi connect SSID PSK' to /bin/init.sh; provided 'import sh' is in boot.py; There is a problem however if that Wi-Fi network is not available: shell will not start and you will get stuck in 'Waiting for network'  
Ctrl+D to exit shell, Ctrl+D again to perform soft reboot  
Ctrl+C stops a long running or inresponsive command  
If you want to copy files with ampy, exit shell and disconnect from serial terminal first, otherwise raw REPL can't be activated properly  
Add init.sh or init.py to /bin if you want to run commands after shell initializes  


Limitations
-----------

No environment variables for now  
No users or permissions  
Killing threads does not work, once you start a thread it needs to finish on its own  
I/O redirection is not supported and might not be possible to implement in MicroPython  
Pipes are not supported and might not be possible to implement in MicroPython  
Current version does not work on ESP8266 because of memory constraints, but it used to. Will fix that really soon by moving some integrated commands to separate scripts.  
cmd.py is not a standard Python's cmd module nor micropython-cmd because latter does not support line completion and other necessary features; it's rather a custom version that implements handling of common special keys like arrows, tab, home and end, pgup and pgdown  


New era of MCUs
---------------

Don't compile, Interpret instead  
Don't flash, Configure instead  
Don't use serial, Telnet instead  

