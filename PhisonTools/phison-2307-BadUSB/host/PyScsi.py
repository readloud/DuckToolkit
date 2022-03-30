"""SCSI direct command interface. Uses PyScsi.dll"""

from ctypes import *

class error(Exception):
	def __init__(self, value):
        	self.value = value
    	def __str__(self):
     		return repr(self.value)

err_mode_result = False	# return result code (0-ok, other-error code)
err_mode_raise = True	# raise exception on failure
err_mode = err_mode_result

def PyScsiSuccess(val):
	if val==0:
		return True
	if err_mode==err_mode_result:
		return False
	else:
		raise error(val)			

# import DLL
PyScsiDll = CDLL("PyScsi.dll")

# low level functions
open = PyScsiDll.ScsiOpen
open.argtypes = [c_char]
open.restype = PyScsiSuccess

close = PyScsiDll.ScsiClose
close.argtypes = []
close.restype = None

ScsiOut = PyScsiDll.ScsiOut
# *cdb, cdb_size, *data, data_size
ScsiOut.argtypes = [c_char_p, c_uint, c_char_p, c_uint]
ScsiOut.restype = PyScsiSuccess

def write(cdb, data):
	"""Send OUT cdb and data. Returns 0-ok"""
	return ScsiOut(cdb, len(cdb), data, len(data))	

ScsiIn = PyScsiDll.ScsiIn
# *cdb, cdb_size, *data, data_size
ScsiIn.argtypes = [c_char_p, c_uint, c_char_p, c_uint]
ScsiIn.restype = PyScsiSuccess

def read(cdb, size):
	"""Send IN cdb and receive data[size]. Returns data or None"""
	buf = create_string_buffer(size)
	if ScsiIn(cdb, len(cdb), buf, size):
		return buf.raw
	else:
		return None

set_timeout = PyScsiDll.ScsiSetTimeout
set_timeout.argtypes = [c_uint]
set_timeout.restype = None

get_timeout = PyScsiDll.ScsiGetTimeout
get_timeout.argtypes = None
get_timeout.restype = c_uint

__all__ = ["open", "close", "write", "read", "set_timeout", "get_timeout", "err_mode", "err_mode_result", "err_mode_raise"]
