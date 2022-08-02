# k5ktools

Rewrites of old tools that deal with Kawai K5000 native patch file formats.

See the DigitalSynth.net post [Making Sense of Kawai K5000 Patch Data Files](https://digitalsynth.net/posts/2022-07-30/making-sense-of-kawai-k5000-patch-data-files/) for the backstory and details.

To run the programs, you need to have a Python 3 environment installed.
See [Downloading Python](https://wiki.python.org/moin/BeginnersGuide/Download)in the Python wiki for details.

## kaanalyz

This is a rewrite of Jens Groh's `kaanalyz` program in Python 3. It was originally written
in C, but staring hard at the code I was able to determine the structure of
the K5000 .KAA files, to be able to replicate it in Python.

The program does not have all the features of the original; the options
to sort the patches are missing, and it can't extract the contents of the bank into individual
.KA1 files (the latter is intentional, since there is a `kaatoka1` utility waiting for a rewrite.)

To run, issue the command `python3 kaanalyz.py myfile.kaa`, where `myfile.kaa` should
be a valid K5000 .KAA bank file.

## ka1tosyx

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

## License

Licensed under the MIT License. Copyright (C) 2022 Conifer Productions Oy.
