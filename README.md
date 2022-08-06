# k5ktools

Rewrites of old tools that deal with Kawai K5000 native patch file formats.

See the DigitalSynth.net post [Making Sense of Kawai K5000 Patch Data Files](https://digitalsynth.net/posts/2022/07/30/making-sense-of-kawai-k5000-patch-data-files/) for the backstory and details.

To run the programs, you need to have a Python 3 environment installed.
See [Downloading Python](https://wiki.python.org/moin/BeginnersGuide/Download)in the Python wiki for details.

## kaanalyz.py

This is a rewrite of Jens Groh's `kaanalyz` program in Python 3. It was originally written
in C, but staring hard at the code I was able to determine the structure of
the K5000 .KAA files, to be able to replicate it in Python.

The program does not have all the features of the original; the options
to sort the patches are missing, and it can't extract the contents of the bank into individual
.KA1 files (the latter is intentional, since there is a `kaatoka1` utility waiting for a rewrite.)

To run, issue the command `python3 kaanalyz.py myfile.kaa`, where `myfile.kaa` should
be a valid K5000 .KAA bank file.

## ka1tosyx.py

This is a sort of rewrite of the original `ka1tosyx` utility, but actually it's implemented
from scratch. I don't know who wrote the original, because there was no source code, and I wasn't
able to even run it, so this version was developed from the obvious idea that .KA1 files can be
mechanically converted into equivalent MIDI System Exclusive files.

For a SysEx file you need the MIDI channel (1 to 16) and the tone number (like A001, D070 etc.).
These are supplied as program options. If you don't specify an output filename, the name part of
the original .KA1 file will be used, but the extension will be `.syx`. For example, if you pass in
`TIMESURF.KA1`, the output file will be `TIMESURF.syx` unless you specify something else with the
`-o` option.

The full command to convert `TIMESURF.KA1` to a System Exclusive file called `TIMESURF.syx`,
using MIDI channel 1 and tone number D070, would be:

    python3 ka1tosyx.py TIMESURF.KA1 -c 1 -n d070

Use `python3 ka1tosyx.py -h` for a description of the program options.

## kaatosyx.py

Jens Groh wrote the original `kaatosyx` utility, and Jeremy Bernstein ported it to OS X
in 2006. It is based on the `kaanalyz` utility, and uses the same bank analysis code.
I have also reused the new Python code from the new `kaanalyz`.

Looking at the K5000 MIDI specification, it seems that the block single dump files
have `21` as the fourth header byte, instead of `20` as in the `kaatosyx` original
source code. I used `21` and tested a .KAA bank converted to SysEx with the new
Python utility, and my K5000S received the full bank just fine. If you have used
the original `kaatosyx` utility successfully, please let me know. I couldn't run
Jeremy Bernstein's OS X version in macOS Monterey; I only got a message from the
zsh shell: `bad CPU type in executable`, because the binary Mach-O executables
for both 32-bit Intel (i386) and the obsolete PowerPC, but not for x86_64.

There are also some additional options in this Python version, which I deemed
necessary to get a proper bank in SysEx format. The MIDI System Exclusive has the
MIDI channel hardwired, but also the K5000 bank identifier is indicated in the
header. It is specified with the `-b` option.

If you try to use bank identifiers that are not available on your K5000
(like if you use bank E but don't have the ME-1 board installed), then probably
nothing will happen, but if anything bad happens (like you lose some data on your
K5000), then I can't be held responsible.

Here is the full command to convert a bank file like `Collctn1.kaa` to a MIDI System Exclusive
file called `Collctn1.syx`, transferred on MIDI channel 1 (the default) and intended to go to bank D:

    python3 kaatosyx.py Collctn1.kaa -b d

Use `python3 kaatosyx.py -h` for a description of the program options.

## identify.py

Attemps to identify a native K5000 file or a MIDI System Exclusive file and give some
information about its content.

For example, this is how you would examine a .KA1 file:

    python3 identify.py ADDEnsem.KA1

You would get back something like this:

    Treating "ADDEnsem.KA1" as native K5000 file
    Extension .ka1: One single patch
    File size 3650 bytes: 0 PCM, 4 ADD sources

The KA1 file sizes are checked against a table originally compiled by Jens Groh.

Hopefully this identification script can be augmented to cover more file types.

## License

Licensed under the MIT License. Copyright (C) 2022 Conifer Productions Oy.
