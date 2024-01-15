#adc.py

__version__ = '1.0.0' # Major.Minor.Patch

#from sh import human
#import os
from machine import Pin, ADC
from time import sleep

'''
ADC.ATTN_0DB : 1.2V
ADC.ATTN_2_5DB : 1.5V
ADC.ATTN_6DB : 2.0V
ADC.ATTN_11DB : 3.3V
'''

def __main__(args):
	adcpin = 32	# 27, 32, 33 are good candidates
	adcdelay=1.0
	adcloop=10
	adcdb=ADC.ATTN_11DB
	advvmsg='3.3'
	termwid=0
	adcmax=None
	adcmin=None
	omaxlen=0;
	if len(args) > 2:
		adcpin = int(args[2])
	if len(args) > 3:
		adcdelay = float(args[3])
	if len(args) > 4:
		adcloop = int(args[4])
	if len(args) > 5:
		advvmsg=args[5]
		if args[5] == '1.2':
			adcdb=ADC.ATTN_0DB
		elif args[5] == '1.5':
			adcdb=ADC.ATTN_2_5DB
		elif args[5] == '2.0':
			adcdb=ADC.ATTN_6DB
		#elif args[5] == '3.3':
		else:
			advvmsg='3.3'
			adcdb=ADC.ATTN_11DB
	if len(args) > 6:
		termwid = int(args[6])

	#print("adc pin"+adcpin+" delay"+adcdelay+" loop"+adcloop)
	print("adc pin{} delay{} loop{} gain{} termwid{}".format(adcpin, adcdelay, adcloop, advvmsg, termwid))

	pot = ADC(Pin(adcpin))
	pot.atten(adcdb)

	while adcloop>0:
		pot_value = pot.read()
		if adcmax is None or pot_value>adcmax:
			adcmax=pot_value+1
		if adcmin is None or pot_value<adcmin:
			adcmin=pot_value
		
		#out=str(pot_value) + " " str(adcmin) 
		out=str(adcmin) 
		omax=str(adcmax-1) + " " + str(pot_value)
		if len(omax)>omaxlen:
			omaxlen=len(omax)	# don't mess up chart when, e.g., pot_value drops from 1000 to 0
		while len(omax)<omaxlen:
			omax=omax+" "
		chartwid=termwid-len(out)-len(omax)
		if chartwid<=0 :
			print(pot_value)
		else:
			splat=(float(pot_value-adcmin) / float(adcmax-adcmin)) * float(chartwid)-1.0
			while splat>0.0:
				out = out + " "
				splat = splat - 1.0
				chartwid=chartwid-1
			out = out + "*"
			while chartwid>0:
				out = out + " "
				chartwid=chartwid-1
			out = out + omax
			print(out)
			

		sleep(adcdelay)
		adcloop=adcloop-1


