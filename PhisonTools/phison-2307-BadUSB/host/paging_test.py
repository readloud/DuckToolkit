import sys
import struct
import PyScsi
from util import BinFile

def outhex(s):
	for b in s:
		print "%02X" % (ord(b)),
	print ""

PyScsi.open("E")
hfo = open("paging.bin", "wb")
for i in xrange(0x400):
	print "%04X:" % (i),
	PyScsi.write("\x06\x0C\x00PhI\xFA\x46"+struct.pack("B", i & 0xFF)+"\x00\x00\x00\x00\x00\x00\x00", "")
	PyScsi.write("\x06\x0C\x00PhI\xFA\x47"+struct.pack("B", i>>8)+"\x00\x00\x00\x00\x00\x00\x00", "")
	data = PyScsi.read("\x06\x05RA\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00", 0x210)
	hfo.write(data[0:0x200])
	if data[0:2]=="\xAA\x55":
		print "This is %04X" % struct.unpack("<H", data[2:4])
	else:
		outhex(data[0:32])
		PyScsi.write("\x06\x0C\x00PhI\x00\x00\xAA\x00\x00\x00\x00\x00\x00\x00", "")
		PyScsi.write("\x06\x0C\x00PhI\x00\x01\x55\x00\x00\x00\x00\x00\x00\x00", "")
		PyScsi.write("\x06\x0C\x00PhI\x00\x02"+struct.pack("B", i & 0xFF)+"\x00\x00\x00\x00\x00\x00\x00", "")
		PyScsi.write("\x06\x0C\x00PhI\x00\x03"+struct.pack("B", i>>8)+"\x00\x00\x00\x00\x00\x00\x00", "")
PyScsi.close()
hfo.close()
