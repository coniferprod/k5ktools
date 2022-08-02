import sys
import os
import argparse

def read_file_data(filename):
    try:
        with open(filename, 'rb') as f:
            data = f.read()
            #print('Read {} bytes from file {}'.format(len(data), filename))
            return data
    except FileNotFoundError:
        print(f'File not found: {filename}')
        sys.exit(-1)

def check_file_size(length):
    if length in [254, 340, 426, 512, 598, 1060, 1146, 1232, 1318, 1404, 1866, 1952,
                  2038, 2124, 2210, 2758, 2844, 2930, 3016, 3650, 3736, 3822, 4542,
                  4628, 5434]:
        return True
    return False

def parse_tone_number(s):
    name = s[0].upper()
    number = int(s[1:])
    return (name, number)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert Kawai K5000 .KA1 files to MIDI System Exclusive format')
    parser.add_argument(dest='filenames', metavar='filename', nargs='*')
    parser.add_argument('-n', dest='number', action='store', required=True, help='Tone number, like A001 or D127')
    parser.add_argument('-c', type=int, dest='channel', action='store', default=1, help='MIDI channel (1...16)')
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

    (bank_id, tone_number) = parse_tone_number(args.number)
    if not bank_id in ['A', 'B', 'D']:
        print(f'Bank name must be A, B, or D (was {bank_id})')
        sys.exit(-1)
    if tone_number < 0 or tone_number > 127:
        print(f'Tone number must be between 1 and 127 (was {tone_number})')
        sys.exit(-1)
    print(f'Tone number: {bank_id}{tone_number:03}')

    header = bytearray([0xF0, 0x40, 0x00, 0x20, 0x00, 0x0A, 0x00, 0x00, 0x00])

    message = bytearray()

    header[2] = channel - 1  # adjust channel to 0...15
    if bank_id == 'A':
        header[7] = 0x00
    elif bank_id == 'B':
        header[7] = 0x01
    elif bank_id == 'D':
        header[7] = 0x02

    header[8] = tone_number - 1  # tone numbers are zero-based

    data = read_file_data(filename)
    if not check_file_size(len(data)):
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
