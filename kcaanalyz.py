import os
import sys
import argparse

import helpers
import multi

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze a Kawai K5000 .KCA file')
    parser.add_argument(dest='filenames', metavar='filename', nargs='*')
    args = parser.parse_args()

    filename = args.filenames[0]

    data = helpers.read_file_data(filename)
    if not multi.check_size(len(data) / multi.MULTI_COUNT):
        print(f'File size does not appear to be valid (was {len(data)} bytes)')
        sys.exit(-1)

    multi_chunks = [data[i:i + multi.MULTI_DATA_SIZE] for i in range(0, len(data), multi.MULTI_DATA_SIZE)]
    multis = []
    for chunk in multi_chunks:
        multis.append(multi.MultiPatch.from_data(chunk))

    for n, m in enumerate(multis):
        print(f'M{n+1:02} {m.common.name}')
