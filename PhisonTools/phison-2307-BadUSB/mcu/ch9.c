#include "PS2303.h"
#include "usb.h"
#include "ch9.h"

static BOOL GetStatus()
{
	return FALSE;
}

static BOOL ClearFeature()
{
	return FALSE;
}

static BOOL SetFeature()
{
	return FALSE;
}

static BOOL SetAddress()
{
	if (wValue<0x7F)
	{
		usb_addressed = (wValue!=0);
		EP0ACK();
		return TRUE;
	}
	return FALSE;
}

static BOOL GetDescriptor()
{
	return FALSE;
}

static BOOL SetDescriptor()
{
	return FALSE;
}

static BOOL GetConfiguration()
{
	return FALSE;
}

static BOOL SetConfiguration()
{
	if (wValue<=1)
	{
		usb_config = wValue;
		EP0ACK();
		return TRUE;
	}
	return FALSE;
}

static BOOL GetInterface()
{
	return FALSE;
}

static BOOL SetInterface()
{
	return FALSE;
}

static BOOL Req30()
{
	return FALSE;
}


BOOL HandleStandardRequest()
{
	switch(bRequest)
	{
		case USB_REQ_GET_STATUS:
			return GetStatus();
		case USB_REQ_CLEAR_FEATURE:
			return ClearFeature();
		case USB_REQ_SET_FEATURE:
			return SetFeature();
		case USB_REQ_SET_ADDRESS:
			return SetAddress();
		case USB_REQ_GET_DESCRIPTOR:
			return GetDescriptor();
		case USB_REQ_SET_DESCRIPTOR:
			return SetDescriptor();
		case USB_REQ_GET_CONFIGURATION:
			return GetConfiguration();
		case USB_REQ_SET_CONFIGURATION:
			return SetConfiguration();
		case USB_REQ_GET_INTERFACE:
			return GetInterface();
		case USB_REQ_SET_INTERFACE:
			return SetInterface();
		case 0x30: //WTF?
			return Req30();
		default:
			return FALSE;
	}
}
