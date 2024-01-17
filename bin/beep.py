# beep.py

__version__ = '1.0.0' # Major.Minor.Patch

from sh import human
import os
from machine import Pin, PWM
from utime import sleep


def __main__(args):
	num = 10
	pin=26
	freq=1000
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
	if len(args) > 6:
		freq = float(args[6])
	
	if not num:
		num = 10

	print("beep pin{} ondelay{} offdelay{} loop{} freq{}".format(pin, ton, toff, num, freq))

	SPEAKER_PIN = pin
	speaker = PWM(Pin(SPEAKER_PIN))

	while num>0:
		# create a Pulse Width Modulation Object on this pin
		# set the duty cycle to be 50%
		speaker.duty_u16(freq)
		speaker.freq(freq) # 50% on and off
		sleep(ton)
		speaker.duty_u16(0)
		# turn off the PWM circuits off with a zero duty cycle
		speaker.duty_u16(0)
		sleep(toff)
		num=num-1



