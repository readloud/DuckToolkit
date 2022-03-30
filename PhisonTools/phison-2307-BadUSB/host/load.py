"""load code"""
import sys
import PyScsi as drv
import Phison as ph

if len(sys.argv)!=2:
	sys.exit("Load and start PRAM code file\nUsage: %s <file>" % (sys.argv[0]))

disk = ph.FindDrive()
if not disk:
	sys.exit("No Phison devices found !")

drv.err_mode = drv.err_mode_raise
drv.open(disk)
print "Loading..."
ph.LoadBurner(sys.argv[1])
drv.close()
