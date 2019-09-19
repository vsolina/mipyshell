iimport machine

def __main__(args):
    if len(args) < 3:
        print ("Current CPU Frequency: {} MHz".format(machine.freq()/1000/1000))
    elif len(args) == 3:
        print ("Setting CPU Frequency to: {} MHz".format(int(args[2])))
        machine.freq(int(args[2])*1000*1000)

