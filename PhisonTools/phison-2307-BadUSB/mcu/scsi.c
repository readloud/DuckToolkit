#include "string.h"
#include "PS2303.h"
#include "led.h"
#include "ticks.h"
#include "usb.h"
#include "ch9.h"

BYTE 	scsi_status;
DWORD	scsi_data_residue, scsi_transfer_size;
BYTE	scsi_tag[4];
__bit	scsi_dir_in;
BYTE	scsi_lun;
BYTE 	scsi_cdb[16];
BYTE	scsi_cdb_size;

bit ScsiHandleCDB()
{
	//BYTE __code *ptr;

	scsi_status = 1;
	switch(scsi_cdb[0])
	{
		case 0x00: //test unit ready
			scsi_status = 1;
			return 1;
		case 0x03: //request sense
			memset(EPBUF, 0, 18);
			EPBUF[0] = 0x70;
			EPBUF[2] = 0x02;
			EPBUF[7] = 10;
			EPBUF[12] = 0x3A;
			UsbTxDma(18, 0);
			scsi_status = 0;
			return 1;
		case 0x06: //vendor
		case 0xC6:
		case 0xC7:
			switch(scsi_cdb[1])
			{
				case 0x05: //read addr
					//UsbTxDmaTest(0x200, 0, scsi_cdb[4], scsi_cdb[5], scsi_cdb[6], scsi_cdb[7]);
					memcpy(EPBUF, (BYTE __xdata *)((scsi_cdb[4]<<8) | scsi_cdb[5]), 0x200);
					EPBUF[0x200] = 'I';
					EPBUF[0x201] = 'F';
					UsbTxDma(0x210, 0);
					scsi_status = 0;
					return 1;
				case 0x0C: //write addr
					*(BYTE __xdata *)((scsi_cdb[6]<<8) | scsi_cdb[7]) = scsi_cdb[8];
					scsi_status = 0;
					return 1;
			}
			return 0;
		default:
			return 0; //not handled
	}
}

BOOL HandleClassRequest()
{
	return FALSE;
}

BOOL HandleVendorRequest()
{
	return FALSE;
}
