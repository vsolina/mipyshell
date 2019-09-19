'''
Created by Valentin Solina, Part of mipyshell project
Dinamically allocating RAM backed FAT file system for MicroPython
'''

import uos
from sh import _vfses

class RAMDynBlockDev:
	def __init__(self, block_size, num_blocks):
		self.block_size = block_size
		self.data = [None for a in range(num_blocks)]
	#        self.data = bytearray(block_size * num_blocks)

	def readblocks(self, block_num, buf):
#		print ("Reading block {} {}B".format(block_num, len(buf)))
		for bn in range(len(buf) // self.block_size):
			if self.data[block_num + bn] is not None:
				block = self.data[block_num + bn]
				for i in range(self.block_size):
					buf[bn + i] = block[i]
			else:
				for i in range(self.block_size):
					buf[bn + i] = 0
	
	def writeblocks(self, block_num, buf):
#		print ("Writing block {} {}B".format(block_num, len(buf)))
		for bn in range(len(buf) // self.block_size):
			if self.data[block_num + bn] is None:
#				print ("RAMfs alloc {}".format(self.block_size))
				self.data[block_num + bn] = bytearray(self.block_size)
			block = self.data[block_num + bn]
			for i in range(self.block_size):
				block[i] = buf[bn + i]

	def ioctl(self, op, arg):
#		print ("RAMBD ioctl {} arg {}".format(op, arg))
		if op == 3: # sync
			self.cleanup()
		if op == 4: # get number of blocks
			return len(self.data)# // self.block_size
		if op == 5: # get block size
			return self.block_size
	
	def cleanup(self):
		idx = 0
		for block in self.data:
			if block is not None:
				skip = False
				for i in range(self.block_size):
					if block[i] != 0:
						skip = True
						continue
				if not skip:
					print ("RAMfs dealloc {}".format(idx))
					self.data[idx] = None
			idx += 1
	
	def __del__(self):
		print ("Called RAMdisk deallocator")


def __main__(args):
	if len(args) < 3:
		print ("Usage:")
		print ("ramdisk <path> count block_size")
		print ("eg. ramdisk /ram0 50 512")
		print ("    mounts 25KB ramdisk to /ram0")
		return
	
	pth = args[2]
	bsize = 512
	cnt = 50
	if len(args) > 3:
		cnt = int(args[3])
	if len(args) > 4:
		bsize = int(args[4])
	if bsize * cnt < 512*50:
		print ("Min disk size is {}KB".format(512*50/1024))
		print ("Entered {}KB".format(bsize*cnt/1024))
		return
	
	print ("Creating filesystem of {}KB in {}".format(bsize*cnt/1024, pth))
	bdev = RAMDynBlockDev(bsize, cnt)
	uos.VfsFat.mkfs(bdev)
	vfs = uos.VfsFat(bdev)
	uos.mount(vfs, pth)
	_vfses[pth] = (vfs, bdev)

