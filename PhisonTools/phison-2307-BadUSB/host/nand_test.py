import sys
import struct
import PyScsi
import Phison
from util import BinFile

def outhex(s):
	for b in s:
		print "%02X" % (ord(b)),
	print ""

def wr(addr, val):
	PyScsi.write("\x06\x0C\x00PhI"+struct.pack(">HB", addr & 0xFFFF, val & 0xFF)+"\x00\x00\x00\x00\x00\x00\x00", "")

def rd(addr):
	return ord(PyScsi.read("\x06\x05RA"+struct.pack(">H", addr & 0xFFFF)+"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00", 0x210)[0])

def DmaFill(dst, val, size, width=1):
	# dst
	wr(0xF900, dst)
	wr(0xF901, dst>>8)
	wr(0xF902, dst>>16)
	wr(0xF903, 0)
	# size
	wr(0xF908, size)
	wr(0xF909, size>>8)
	wr(0xF90A, size>>16)
	wr(0xF90B, 0)
	# value
	wr(0xF90C, val)
	wr(0xF90D, val>>8)
	wr(0xF90E, val>>16)
	wr(0xF90F, val>>24)
	# go
	if width==2:
		cmd = 0x44
	elif width==4:
		cmd = 0x84
	else:
		cmd = 0x04
	wr(0xF930, cmd)
	# check done
	if rd(0xF930) & 7:
		print "DMA is busy !"
		return False
	return True

def NandSelect(cs):
	wr(0xF618, 0xFF)
	wr(0xF608, 0xFF ^ (1<<cs)) # CSx=0

def NandDesel():
	wr(0xF618, 0)
	
def NandReset():
	wr(0xF400, 0xFF) 
	while (rd(0xF41E) & 1)==0:
		pass

def NandReadId(addr, size):
	wr(0xF400, 0x90)
	wr(0xF404, addr) 
	data = ""
	for i in xrange(size):
		data+=chr(rd(0xF408))
	return data

##################################################################

PyScsi.open("E")

DmaFill(0x8000, 0, 0x1000)

wr(0xF480, 0) # set raw mode
NandSelect(0)
NandReset()

id = NandReadId(0, 6)
outhex(id)

NandReset()
NandDesel()


NandSelect(0)

wr(0xF638, 0x5A) # turn off descrambler
#wr(0xF46C, 0x40) # r dma page
#wr(0xF470, 0x40) # w dma page

wr(0xF474, 0)
wr(0xF475, 0x80)
wr(0xF476, 0)
wr(0xF477, 0)

wr(0xF478, 0)
wr(0xF479, 0x80)
wr(0xF47A, 0)
wr(0xF47B, 0)

"""
wr(0xF49C, 0x40)
wr(0xF49D, 0)

wr(0xF43C, 0x00)
wr(0xF43D, 0x01)
"""

wr(0xF400, 0x90)
wr(0xF404, 0x00)

#wr(0xF480, 0x41) # set bus mode

wr(0xF440, 0)
wr(0xF441, 0x1)
wr(0xF442, 0)
wr(0xF443, 0)

wr(0xF460, 1) # go
print "F460: %02X" % (rd(0xF460))
data = Phison.ReadMemory(0, 0x400)
NandDesel()

outhex(data)
BinFile.save("nanddump.bin", data)

PyScsi.close()
