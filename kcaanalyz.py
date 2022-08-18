import os
import sys
import argparse

import helpers
import multi

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert Kawai K5000 .KCA files to MIDI System Exclusive format')
    parser.add_argument(dest='filenames', metavar='filename', nargs='*')
    parser.add_argument('-c', type=int, dest='channel', action='store', default=1, help='MIDI channel 1...16')
    parser.add_argument('-o', dest='outfile', action='store', help='Output file (defaults to original name with .syx extension)')
    args = parser.parse_args()

    #filename = args.filenames[0]

    # TODO: Work in progress, don't use yet.
