#include "PS2303.h"

static BYTE 	tmr1count;
static WORD	tmr1reload;

void tmr1isr(void) __interrupt TMR1_VECT
{
	TR1 = 0;
	TH1 = MSB(tmr1reload);
	TL1 = LSB(tmr1reload);
	tmr1count++;
	TR1 = 1;
}

void InitTicks()
{
	if (XREG(0xFA60)==0x0F)
	{
		tmr1reload = 0xF63C;
	}
	else
	{
		tmr1reload = 0-(2500/(XREG(0xFA60)+2));
	}
	tmr1count = 0;
	TR1 = 0;
	ET1 = 1;
	TMOD = TMOD & 0x0F | 0x10; //T1 mode: 16-bit counter, source is CLKOUT/4, count when TR1=1
//	TR1 = 1;
}

BYTE GetTickCount(void)
{
	return tmr1count;
}
