import sys

from bank import get_bank, get_patch_data

if __name__ == '__main__':
    filename = sys.argv[1]

    with open(filename, 'rb') as f:
        data = f.read()
        print('Read {} bytes from file {}'.format(len(data), filename))

        bank = get_bank(data)
        all_patch_data = get_patch_data(data)
        for patch in bank['patches']:
            name = patch['name'].rstrip()
            print('"{}.ka1"'.format(name))
            offset = patch['tone']
            patch_data = all_patch_data[offset : offset + patch['size']]
            print('patch data length = {} bytes'.format(len(patch_data)))

