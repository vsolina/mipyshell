import esp32

raw_t = esp32.raw_temperature()
t = (raw_t - 32) / 1.8

print ("{} Deg Celsius".format(t))

