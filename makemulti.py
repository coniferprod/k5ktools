import sys
import os
import argparse

import helpers
import multi

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Make a new multi/combi file for Kawai K5000 in System Exclusive format')
    parser.add_argument('-c', type=int, dest='channel', action='store', default=1, help='MIDI channel (1...16)')
    parser.add_argument('-i', type=int, dest='instrument', action='store', default=1, help='Multi/combi instrument number')
    parser.add_argument('-o', dest='outfile', action='store', help='Output file name')
    args = parser.parse_args()

    filename = sys.argv[1]
    pathname, ext = os.path.splitext(filename)

    channel = args.channel
    if channel < 1 or channel > 16:
        print(f'MIDI channel must be between 1 and 16 (was {channel})')
        sys.exit(-1)
    else:
        print(f'MIDI channel: {channel}')

    instrument = args.instrument
    if instrument < 1 or instrument > 64:
        print(f'Instrument number must be between 1 and 64 (was {instrument})')
        sys.exit(-1)
    else:
        print(f'Instrument number: {channel}')

    header = bytearray([0xF0, 0x40, 0x00, 0x20, 0x00, 0x0A, 0x20, 0x00])
    header[2] = channel - 1  # adjust channel to 0...15
    header[7] = instrument - 1

    message = bytearray()
    message += header

    multi_patch = multi.MultiPatch(
        checksum=0x00,  # don't care at this point
        effect=multi.EffectSettings(
            algorithm=1,
            reverb=multi.Reverb(
                reverb_type=1, # are these zero-based or one-based?
                dry_wet1=0,
                dry_wet2=0,
                param2=0,
                param3=0,
                param4=0
            ),
            effect1=multi.Effect(
                effect_type=1,
                dry_wet=0,
                param1=0,
                param2=0,
                param3=0,
                param4=0
            ),
            effect2=multi.Effect(
                effect_type=1,
                dry_wet=0,
                param1=0,
                param2=0,
                param3=0,
                param4=0
            ),
            effect3=multi.Effect(
                effect_type=1,
                dry_wet=0,
                param1=0,
                param2=0,
                param3=0,
                param4=0
            ),
            effect4=multi.Effect(
                effect_type=1,
                dry_wet=0,
                param1=0,
                param2=0,
                param3=0,
                param4=0
            ),
            geq=[0, 0, 0, 0, 0, 0, 0]
        ),
        common=multi.Common(
            name='NewMulti',
            volume=100,
            mutes=[False, False, True, True],
            control1=multi.Control(
                source=1,
                destination=1,
                depth=0
            ),
            control2=multi.Control(
                source=1,
                destination=1,
                depth=0
            )
        ),
        sections=[
            multi.Section(
                instrument=100,
                volume=100,
                pan=0,
                effect_path=1,
                transpose=0,
                tune=0,
                zone=(0, 127),
                vel_sw=multi.VelocitySwitching(
                    sw_type=0,
                    amount=0
                ),
                receive_channel=1
            ),
            multi.Section(
                instrument=100,
                volume=100,
                pan=0,
                effect_path=1,
                transpose=0,
                tune=0,
                zone=(0, 127),
                vel_sw=multi.VelocitySwitching(
                    sw_type=0,
                    amount=0
                ),
                receive_channel=2
            ),
            multi.Section(
                instrument=100,
                volume=100,
                pan=0,
                effect_path=1,
                transpose=0,
                tune=0,
                zone=(0, 127),
                vel_sw=multi.VelocitySwitching(
                    sw_type=0,
                    amount=0
                ),
                receive_channel=3
            ),
            multi.Section(
                instrument=100,
                volume=100,
                pan=0,
                effect_path=1,
                transpose=0,
                tune=0,
                zone=(0, 127),
                vel_sw=multi.VelocitySwitching(
                    sw_type=0,
                    amount=0
                ),
                receive_channel=4
            )
        ]
    )
    print(multi_patch)

    message += multi_patch.as_data()
    message += bytes([0xf7])

    if args.outfile is not None:
        out_filename = args.outfile
    print(f'Writing {len(message)} bytes to "{out_filename}"')
    helpers.write_file_data(out_filename, message)
