# Identify and report on Kawai K5000 patch files
# (native or System Exclusive)

import sys
import os

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

def read_file_data(filename):
    try:
        with open(filename, 'rb') as f:
            data = f.read()
            #print('Read {} bytes from file {}'.format(len(data), filename))
            return data
    except FileNotFoundError:
        print(f'File not found: {filename}')
        sys.exit(-1)

def is_sysex(data):
    return data[0] == 0xf0 and data[-1] == 0xf7

def is_kawai(data):
    return data[1] == 0x40

def identify_sysex(filename):
    print(f'Treating "{filename}" as MIDI System Exclusive file')
    data = read_file_data(filename)
    print(f'Read {len(data)} bytes from file')

    is_valid = is_sysex(data) and is_kawai(data)
    if not is_valid:
        print('This file does not contains a System Exclusive message for Kawai')
        return

def identify_native(filename, extension):
    lines = []

    lines.append(f'Treating "{filename}" as native K5000 file')

    data = read_file_data(filename)
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

    for line in lines:
        print(line)

if __name__ == '__main__':
    filename = sys.argv[1]
    pathname, extension = os.path.splitext(filename)
    #print(f'extension = {extension}')

    if extension.lower() == '.syx':
        identify_sysex(filename)
    elif extension.lower() in ['.kaa', '.ka1', '.kca', '.kc1', '.kra']:
        identify_native(filename, extension.lower()[1:])
