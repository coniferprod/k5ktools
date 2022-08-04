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

def identify_sysex(filename):
    print(f'Treating {filename} as MIDI System Exclusive file')
    data = read_file_data(filename)
    print(f'Read {len(data)} bytes from file')
    print('TODO: Identify SysEx based on header information')

def identify_native(filename):
    print(f'Treating {filename} as native K5000 file')

if __name__ == '__main__':
    filename = sys.argv[1]
    pathname, extension = os.path.splitext(filename)
    print(f'extension = {extension}')

    if extension == '.syx':
        identify_sysex(filename)
    elif extension in ['.kaa']:
        identify_native(filename)
