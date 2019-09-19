import ssd1306
import machine
from sh import scrollback

reset = machine.Pin(4)
reset.init(reset.OUT)
reset.off()
reset.on()
i2c = machine.I2C(scl=machine.Pin(14), sda=machine.Pin(2), freq=600000)
oled = ssd1306.SSD1306_I2C(128, 32, i2c)

def __main__(args):
	global scrollback
	txt = args[2]
	scrollback.append(txt)
	oled.fill(0)
	index = 0
	height = 8
	for line in scrollback[-4:]:
		oled.text(line, 0, index * height)
		index += 1
	oled.show()
