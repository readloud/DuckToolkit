"""switch to BootROM mode"""
import sys
import PyScsi as drv
import Phison as ph

disk = ph.FindDrive()
if not disk:
	sys.exit("No Phison devices found !")

drv.err_mode = drv.err_mode_raise
drv.open(disk)
drv.write("\x06\xBF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00", "")
drv.close()
