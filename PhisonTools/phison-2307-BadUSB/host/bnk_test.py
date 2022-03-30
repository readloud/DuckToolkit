import sys
import PyScsi as drv
import Phison as ph

def outhex(s):
	for b in s:
		print "%02X" % (ord(b)),
	print ""

disk = "E"

drv.err_mode = drv.err_mode_raise
drv.open(disk)
print "Reading..."

hfo = open("regbanks.bin", "wb")

for bnk in xrange(8):
	data = ph.fwReadBankedMemory(bnk, 0xF000, 0x1000)
	hfo.write(data)
	print bnk, ":",
	outhex(data[0:32])
drv.close()
hfo.close()
