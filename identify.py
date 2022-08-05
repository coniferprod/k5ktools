# Identify and report on Kawai K5000 patch files
# (native or System Exclusive)

import sys
import os

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
    print(f'Treating "{filename}" as native K5000 file')
    print(f'Extension = "{extension}"')

if __name__ == '__main__':
    filename = sys.argv[1]
    pathname, extension = os.path.splitext(filename)
    #print(f'extension = {extension}')

    if extension.lower() == '.syx':
        identify_sysex(filename)
    elif extension.lower() in ['.kaa', '.ka1', '.kca', '.kc1', '.kra']:
        identify_native(filename, extension.lower()[1:])
