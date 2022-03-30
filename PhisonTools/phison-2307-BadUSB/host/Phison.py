"""Phison vendor mode commands"""

import struct
import PyScsi as drv

def GetVersionPage():
	return drv.read("\x06\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00", 528)

def GetChipType(iddata=None):
	"""Get IC type from version page"""
	if not iddata:
		iddata = drv.read("\x06\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00", 528)
	if not iddata or iddata[0x17A:0x17C]!="VR":
		return 0
	return struct.unpack(">H", iddata[0x17E:0x180])[0]

def GetVersion(iddata=None):
	"""Get code version from version page"""
	if not iddata:
		iddata = drv.read("\x06\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00", 528)
	if not iddata or iddata[0x17A:0x17C]!="VR":
		return (0, 0, 0)
	return struct.unpack("BBB", iddata[0x94:0x97])
	
def GetDate(iddata=None):
	"""Get code build date from version page"""
	if not iddata:
		iddata = drv.read("\x06\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00", 528)
	if not iddata or iddata[0x17A:0x17C]!="VR":
		return (0, 0, 0)
	return struct.unpack("BBB", iddata[0x97:0x9A])

def GetF1F2(iddata=None):
	"""Get F1/F2 parameters from version page"""
	if not iddata:
		iddata = drv.read("\x06\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00", 528)
	if not iddata or iddata[0x17A:0x17C]!="VR":
		return (0, 0)
	return struct.unpack("BB", iddata[0x9A:0x9C])

def GetRunMode(iddata=None):
	"""Get run mode from version page"""
	if not iddata:
		iddata = drv.read("\x06\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00", 528)
	if not iddata or iddata[0x17A:0x17C]!="VR":
		return "?"
	if iddata[0xA0:0xA8]==" PRAM   ":
		return "BROM"	# BootROM
	if iddata[0xA0:0xA8]==" FW BURN":
		return "BN"	# firmware burner
	if iddata[0xA0:0xA8]==" HV TEST":
		return "HV"	# hardware verify
	return "FW"		# firmware


def FindDrive(start="E", end="P"):
	"""Find first Phison-based drive. Returns drive letter or None"""
	em = drv.err_mode	
	drv.err_mode = drv.err_mode_result
	for i in range(ord(start), ord(end)):
		l = chr(i)
		if not drv.open(l):
			continue
		chip = GetChipType()
		if chip!=0:
			print "Drive %c: PS%04X in %s mode" % (l, chip, GetRunMode())
			drv.err_mode = em
			return l
	drv.err_mode = em
	return None

def ReadMemory(addr, size):
	"""Read chip's XDATA memory. Returns data[size] or None"""
	data = ""
	while size>0:
		d = drv.read("\x06\x05RA"+struct.pack(">H", addr)+"\x00\x00\x00\x00\x00\x00", 528)
		if not d:
			return None
		if size<=512:
			return data+d[0:size]			
		data += d[0:512]
		addr += 512
		size -= 512
	return data

def WriteMemory(addr, data):
	"""Write XDATA memory"""
	for i in xrange(len(data)):
		drv.write("\x06\x0C\x00PhI"+struct.pack(">H", addr+i)+data[i]+"\x00\x00\x00\x00\x00\x00\x00", "")

def fwReadMemory(addr, size):
	"""Read chip's memory in FW mode. Returns data[size] or None"""
	data = ""
	while size>0:
		d = drv.read("\x06\x8D\x00\x00\x01\x00"+struct.pack(">H", addr)+"\x00\x00\x00\x00\x00\x00\x00\x00", 0x200)
		if not d:
			return None
		if size<=512:
			return data+d[0:size]			
		data += d
		addr += 512
		size -= 512
	return data

def fwReadBankedMemory(bank, addr, size):
	"""Read chip's banked registers (controlled by F000) in FW mode. Returns data[size] or None"""
	data = ""
	while size>0:
		d = drv.read("\x06\x8D\x55"+struct.pack("B", bank)+"\x01\x00"+struct.pack(">H", addr)+"\x00\x00\x00\x00\x00\x00\x00\x00", 0x200)
		if not d:
			return None
		if size<=512:
			return data+d[0:size]			
		data += d
		addr += 512
		size -= 512
	return data

def fwReadDmaPages(pg, size):
	"""Read chip's memory in FW mode via DMA. Returns data[size] or None"""
	return drv.read("\x06\xA1"+struct.pack("B", pg)+"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00", size)

def GoRam():
	"""Run a BN/FW"""
	return drv.write("\x06\xB3\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00", "")

def GoRom():
	"""Enter BootROM from FW"""
	return drv.write("\x06\xBF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00", "")

def LoadBurner(fname):
	"""Load and start burner. Returns boolean"""
	f = open(fname, "rb")

	hdr = f.read(0x200)
	if hdr[0:8]!="BtPramCd":
		f.close()
		print "Not a Phison Image file !"
		return False

	size = struct.unpack("<L", hdr[0x10:0x14])[0]
	if size>255: # burners have xx 00 00 00 sizes, FWs have banking info in upper bytes
		f.close()
		print "Not a burner file !"
		return False
	size *= 0x400 # burner size is in 1k pages
	# send header
	if not drv.write("\x06\xB1\x03\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00", hdr):
		f.close()
		return False
	# get header response
	rsp = drv.read("\x06\xB0\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00", 8)
	if not rsp:
		f.close()
		return False
	if rsp[0]!="\x55":
		print "Header not accepted !"
		f.close()
		return False		
	# send body
	addr = 0
	while size>0:
		if size>0x8000:
			chunk_size = 0x8000
		else:
			chunk_size = size
		if not drv.write("\x06\xB1\x02"+struct.pack(">HHH", addr>>9, 0, chunk_size>>9)+"\x00\x00\x00\x00\x00\x00\x00", f.read(chunk_size)):
			f.close()
			return False
		rsp = drv.read("\x06\xB0\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00", 8)
		if not rsp:
			f.close()
			return False
		if rsp[0]!="\xA5":
			print "Body not accepted !"
			f.close()
			return False		
		addr += chunk_size
		size -= chunk_size
	f.close()
	# run
	if not drv.write("\x06\xB3\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00", ""):
		print "Failed to run !"
		return False
	return True

def bnReadNand(mode, cs, start_page, num_pages):
	"""read FW area in BN mode"""
	return drv.read("\x06\x03"+struct.pack("BB", num_pages, cs)+"\x00\x00\x00"+struct.pack("<HH", start_page, mode)+"\x00\x00\x00\x00\x00", num_pages*0x400+0x40)
