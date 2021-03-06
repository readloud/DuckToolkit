Phison 2251-03 (2303) Custom Firmware &amp; Existing Firmware Patches
========

This repository contains the following items:
- DriveCom -- PC C# application to communicate with Phison drives.
- EmbedPayload -- PC C# application to embed Rubber Ducky inject.bin key scripts into custom firmware for execution on the drive.
- Injector -- PC C# application to extract addresses/equates from firmware as well as embed patching code into the firmware.
- firmware -- this is 8051 custom firmware written in C.
- patch -- this is a collection of 8051 patch code written in C.

Releases have the following items:
- patch -- this is a collection of 8051 patch code written in C.
- tools -- these are the compiled binaries of all the tools.
- CFW.bin -- this is custom firmware set up to send an embedded HID payload.

Take note that the firmware patches have only been tested against PS2251-03 firmware version 1.03.53 (which is for an 8K eD3 NAND flash chip). They may work for others, but be careful.

As long as you are using the correct firmware image for your controller version and NAND chip, there is no harm in downgrading to an earlier version (such as from 1.10.53).

## Getting Started
To get started, you'll need to obtain a burner image, which is the 8051 executable responsible for flashing firmware to the drive.

See "Obtaining a Burner Image" on the wiki for more information.

## Build Environment
To patch or modify existing firmware, you must first set up a build environment. See "Setting Up the Environment" on the wiki for more information.

At a minimum, SDCC needs to be installed to C:\Program Files\SDCC.

## Dumping Firmware
Run DriveCom, passing in the drive letter representing the drive you want to flash, the path of the burner image you obtained, and the destination path for the firmware image:

> tools\DriveCom.exe /drive=E /action=DumpFirmware /burner=BN03V104M.BIN /firmware=fw.bin

where "E" is the drive letter, "BN03V104M.BIN" is the path to the burner image, and fw.bin is the resulting firmware dump.

Currently, only 200KB firmware images can be dumped (which is what the Patriot 8GB Supersonic Xpress drive uses).

## Flashing Custom Firmware
Run DriveCom, passing in the drive letter representing the drive you want to flash, the path of the burner image you obtained, and the path of the firmware image you want to flash:

> tools\DriveCom.exe /drive=E /action=SendFirmware /burner=BN03V104M.BIN /firmware=fw.bin

where "E" is the drive letter, "BN03V104M.BIN" is the path to the burner image, and fw.bin is the path to the firmware image.

## Running Demo 1 (HID Payload)
Create a key script in Rubber Ducky format, then use Duckencoder to create an inject.bin version of it:

> java -jar duckencoder.java -i keys.txt -o inject.bin

where "keys.txt" is the path to your key script.

You may notice the delays are not quite the same between the Rubber Ducky and the drive -- you may need to adjust your scripts to compensate.

(These tools are available from https://code.google.com/p/ducky-decode/.)

Once you have an inject.bin file, embed it into the custom firmware with:

> copy CFW.bin hid.bin
> tools\EmbedPayload.exe inject.bin hid.bin

where "inject.bin" is the path to your inject.bin file, and "hid.bin" is the path to the HID payload custom firmware.

(Notice that the firmware image is copied, and the payload is embedded into the copy -- this is because the payload can only be embedded once, so the original CFW.bin must remain intact.)

You can now flash the firmware to your drive with:

> tools\DriveCom.exe /drive=E /action=SendFirmware /burner=BN03V104M.BIN /firmware=hid.bin

where "E" is the drive letter representing your drive, "BN03V104M.BIN" is the path to your burner image, and "hid.bin" is the path to the HID payload custom firmware.

## Running Demo 2 (Hidden Partition Patch)
First, determine the number of logical blocks (sectors) your drive has with the following command:

> tools\DriveCom.exe /drive=E /action=GetNumLBAs

Go into the "patch" directory and modify base.c to disable all other patches, and enable the hidden partition patch:

> //&#35;define FEATURE_CHANGE_PASSWORD

> &#35;define FEATURE_EXPOSE_HIDDEN_PARTITION

Then modify the NUM_LBAS define to the number of logical blocks on your drive:

> &#35;define NUM_LBAS	0xE6C980UL //this needs to be even! (round down)

Make sure you round down to an even number, and it couldn't hurt to subtract a few first, in case a few blocks go bad over time. (For example, if the number of LBAs was 0xE6C981, you might reduce it to 0xE6C940.)

Place the firmware image you want to patch into the "patch" directory and name it "fw.bin."

Go to the "patch" directory and run "build.bat." It will produce a file at patch\bin\fw.bin -- this is the modified firmware image.

You can now flash this file to your drive.

After flashing, Windows may be confused, as it now only sees half of the partition it once did -- it may ask you to format the first time you view either the public or hidden halves of the drive. This is normal.

## Running Demo 3 (Password Patch)
Go into the "patch" directory and modify base.c to disable all other patches, and enable the hidden partition patch:

> &#35;define FEATURE_CHANGE_PASSWORD

> //&#35;define FEATURE_EXPOSE_HIDDEN_PARTITION

Place the firmware image you want to patch into the "patch" directory and name it "fw.bin."

Go to the "patch" directory and run "build.bat." It will produce a file at patch\bin\fw.bin -- this is the modified firmware image.

You can now flash this file to your drive.

## Building From Source
Modify the C files in the "firmware" directory for custom firmware, or the "patch" directory for the firmware patches, then run the "build.bat" file in the appropriate directory.

Once it has built successfully, use DriveCom to flash the resulting file (bin\fw.bin) to your drive:

> tools\DriveCom.exe /drive=E /action=SendFirmware /burner=BN03V104M.BIN /firmware=firmware\bin\fw.bin

...or...

> tools\DriveCom.exe /drive=E /action=SendFirmware /burner=BN03V104M.BIN /firmware=patch\bin\fw.bin

## Questions? Comments? Complaints?
Unfortunately this isn't the most straightforward process at the moment, so if you have questions, e-mail brandonlw@gmail.com and I'll do my best to help (and update the readme/wiki).
