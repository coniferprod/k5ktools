import sys
import os
import argparse
import typing

import bank
import helpers

def get_tone_map(patches: list[dict[str, typing.Any]]) -> bytes:
    tone_bits = ['0'] * 128
    for patch in patches:
        number = patch['index']
        #print(f'patch number = {number}')
        tone_bits[number] = '1'
    #print('tone map: ', tone_bits)

    # Split the bits into groups of seven:
    groups = [tone_bits[i:i + 7] for i in range(0, len(tone_bits), 7)]
    #print(f'number of groups = {len(groups)}')

    buf = bytearray()
    byte_num = 1
    for group in groups:
        bits = ''
        for b in reversed(group):  # need to reverse because bit0 = A001, bit1 = A002 etc.
            bits += b
        #print(f'bits for byte number {byte_num}: {bits}')
        by = int(bits, 2)
        #print(f'byte = {by:02X}')
        buf += bytes([by])
        byte_num += 1

    return bytes(buf)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert Kawai K5000 .KAA files to MIDI System Exclusive format')
    parser.add_argument(dest='filenames', metavar='filename', nargs='*')
    parser.add_argument('-c', type=int, dest='channel', action='store', default=1, help='MIDI channel (1...16)')
    parser.add_argument('-b', dest='bank_id', action='store', required=True, help='Bank identifier (A, B, D, E, F)')
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

    data = helpers.read_file_data(filename)

    bank_id = args.bank_id.upper()
    if not bank_id in ['A', 'B', 'D', 'E', 'F']:
        print(f'Bank name must be A, B, D, E or F (was {bank_id})')
        sys.exit(-1)
    print(f'Bank identifier: {bank_id}')

    bank_data = bank.get_bank(data)
    final_patches = sorted(bank_data['patches'], key=lambda x: x['index'])

    patch_data = bytearray()
    for patch in final_patches:
        print(f'{patch["index"]} {patch["name"]}  {hex(patch["tone"])}')
        patch_data += patch['data']

    header = bytearray([0xF0, 0x40, 0x00, 0x21, 0x00, 0x0A, 0x00, 0x00])
    header[2] = channel - 1  # adjust channel to 0...15
    if bank_id == 'A':
        header[7] = 0x00
    elif bank_id == 'B':
        header[7] = 0x01
    elif bank_id == 'D':
        header[7] = 0x02
    elif bank_id == 'E':
        header[7] == 0x03
    elif bank_id == 'F':
        header[7] == 0x04

    message = bytearray()
    message += header
    tone_map = get_tone_map(final_patches)
    #print(f'tone map = {tone_map}, length = {len(tone_map)}')
    message += tone_map
    message += patch_data
    message += bytes([0xf7])

    pathname, extension = os.path.splitext(filename)
    out_filename = pathname.split('/')[-1] + '.syx'
    if args.outfile is not None:
        out_filename = args.outfile
    print(f'Writing {len(message)} bytes to "{out_filename}"')
    helpers.write_file_data(out_filename, message)
