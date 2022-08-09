# Identify and report on Kawai K5000 patch files
# (native or System Exclusive)

import sys
import os

import helpers

# key = file size, value = tuple of (PCM count, ADD count)
# This is based on the table by Jens Groh.
single_info = {
    254: (2, 0),
    340: (3, 0),
    426: (4, 0),
    512: (5, 0),
    598: (6, 0),
    1060: (1, 1),
    1146: (2, 1),
    1232: (3, 1),
    1318: (4, 1),
    1404: (5, 1),
    1866: (0, 2),
    1952: (1, 2),
    2038: (2, 2),
    2124: (3, 2),
    2210: (4, 2),
    2758: (0, 3),
    2844: (1, 3),
    2930: (2, 3),
    3016: (3, 3),
    3650: (0, 4),
    3736: (1, 4),
    3822: (2, 4),
    4542: (0, 5),
    4628: (1, 5),
    5434: (0, 6),
}

def is_sysex(data):
    return data[0] == 0xf0 and data[-1] == 0xf7

def is_kawai(data):
    return data[1] == 0x40

def get_tone_map(data):
    tone_data = data[8 : 8 + 19]
    bit_str = ''
    for b in tone_data:
        b_str = '{0:07b}'.format(b)  # exactly seven bits each
        bit_str += b_str[::-1] # reverse it
    flags = []
    flag_str = bit_str[:128] # cut the spurious bits from the last byte
    for bit in flag_str:
        flags.append(True if bit == '1' else False)
    #print(flag_str[:128])
    #print(len(flag_str))
    return flags

def identify_sysex(filename):
    lines = []

    lines.append(f'Treating "{filename}" as MIDI System Exclusive file')

    data = helpers.read_file_data(filename)
    print(f'Read {len(data)} bytes from file')

    is_valid = is_sysex(data) and is_kawai(data)
    if not is_valid:
        lines.append('This file does not contains a System Exclusive message for Kawai')
        return

    channel = data[2] + 1
    lines.append(f'MIDI channel: {channel}')

    # Collect the cardinality, kind and location information from the header:

    cardinality = None
    if data[3] == 0x20:
        cardinality = 'one'
    elif data[3] == 0x21:
        cardinality = 'block'

    # data[4] should always be 00h
    # data[5] should always be 0Ah

    kind = None
    if data[6] == 0x00:
        kind = 'single'
    elif data[6] == 0x10:
        kind = 'drumkit'
    elif data[6] == 0x11:
        kind = 'druminstrument'
    elif data[6] == 0x20:
        kind = 'combi/multi'  # multi on K5000S/R

    location = None  # and remains so for combi/multi and drums
    if data[7] == 0x00:
        location = 'A'
    elif data[7] == 0x01:
        location = 'B'
    # there is no bank C!
    elif data[7] == 0x02:
        location = 'D'
    elif data[7] == 0x03:
        location = 'E'
    elif data[7] == 0x04:
        location = 'F'

    # Construct information lines from the collected info:
    if cardinality == 'block':
        tone_map = get_tone_map(data)
        tone_count = 0
        for tone in tone_map:
            if tone:
                tone_count += 1
        line = f'Contains {tone_count} {kind} tones'
        if location is not None:
            line += f'for bank {location}'
        lines.append(line)
    elif cardinality == 'one':
        tone_num = data[8] + 1
        lines.append(f'Kind: {kind}')
        lines.append(f'Contains {kind} tone {location}{tone_num}')
    else:
        lines.append('Unable to determine patch information')

    return lines

def identify_native(filename, extension):
    lines = []

    lines.append(f'Treating "{filename}" as native K5000 file')

    data = helpers.read_file_data(filename)
    #print(f'Read {len(data)} bytes from file')

    kind_line = f'Extension .{extension}: '
    if extension == 'kaa':
        kind_line += 'Single bank'
    elif extension == 'ka1':
        kind_line += 'One single patch'
    elif extension == 'kca':
        kind_line += 'Combi/multi bank'
    elif extension == 'kc1':
        kind_line += 'One combi/multi patch'
    elif extension == 'kra':
        kind_line += 'Arpeggiator settings'
    else:
        pass

    lines.append(kind_line)

    source_line = f'File size {len(data)} bytes: '
    if extension == 'kaa':
        lines.append('Use kaanalyz.py to get more information about this bank')
    elif extension == 'ka1':
        if len(data) in single_info:
            counts = single_info[len(data)]
            source_line += f'{counts[0]} PCM, {counts[1]} ADD sources'
        else:
            source_line += 'Does not match any valid KA1 file'
        lines.append(source_line)

    return lines

if __name__ == '__main__':
    filename = sys.argv[1]
    pathname, ext = os.path.splitext(filename)

    lines = []

    extension = ext.lower()[1:]
    if extension == 'syx':
        lines = identify_sysex(filename)
    elif extension in ['kaa', 'ka1', 'kca', 'kc1', 'kra']:
        lines = identify_native(filename, extension)

    for line in lines:
        print(line)
