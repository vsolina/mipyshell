
def __main__(args):
	print ("Burning cpu")
	
	stages = 1
	if len(args) > 2:
		stages = int(args[2])
	result = 0
	for s in range(stages):
		for a in range(1000):
			for b in range(1000):
				result = a * b
		print ("stage {} finished".format(s+1))
	
	print ("Finished burning")
