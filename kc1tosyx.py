import os
import sys
import argparse

import helpers
import multi

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert Kawai K5000 .KC1 files to MIDI System Exclusive format')
    parser.add_argument(dest='filenames', metavar='filename', nargs='*')
    parser.add_argument('-n', type=int, dest='number', action='store', required=True, help='Multi/combi number 1...64')
    parser.add_argument('-c', type=int, dest='channel', action='store', default=1, help='MIDI channel 1...16')
    parser.add_argument('-o', dest='outfile', action='store', help='Output file (defaults to original name with .syx extension)')
    args = parser.parse_args()

    filename = args.filenames[0]
    print(f'File: {filename}')

    channel = args.channel
    if channel < 1 or channel > 16:
        print(f'MIDI channel must be between 1 and 16 (was {channel})')
        sys.exit(-1)
    else:
        print(f'MIDI channel: {channel}')

    number = args.number
    if number < 1 or number > 64:
        print(f'Multi/combi number must be between 1 and 64 (was {number})')
        sys.exit(-1)
    else:
        print(f'Multi/combi number: {number}')

    header = bytearray([0xF0, 0x40, 0x00, 0x20, 0x00, 0x0A, 0x20, 0x00])
    header[2] = channel - 1  # adjust channel to 0...15
    header[7] = number - 1 # adjust multi number to 0...63

    message = bytearray()

    data = helpers.read_file_data(filename)
    if not multi.check_size(len(data)):
        print(f'File size does not appear to be valid (was {len(data)} bytes)')
        sys.exit(-1)

    message += header
    message += data
    message += bytes([0xf7])

    pathname, extension = os.path.splitext(filename)
    out_filename = pathname.split('/')[-1] + '.syx'
    if args.outfile is not None:
        out_filename = args.outfile
    print(f'Writing {len(message)} bytes to "{out_filename}"')
    with open(out_filename, 'wb') as out_file:
        out_file.write(bytes(message))
