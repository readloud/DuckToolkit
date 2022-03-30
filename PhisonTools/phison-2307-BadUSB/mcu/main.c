#include "PS2303.h"
#include "config.h"
#include "led.h"
#include "ticks.h"
#include "usb.h"

extern void usb_isr(void) __interrupt USB_VECT;
extern void ep_isr(void) __interrupt EP_VECT;
extern void tmr0isr(void) __interrupt TMR0_VECT;
extern void com0isr(void) __interrupt COM0_VECT;
extern void tmr1isr(void) __interrupt TMR1_VECT;

void HwInit0()
{
	// ram mapping
	BANK0PAL = BANK0_PA>>9;
	BANK0PAH = BANK0_PA>>17;

	BANK1VA  = BANK1_VA>>8;
	BANK1PAL = BANK1_PA>>9;
	BANK1PAH = BANK1_PA>>17;

	BANK2VA  = BANK2_VA>>8;
	BANK2PAL = BANK2_PA>>9;
	BANK2PAH = BANK2_PA>>17;

	XREG(0xF809) = 7;
	XREG(0xF80A) = 0x1F;

	XREG(0xF810) = 0x60;
	XREG(0xF811) = 0;
//	XREG(0xF810) = 0xC0;
//	XREG(0xF811) = 0;

	XREG(0xF08F) = 0;

	XREG(0xFA6F) = 0x1F;
	XREG(0xFA60) = 2;
	XREG(0xFA61) = 0;
	XREG(0xFA64) = 0;
	XREG(0xFA65) = 0;
	XREG(0xFA66) = 0;
	XREG(0xFA67) = 0;
	XREG(0xFA62) = 0x0F;
	XREG(0xFA6F) = 0x1F;

	GPIO0DIR &= 0xFD;
	GPIO0OUT |= 2;

	XREG(0xFA21) = 7;
	XREG(0xFA21) &= 0xFB;

	XREG(0xFA68) &= 0xF7;
	XREG(0xFA69) &= 0xF7;
	XREG(0xFA6A) &= 0xF7;
	XREG(0xFA6B) &= 0xF7;

	XREG(0xFE00) = 0;
	XREG(0xFE00) = 0x80;

	XREG(0xFA50) = 0x20;

	XREG(0xFE01) = 0;
	XREG(0xFE02) = 0x45;
}

void InitCore()
{
	TMOD = 0x11;  //both timers are 16-bit, no gating, internal source

	TH0 = 0xF0;
	TL0 = 0x5F;

	TH1 = 0xF0;
	TL1 = 0x5F;

	IP = 1;
	TCON = 0x10;
	SCON = 0;
	IE = 0x80;
}

void HwInit2()
{
	if (XREG(0xFA38) & 2)
	{
		return;
	}
	REGBANK = 5;
	XREG(0xF210) = 0xFF;
	XREG(0xF211) = 2;
	XREG(0xF212) = 3;
	XREG(0xF213) = 0x24;
	REGBANK = 0;
	XREG(0xFA6B) = 0xFF;
	while((XREG(0xF014) & 3)==0);
}

void main()
{
	HwInit0();
	InitCore();
	InitLED();
	InitTicks();
	HwInit2();
	InitUsb();
	//HwInit4();
	LEDBlink();
/* USB renumerate
	USBCTL &= ~bmAttach;
	EPIE = 2;
	EP1.cs = 0;
	EP2.cs = 0;
	EP3.cs = 0;
	EP4.cs = 0;

	XREG(0xFE88) = 0;
	XREG(0xFE82) = 0x10;
	while(XREG(0xFE88)!=2);
	USBCTL = bmAttach | 4;
*/
//	PRAMCTL &= ~bmPRAM;
	UsbEventLoop(); //forever
}
