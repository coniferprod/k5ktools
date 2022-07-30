# k5ktools

Rewrites of old tools that deal with Kawai K5000 native patch file formats.

See the DigitalSynth.net post [https://digitalsynth.net/posts/2022-07-30/making-sense-of-kawai-k5000-patch-data-files/](Making Sense of Kawai K5000 Patch Data Files) for
the backstory and details.

To run the programs, you need to have a Python 3 environment installed.
See [https;//python.org](Python home page) for details.

## kaanalyz

This is a rewrite of Jens Groh's `kaanalyz` program in Python 3. It was originally written
in C, but staring hard at the code I was able to determine the structure of
the K5000 .KAA files. The program does not have all the features of the original; the options
to sort the patches are missing, and it can't extract the contents of the bank into inidividual
.KA1 files (the latter is intentional, since there is a `kaatoka1` utility waiting for a rewrite.)

To run, issue the command `python3 kaanalyz.py myfile.kaa`, where `myfile.kaa` should
be a valid K5000 .KAA bank file.

## License

Licensed under the MIT License. Copyright (C) 2022 Conifer Productions Oy.
