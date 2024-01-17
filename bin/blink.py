# blink.py

__version__ = '1.0.0' # Major.Minor.Patch

from sh import human
import os
import machine
import time


def __main__(args):
	num = 10
	pin=2
	if len(args) > 2:
		pin = int(args[2])
	if len(args) > 3:
		num = int(args[3])
	ton = 1.0
	if len(args) > 4:
		ton = float(args[4])
	toff = 1.0
	if len(args) > 5:
		toff = float(args[5])
	
	if not num:
		num = 10

	print("blink pin{} loop{} ondelay{} offdelay{}".format(pin, num, ton, toff))
	led = machine.Pin(pin, machine.Pin.OUT)

	while num>0:
	    led.value(1)
	    time.sleep(ton)
	    led.value(0)
	    time.sleep(toff)
	    num=num-1


