# set.py

__version__ = '1.0.0' # Major.Minor.Patch

from sh import human
import os
import machine
import time

def __main__(args): # ['python', '/bin/set.py', '33', '0']
	num = 1		# times to loop
	pin = 2
	freq=1000	# hz
	duty=32768	# 0 to 65535
	ton=1.0
	toff=1.0
	voff=0		# what "off" means (inverted for some LEDs)

	# print(args)

	if len(args) < 3:
		print("Usage:")
		print("set pin{} value{}".format(pin, num))
		print("set pin{} loop{} freq{} duty{} ondelay{} offdelay{} voff{}".format(pin, num, freq, duty, ton, toff, voff))
	else:
		if len(args) > 2:
			pin = int(args[2])
		if len(args) > 3:
			num = int(args[3])

		# Case 1 - simple pin set
		if len(args) <5:
			print("set pin{} value{}".format(pin, num))
			led = machine.Pin(pin, machine.Pin.OUT)
			led.value(num)

		else:

			# Case 2 - PWM demo
			if len(args) > 4:
				freq = int(args[4])
			if len(args) > 5:
				duty = int(args[5])
			if len(args) > 6:
				ton = float(args[6])
			if len(args) > 7:
				toff = float(args[7])
			if len(args) > 8:
				voff = float(args[8])


			print("set pin{} loop{} freq{} duty{} ondelay{} offdelay{} voff{}".format(pin, num, freq, duty, ton, toff, voff))

			pwm = machine.PWM(pin, freq=freq, duty_u16=duty)	# create a PWM object on a pin and set freq and duty
			# pwm.duty_u16(32768)			# set duty to 50%
			# pwm.init(freq=5000, duty_ns=5000)	# reinitialise with a period of 200us, duty of 5us
			# pwm.duty_ns(3000)			# set pulse width to 3us

			if num>0:
				while num>0:
					pwm.duty_u16(duty)
					time.sleep(ton)
					pwm.duty_u16(65545*voff)
					time.sleep(toff)
					num=num-1

				pwm.deinit()
			else:
				pass	# leave pwm on


