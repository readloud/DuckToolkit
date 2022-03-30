#include "PS2303.h"

static BYTE 	tmr0count, led_ticks, led_timer;

void tmr0isr(void) __interrupt TMR0_VECT
{
	//approx. 10 times per second
	TR0 = 0;
	TL0 = 0xE6;
	TH0 = 0x96;
	TR0 = 1;
	// led blink
	if ((GPIO0OUT & 2)==0) //turned off
	{
		return;
	}
	tmr0count++;
	led_ticks++;
	if (led_ticks<10)
	{
		return;
	}
	led_ticks = 0;
	if (led_timer>=31)
	{
		GPIO0OUT = 1;
		led_timer = 0;		
		return;
	}
	if (led_timer>=10)
	{
		GPIO0OUT = ~GPIO0OUT;
		led_timer++;
		return;
	}
	if (led_timer==0)
	{
		return;
	}
	//0<led_timer<10 - blink each second
	if ((GPIO0OUT & 1)!=0)
	{
		GPIO0OUT &= 0xFE;
	}
	else
	{
		GPIO0OUT |= 1;
	}
}

void InitLED(void)
{
	tmr0count = 0;
	GPIO0OUT = 3;
	led_ticks = 0;
	led_timer = 0;
	EA = 1;
	ET0 = 1;
	TR0 = 1;
}

void LEDBlink(void)
{
	GPIO0OUT = 2;
	led_timer = 1;
}

void LEDBlinkOnce(void)
{
	GPIO0OUT = 3;
	led_timer = 10;
}

void LEDOff(void)
{
	GPIO0OUT = 3;
	led_timer = 0;
}
	