#ifndef _USB_H_INCLUDED
#define _USB_H_INCLUDED

void InitUsb(void);
void UsbEventLoop(void);

void EP0ACK();

void UsbTxDma(WORD size, BYTE page);

void UsbTxDmaTest(WORD size, BYTE page, BYTE r5, BYTE r6, BYTE r7, BYTE r8);

extern BYTE	bmRequestType;
extern BYTE	bRequest;
extern WORD	wValue;
extern WORD	wIndex;
extern WORD	wLength;

extern BYTE 	usb_config;
extern BYTE	usb_speed;
extern BOOL	usb_addressed;

extern __xdata volatile BYTE EPBUF[1024];

#endif
