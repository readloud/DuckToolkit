#include "PS2303.h"
#include "config.h"
#include "led.h"
#include "string.h"

__xdata __at EPBUF_VA volatile BYTE EPBUF[1024];

#define EPRX	EP2
#define EPTX	EP1

static BYTE	rx_avail = 0, usb_irq = 0;
static BYTE	UsbIntStsF080, UsbIntStsF082, UsbIntStsF086, UsbIntStsF087;
static BYTE	err_count = 0;
// setup packet
// intensionally left sparse (not struct) to allow bit addressing optimizations
BYTE	bmRequestType;
BYTE	bRequest;
WORD	wValue;
WORD	wIndex;
WORD	wLength;

BOOL usb_addressed;
BYTE usb_config, usb_speed;

static bit 	have_status = 0;

//scsi handler module interface
extern BYTE 	scsi_status;
extern DWORD	scsi_data_residue, scsi_transfer_size;
extern BYTE	scsi_tag[4];
extern bit	scsi_dir_in;
extern BYTE 	scsi_cdb[16];
extern BYTE	scsi_lun;
extern BYTE	scsi_cdb_size;
extern bit ScsiHandleCDB(void); //1-handled

extern BOOL HandleStandardRequest(void);
extern BOOL HandleClassRequest(void);
extern BOOL HandleVendorRequest(void);

static void ArmDma(BYTE p7, BYTE p5, BYTE p3, BYTE px)
{
	XREG(0xF80B) = p7;
	XREG(0xF80C) = p5-1;
	switch(px)
	{
		case 0:
			XREG(0xF80D) = p3;
			XREG(0xF80E) = p3;
			return;
		case 1:
			XREG(0xF80D) = p3;
			return;
		case 2:
			XREG(0xF80E) = p3;
			return;
		default:
			while(1);
	}
}

void UsbTxDma(WORD size, BYTE ofs)
{
	if (size==0)
	{
		return;
	}
	ArmDma(0, 0x20, 0, 0);
	ArmDma(0, 0x20, 0x80, 1);
	EPTX.ptr_l = EPBUF_PA>>8;
	EPTX.ptr_m = EPBUF_PA>>16;
	EPTX.ptr_h = EPBUF_PA>>24;
	EPTX.ofs = ofs; //dma src addr = ptr<<8+rA*0x200

	EPTX.len_l = LSB(size);
	EPTX.len_m = MSB(size);
	EPTX.len_h = 0;
	EPTX.cs = 0x88;		

	while(EPTX.cs & 0x80);	
}

void UsbTxDmaTest(WORD size, BYTE page, BYTE r5, BYTE r6, BYTE r7, BYTE r8)
{
	if (size==0)
	{
		return;
	}
//	ArmDma(0, 0x20, 0, 0);
//	ArmDma(0, 0x20, 0x80, 1);
	EPTX.ptr_l = r5;
	EPTX.ptr_m = r6;
	EPTX.ptr_h = r7;
	EPTX.r8 = 0x10;
	EPTX.ofs = page; //dma src addr = xx+rA*0x200

	EPTX.len_l = LSB(size);
	EPTX.len_m = MSB(size);
	EPTX.len_h = 0;
	EPTX.cs = 0x88;		

	while(EPTX.cs & 0x80);	
}

static void HandleCBW()
{
	BYTE a,b,c,d;

	if (rx_avail)
	{
		if ((EPRX.r17 & 0x80)==0) //some invalid state
		{
			LEDBlink();
			while(1);
		}
		scsi_data_residue = 0;
		if (EPRX.fifo_count==31) //CBW size
		{
			while(EPTX.cs & 0x40);
			while(EPRX.cs & 0x40);
			while(EP3.cs & 0x40);
			while(EP4.cs & 0x40);
			a = EPRX.fifo;
			b = EPRX.fifo;
			c = EPRX.fifo;
			d = EPRX.fifo;
			if ((a=='U') && (b=='S') && (c=='B') && (d=='C')) //CBW magic
			{
				scsi_tag[0] = EPRX.fifo;
				scsi_tag[1] = EPRX.fifo;
				scsi_tag[2] = EPRX.fifo;
				scsi_tag[3] = EPRX.fifo;
				scsi_transfer_size = EPRX.fifo;
				scsi_transfer_size |= ((DWORD)EPRX.fifo)<<8;
				scsi_transfer_size |= ((DWORD)EPRX.fifo)<<16;
				scsi_transfer_size |= ((DWORD)EPRX.fifo)<<24;
				scsi_dir_in = EPRX.fifo & 0x80;
				scsi_lun = EPRX.fifo;
				scsi_cdb_size = EPRX.fifo;
				for(a=0; a<16; a++)
				{
					scsi_cdb[a] = EPRX.fifo;
				}
				EPRX.cs = 0x40;
				if (!ScsiHandleCDB()) //not handled
				{
					scsi_status = 1;
					if (scsi_transfer_size==0)
					{
						EPTX.cs = bmSTALL; 
					}
					else if (scsi_dir_in)
                                	{
                                		EPTX.cs = bmSTALL;
                                	}
                                	else
                                	{
                                		EPRX.cs = bmSTALL;
                                	}
				}
				have_status = 1;
			}
			else
			{
				EPRX.cs = 0x40; //ACK ?	
				EPRX.cs = 4;	// ?
			}
		}
		else
		{
			EPRX.cs = 0x40; //ACK ?	
			EPRX.cs = 4;	// ?
		}		
	}
	//rearm EPRX
	rx_avail = 0;
	EPIE = bmEP2IRQ;
}

