import sys
import os
import argparse

import levels
import helpers


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate harmonic levels for various waveforms as System Exclusive files')
    parser.add_argument('-w', dest='waveform', action='store', required=True, help='Waveform name (saw, sqr, tri, sin)')
    parser.add_argument('-c', type=int, dest='channel', action='store', default=1, help='MIDI channel (1...16)')
    parser.add_argument('-s', type=int, dest='source_number', action='store', default=1, help='Source number 1...6')
    parser.add_argument('-o', dest='outfile', action='store', help='Output file name')
    args = parser.parse_args()

    harm_levels = levels.get_harmonic_levels(args.waveform)

    channel = args.channel
    if channel < 1 or channel > 16:
        print(f'MIDI channel must be between 1 and 16 (was {channel})')
        sys.exit(-1)
    else:
        print(f'MIDI channel: {channel}')

    source_number = args.source_number
    if source_number < 1 or source_number > 6:
        print(f'Source number must be between 1 and 6 (was {source_number}')
        sys.exit(-1)
    else:
        print(f'Source number: {source_number}')

    harm_levels = levels.get_harmonic_levels(args.waveform)

    messages = []

    for group_num in range(2):
        for i, h in enumerate(harm_levels):
            hc = 0x40 + group_num

            message = bytearray([
                0xf0,  # start SysEx
                0x40,  # Kawai ID
                channel,
                0x10, # function number
                group_num, # group number
                0x0a, # machine number
                0x02, # "Single Tone ADD Wave Parameter"
                hc,
                source_number - 1, # 00h...05h
                i, 0, 0, h,
                0xf7
            ])

            messages.append(message)

    all_message_data = bytearray()
    for message in messages:
        all_message_data.extend(message)

    helpers.write_file_data(args.outfile, all_message_data)
