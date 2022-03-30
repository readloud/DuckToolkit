"""read XDATA memory"""
import sys
import PyScsi as drv
import Phison as ph
from util import BinFile

if len(sys.argv)!=4:
	sys.exit("Read chip internal memory\nUsage: %s <file> <addr> <size>\nExample: %s ram.bin 0 0x10000" % (sys.argv[0], sys.argv[0]))

addr = int(sys.argv[2], 0)
size = int(sys.argv[3], 0)

disk = ph.FindDrive()
if not disk:
	sys.exit("No Phison devices found !")

drv.err_mode = drv.err_mode_raise
drv.open(disk)
print "Reading..."
BinFile.save(sys.argv[1], ph.ReadMemory(addr, size))
drv.close()