static void SendCSWDma()
{
	//magic
	EPBUF[0] = 'U';
	EPBUF[1] = 'S';
	EPBUF[2] = 'B';
	EPBUF[3] = 'S';
	//tag
	EPBUF[4] = scsi_tag[0];
	EPBUF[5] = scsi_tag[1];
	EPBUF[6] = scsi_tag[2];
	EPBUF[7] = scsi_tag[3];
	//data residue
	EPBUF[8] = scsi_data_residue;
	EPBUF[9] = scsi_data_residue>>8;
	EPBUF[10] = scsi_data_residue>>16;
	EPBUF[11] = scsi_data_residue>>24;
	//status
	EPBUF[12] = scsi_status;

	UsbTxDma(13, 0);
	have_status = 0;
	scsi_data_residue = 0;
}

static void SendCSW()
{
	while(EPTX.cs & bmSTALL);

	while((EPTX.r17 & 0x80)==0)
	{
		if ((XREG(0xF010) & 0x20)==0)
		{
			have_status = 0;
			return;
		}
	}

      	while(EPTX.cs & 0x40);
      	while(EPRX.cs & 0x40);
      	while(EP3.cs & 0x40);
      	while(EP4.cs & 0x40);

	//magic
	EPTX.fifo = 'U';
	EPTX.fifo = 'S';
	EPTX.fifo = 'B';
	EPTX.fifo = 'S';
	//tag
	EPTX.fifo = scsi_tag[0];
	EPTX.fifo = scsi_tag[1];
	EPTX.fifo = scsi_tag[2];
	EPTX.fifo = scsi_tag[3];
	//data residue
	EPTX.fifo = scsi_data_residue;
	EPTX.fifo = scsi_data_residue>>8;
	EPTX.fifo = scsi_data_residue>>16;
	EPTX.fifo = scsi_data_residue>>24;
	//status
	EPTX.fifo = scsi_status;

	EPTX.len_l = 13;
	EPTX.len_m = 0;
	EPTX.len_h = 0;
	EPTX.cs = 0x40;		
	have_status = 0;
	scsi_data_residue = 0;
}

static void InitVars()
{
	usb_speed = 0;
	usb_addressed = 0;
	//ERAM_64B5 = 0;
	//RAM_B = 0;
	//RAM_19 = 0;
	//RAM_1E = 0;
	//RAM_25.3 = 0;
	//RAM_25.0 = 0;
	//RAM_25.2 = 0;
	usb_config = 0;
	//RAM_F = 1;
}

static void InitEpDma()
{
	//F207:F206:F205 = usb_cnt<<1
	EPTX.ptr_l = EPBUF_PA>>8;
	EPTX.ptr_m = EPBUF_PA>>16;
	EPTX.ptr_h = EPBUF_PA>>24;
	EPTX.r8 = 0x10;
	EPTX.ofs = 0;
	//F247:F246:F245 = usb_cnt<<1
	EPRX.ptr_l = EPBUF_PA>>8;
	EPRX.ptr_m = EPBUF_PA>>16;
	EPRX.ptr_h = EPBUF_PA>>24;
	EPRX.r8 = 0x10;
	EPRX.ofs = 0;
}

void InitUsb(void)
{
	BYTE b;

	InitVars();
	InitEpDma();

	if (XREG(0xFA38) & 2) //USB warm start
	{
		//RAM_25.2 = 1
		usb_config = 0x11;
		if ((USBSTAT & bmSpeed)==bmSuperSpeed)
		{
			usb_speed = 3;
		}
		else if ((USBSTAT & bmSpeed)==bmHighSpeed)
		{
			usb_speed = 2;
		}
		else if ((USBSTAT & bmSpeed)==bmFullSpeed)
		{
			usb_speed = 1;
		}
		else
		{
			usb_speed = 0;
		}
		EX1 = 1;
		EX0 = 1;
		EPIE = bmEP2IRQ;
		scsi_data_residue = 0;
		scsi_status = 0;
		//RAM_23.3 = 1
		SendCSWDma();
	}
	else	//USB cold start
	{
		REGBANK = 6;
		XREG(0xF240) = 2;
		XREG(0xF28C) = 0x36;
		XREG(0xF28D) = 0xD0;
		XREG(0xF28E) = 0x98;
		REGBANK = 0;
		USBCTL = bmAttach | bmSuperSpeed;

		XREG(0xFA38) |= 2;

		EX1 = 1;
		EX0 = 1;
		for(b=0; b<250; b++);			
	}
}

