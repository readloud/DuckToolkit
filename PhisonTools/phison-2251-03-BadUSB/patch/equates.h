__xdata __at 0x42EF BYTE bmRequestType;
__xdata __at 0x42F0 BYTE bRequest;
__xdata __at 0x42BD BYTE scsi_cdb[16];
#define DEFAULT_READ_SECTOR_HANDLER 0x2D31
#define DEFAULT_CDB_HANDLER 0x2D3F
__xdata __at 0x42E8 BYTE scsi_tag[4];
__xdata __at 0x4301 BYTE FW_EPIRQ;
__xdata __at 0xB000 BYTE EPBUF[1024];
