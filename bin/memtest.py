import machine
import gc
import time
import sys

def __main__(args):
    f = machine.freq() / 1000 / 1000

    arrays = []

    cnt = 512 if len(args) < 3 else int(args[2])
    size = 1024 if len(args) < 4 else int(args[3])
    epochs = 10 if len(args) < 5 else int(args[4])
    srcarr = list(range(size))
    for c in range(cnt):
        arrays.append(srcarr.copy())

    idx = 0
    sys.stdout.write("\033[2J")
    while True:
        sys.stdout.write("\033[0;0H")
        print("CPU Frequency:   \t{} MHz".format(f))
        print("Allocated memory:\t{} KB".format(gc.mem_alloc()//1024))
        print("Available memory:\t{} KB".format(gc.mem_free()//1024))
        print("".join(["-"]*20))

        srcarr = list(range(idx*2, idx*2+size))
    #    print ("Test duration {}".format(time))
        print ("\nWriting sequence {} to {}".format(idx*2, idx*2+size))
        start = time.ticks_ms()
        for e in range(epochs):
            for c in range(cnt):
                arrays[c] = srcarr.copy()
            duration = (time.ticks_ms()-start)/1000
            sys.stdout.write("\033[256D")
            sys.stdout.write("{} Bytes in {} sec ".format((e+1)*cnt*size*4, duration))
            sys.stdout.write("{} MB/s".format((e+1)*cnt*size*4/1024/1024/duration))
        gc.collect()

        start = time.ticks_ms()
        print ("\n\nWriting const {0:b}".format(idx))
        for e in range(epochs):
            srcarr = [idx+e]*size
            for c in range(cnt):
                arrays[c] = srcarr.copy()
            duration = (time.ticks_ms()-start)/1000
            sys.stdout.write("\033[256D")
            sys.stdout.write("{} Bytes in {} sec ".format((e+1)*cnt*size*4, duration))
            sys.stdout.write("{} MB/s".format((e+1)*cnt*size*4/1024/1024/duration))
        gc.collect()

        idx += 1