void usb_isr(void) __interrupt USB_VECT
{
	usb_irq = USBIRQ;

	if (usb_irq & 0x20)
	{
		USBIRQ = 0x20;
	}

	if (usb_irq & 0x10)
	{
		USBIRQ = 0x10;
	}

	if (usb_irq & bmSpeedChange) //speed change ?
	{
		USBIRQ = bmSpeedChange;
		usb_speed = 0;
		if ((USBSTAT & bmSpeed)==bmSuperSpeed)
		{
			usb_speed = 3;
		}
		else if ((USBSTAT & bmSpeed)==bmHighSpeed)
		{
			usb_speed = 2;
		}
		else if ((USBSTAT & bmSpeed)==bmFullSpeed)
		{
			usb_speed = 1;
		}
		else
		{
			usb_speed = 0;
		}
	}

	if (usb_irq & 0x40)
	{
		USBIRQ = 0x40;
	}

	UsbIntStsF087 = XREG(0xF087);
	UsbIntStsF086 = XREG(0xF086);
	UsbIntStsF082 = XREG(0xF082);
	UsbIntStsF080 = XREG(0xF080);

	if (UsbIntStsF082 & 0x80)
	{
		XREG(0xF082) = 0x80;
	}

	if (UsbIntStsF082 & 0x40)
	{
		XREG(0xF082) = 0x40;
	}

	if (UsbIntStsF080 & 1) //EP0
	{
		XREG(0xF080) = 1;
		if (EP0CS & bmSUDAV)
		{	//copy setup packet
			bmRequestType 	= SETUPDAT[0];
			bRequest 	= SETUPDAT[1];
			wValue 		= SETUPDAT[2] | (SETUPDAT[3]<<8);
			wIndex 		= SETUPDAT[4] | (SETUPDAT[5]<<8);
			wLength 	= SETUPDAT[6] | (SETUPDAT[7]<<8);
		}
	}

	if (XREG(0xF082) & 0x20)
	{
		XREG(0xF082) = 0x20;
	}

	if (XREG(0xF081) & 0x10)
	{
		XREG(0xF081) = 0x10;
	}

	if (XREG(0xF081) & 0x20)
	{
		XREG(0xF081) = 0x20;
	}

	if (UsbIntStsF080 | UsbIntStsF082 | UsbIntStsF086 | UsbIntStsF087 | usb_irq)
	{
		EX0 = 0;
	}
}

void ep_isr(void) __interrupt EP_VECT
{
	if ((rx_avail = (EPIRQ & bmEP2IRQ))!=0)
	{
//		XREG(0xF068) = 0xC0; //in FW only, not in BN
		EPIE &= ~bmEP2IRQ; //disable this 
		EPIRQ = bmEP2IRQ; //clear irq
	}
}

static void ResetEPs()
{
	EPIE = bmEP2IRQ;
	EP1.cs = 0;
	EP2.cs = 0;
	EP3.cs = 0;
	EP4.cs = 0;
}

void EP0ACK()
{
	EP0CS = bmEP0ACK;
}

static void HandleControlRequest(void)
{
	BOOL res;
	switch(bmRequestType & 0x60)
	{
		case 0:
			res = HandleStandardRequest();
			break;
		case 0x20:
			res = HandleClassRequest();
			break;
		case 0x40:
			res = HandleVendorRequest();
			break;
		default:
			res = FALSE;
	}
	if (!res)
	{
		EP0CS = wLength ? bmEP0STALL : bmEP0NAK;
	}
}

static void HandleUsbEvents()
{
	if (usb_irq)
	{
		if (usb_irq & 0x40)
		{
			if ((USBSTAT & 0x10) && (++err_count < 3))
			{
				USBCTL &= ~bmAttach;
				ResetEPs();
				XREG(0xFE88) = 0;
				XREG(0xFE82) = 0x10;
				while(XREG(0xFE88)!=2);
				USBCTL = bmAttach;
			}       
			else
			{
				XREG(0xF014) = 0;
				usb_irq = 0;
				EX0 = 1;
				return;
			}
		}
		if (usb_irq & bmSpeedChange)
		{
				ResetEPs();
		}
		usb_irq = 0;
	}
	else
	{
		if (UsbIntStsF082 & 0xC0)
		{
			ResetEPs();
			XREG(0xF092) = 0;
			XREG(0xF096) = 0;
			if (UsbIntStsF082 & 0x40)
			{
				XREG(0xF07A) = 1;
			}
		}
		else
		{
			if (UsbIntStsF080 & 1)
			{
				HandleControlRequest();
			}
		}
		UsbIntStsF080 = 0;
		UsbIntStsF082 = 0; 
		UsbIntStsF086 = 0; 
		UsbIntStsF087 = 0;
	}
	EX0 = 1;	
}

void UsbEventLoop(void)
{
	while(1)
	{
		if (UsbIntStsF080 | UsbIntStsF082 | UsbIntStsF086 | UsbIntStsF087 | usb_irq)
		{
			HandleUsbEvents();
		}
       		if (rx_avail)
       		{
       			HandleCBW();
       		}
       		if (have_status)
       		{
       			SendCSW();
       		}
	}
}
