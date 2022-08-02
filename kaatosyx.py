import sys
import os
import argparse

from bank import get_bank, get_patch_data

KAA_HEADER = bytes([0xF0, 0x40, 0x00, 0x20, 0x00, 0x0A, 0x00, 0x00])
KAA_FOOTER = bytes([0xF7])

def read_file_data(filename):
    try:
        with open(filename, 'rb') as f:
            data = f.read()
            #print('Read {} bytes from file {}'.format(len(data), filename))
            return data
    except FileNotFoundError:
        print(f'File not found: {filename}')
        sys.exit(-1)

def get_tone_map(bank):
    return bytes()

def write_syx_file(filename, bank, data):
    file = open(filename, 'wb')
    file.write(KAA_HEADER)
    file.write(get_tone_map(bank))
    file.write(data)
    file.write(KAA_FOOTER)
    file.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert Kawai K5000 .KAA files to MIDI System Exclusive format')
    parser.add_argument(dest='filenames', metavar='filename', nargs='*')
    parser.add_argument('-c', type=int, dest='channel', action='store', default=1, help='MIDI channel (1...16)')
    parser.add_argument('-o', dest='outfile', action='store', help='Output file (defaults to original name with .syx extension)')
    args = parser.parse_args()

    filename = args.filenames[0]
    print(f'File: {filename}')
    data = read_file_data(filename)

    bank = get_bank(data)
    bank_data = bytes([])
    final_patches = sorted(bank['patches'], key=lambda x: x['index'])
    for patch in final_patches:
        pass

    header = bytearray([0xF0, 0x40, 0x00, 0x20, 0x00, 0x0A, 0x00, 0x00, 0x00])

    message = bytearray()
    message += header
    message += data
    message += bytes([0xf7])

    pathname, extension = os.path.splitext(filename)
    out_filename = pathname.split('/')[-1] + '.syx'
    if args.outfile is not None:
        out_filename = args.outfile
    print(f'Writing {len(message)} bytes to "{out_filename}"')
    write_syx_file(out_filename, bank, message)
