from machine import SDCard
import uos
uos.mount(SDCard(slot=2, mosi=15, miso=2, sck=14, cs=13), "/sd")

