import sys

import bank

def percentage(part, whole):
    percentage = 100 * float(part)/float(whole)
    return f'{percentage:.2f}%'

def read_file_data(filename):
    try:
        with open(filename, 'rb') as f:
            data = f.read()
            #print('Read {} bytes from file {}'.format(len(data), filename))
            return data
    except FileNotFoundError:
        print(f'File not found: {filename}')
        sys.exit(-1)

if __name__ == '__main__':
    filename = sys.argv[1]

    format = 'text'

    data = read_file_data(filename)

    bank_data = bank.get_bank(data)
    #print_bank(bank_data)

    final_patches = sorted(bank_data['patches'], key=lambda x: x['index'])
    total_size = sum(x['size'] for x in final_patches)

    if format == 'text':
        print(f'"{filename}" contains {len(final_patches)} patches using {total_size} bytes ({percentage(total_size, bank.POOL_SIZE)} of memory).'.format(filename, len(final_patches),
            total_size, percentage(total_size, bank.POOL_SIZE)))
        print('{} bytes ({} of memory) free.'.format(bank.POOL_SIZE - total_size, percentage(bank.POOL_SIZE - total_size, bank.POOL_SIZE)))
        print(f'Base address = 0x{bank_data["base"]:08X}.  Patches:')
        print('number name      sources size  pointer  padding')
    for ix, patch in enumerate(final_patches):
        add_count = 0
        pcm_count = 0
        source_str = ''
        for source_index in range(patch['source_count']):
            if patch['sources'][source_index] != 0:
                add_count += 1
                source_str += 'A'
            else:
                pcm_count += 1
                source_str += 'P'
        # Fill up with dashes for unused sources.
        # The sources are not necessarily in this order, but only the counts matter here.
        source_str += '-' * (bank.MAX_SOURCE_COUNT - patch['source_count'])

        if format == 'text':
            print(f' {patch["index"]+1:>4d}  {patch["name"]:8}  {source_str}  {patch["size"]:>4}  0x{patch["tone"]:06X}   {patch["padding"]:>5}')
        elif format == 'csv':
            print(f'{patch["index"]+1},"{patch["name"]}",{source_str},{patch["size"]},0x{patch["tone"]:06X},{patch["padding"]}')
