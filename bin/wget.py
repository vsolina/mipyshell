# wget.py

__version__ = '1.0.2' # Major.Minor.Patch

import requests

def __main__(args):
	run(args[2:])	# mipyshell first 2 arguments are "python" and "photo.py"

def run(args):
	if len(args) < 1:
		print("usage:\tARGV=['https://example.com/url_to_get.htm','outfile.htm'];exec(open('bin/wget.py').read())\t# -or-\n\twget https://example.com/url_to_get.htm [output filename]\n\t(use - for output filename to show on-screen")
	else:
		url = args[0]
		if len(args) > 1:
			filename = args[1]
		else:
			filename = ""
			if url.endswith("/"):
				filename = "index"
			else:
				filename = url.split("/")[-1].split("?")[0]
		try:
			r = requests.get(url).raw
			if filename != '-':
				fp = open(filename, "wt")
				print("\t {} => {} ".format(url,filename), end='\r')
		except Exception as e:
			print(f"Error '{e}' reading URL {url}")
			r = None
		if r:
			l = 0
			while (True):
				read = r.read(4096)
				l = l + len(read)
				if filename != '-':
					fp.write(read)
					print(" {} ".format(l), end='\r')
				else:
					print(read.decode('unicode-escape') ,end='')
				if len(read) < 4096:
					break

			if filename != '-':
				fp.close()
				print("")


if 'ARGV' in locals():
	run(ARGV)
