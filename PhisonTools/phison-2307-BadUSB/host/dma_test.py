import sys
import struct
import PyScsi
from util import BinFile

def outhex(s):
	for b in s:
		print "%02X" % (ord(b)),
	print ""

def wr(addr, val):
	PyScsi.write("\x06\x0C\x00PhI"+struct.pack(">HB", addr & 0xFFFF, val & 0xFF)+"\x00\x00\x00\x00\x00\x00\x00", "")

def rd(addr):
	return ord(PyScsi.read("\x06\x05RA"+struct.pack(">H", addr & 0xFFFF)+"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00", 0x210)[0])

def DmaCopy(dst, src, size):
	# src
	wr(0xF900, src)
	wr(0xF901, src>>8)
	wr(0xF902, src>>16)
	# dst
	wr(0xF904, dst)
	wr(0xF905, dst>>8)
	wr(0xF906, dst>>16)
	# size
	wr(0xF908, size)
	wr(0xF909, size>>8)
	wr(0xF90A, size>>16)
	# go
	wr(0xF930, 0x02)
	# check done
	if rd(0xF930) & 7:
		print "DMA is busy !"
		return False
	return True

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

PyScsi.open("E")

for i in xrange(0, 0x40000, 0x200):
	DmaFill(i, i, 0x200, 4)

PyScsi.close()
