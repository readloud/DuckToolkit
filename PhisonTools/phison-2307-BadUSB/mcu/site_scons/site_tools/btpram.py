import os
import struct

import SCons.Util

def build_btpram(target, source, env):
	hfi = open(SCons.Util.to_String(source[0]), "rb")
	hfi.seek(0, os.SEEK_END)
	sz = hfi.tell()
        hfi.seek(0)
        size = ((sz-1) | 0x3FF)+1

        if size>32768:
        	hfi.close()
        	print "Invalid input file size !"
        	return 1 # fail

        hfo = open(SCons.Util.to_String(target[0]), "wb")

        hfo.write("BtPramCd\x00\x00\x00\x00\x00\x00\x00\x00")
        hfo.write(struct.pack("<L", size/0x400))
        hfo.write("\x00"*0x1EC)
        hfo.write(hfi.read())
        hfo.write("\x00"*(size-sz))
        hfo.close()
        hfi.close()
        return 0 # ok

def generate(env):
         btpram_builder = SCons.Builder.Builder(action=build_btpram,
         			suffix='.btpram',
         			src_suffix='.bin')
         env.Append(BUILDERS = {'BtPram' : btpram_builder})

def exists(env):
	return True
