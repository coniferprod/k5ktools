import struct

MAX_PATCH_COUNT = 128
MAX_SOURCE_COUNT = 6
POOL_SIZE = 0x20000
TONE_COMMON_DATA_SIZE = 82
NAME_OFFSET = 40
NAME_LENGTH = 8
SOURCE_COUNT_OFFSET = 51
SOURCE_DATA_SIZE = 86
ADD_KIT_SIZE = 806

def get_pointer_table(data):
    offset = 0
    pointer_table = []
    for p in range(MAX_PATCH_COUNT):
        spec = '>7I'
        entry = struct.unpack_from(spec, data, offset)
        offset += struct.calcsize(spec)

        tone_ptr = entry[0]
        source_ptrs = entry[1:]
        is_used = True if tone_ptr != 0 else False
        if is_used:
            pointer_table.append({'index': p, 'is_used': is_used, 'tone': tone_ptr, 'sources': source_ptrs})
    return pointer_table

def get_high_pointer(data):
    offset = MAX_PATCH_COUNT * 7 * 4  # 128 patch locations with seven pointers of four bytes each
    entry = struct.unpack_from('>I', data, offset)
    return entry[0]

def get_patch_data(data):
    offset = MAX_PATCH_COUNT * 7 * 4 + 4
    return data[offset : offset + POOL_SIZE]

def print_pointer_table(pt):
    for entry in pt:
        print('index: {}'.format(entry['index']))
        print('tone: {}'.format(hex(entry['tone'])))
        print('sources: ')
        for src in entry['sources']:
            print(hex(src))
        print()

def get_bank(data):
    pointer_table = get_pointer_table(data)
    sorted_pointer_table = sorted(pointer_table, key=lambda x: x['tone'])
    #print_pointer_table(sorted_pointer_table)

    high_ptr = get_high_pointer(data)
    #print('high: {}'.format(hex(high_ptr)))

    base_ptr = sorted_pointer_table[0]['tone']
    #print(hex(base_ptr))

    for entry in sorted_pointer_table:
        entry['tone'] -= base_ptr
        entry['sources'] = [ptr - base_ptr if ptr != 0 else ptr for ptr in entry['sources']]
    high_ptr -= base_ptr

    patch_data = get_patch_data(data)

    patches = []

    for ix, p in enumerate(sorted_pointer_table):
        tone_ptr = p['tone']
        source_count = patch_data[tone_ptr + SOURCE_COUNT_OFFSET]
        add_kit_count = sum(x != 0 for x in p['sources'])
        size = TONE_COMMON_DATA_SIZE + SOURCE_DATA_SIZE * source_count + ADD_KIT_SIZE * add_kit_count
        next_ptr = high_ptr
        if ix < len(sorted_pointer_table) - 1:
            next_ptr = sorted_pointer_table[ix + 1]['tone']
        else:
            next_ptr = high_ptr
        padding = next_ptr - tone_ptr - size

        name_offset = tone_ptr + NAME_OFFSET

        # Decode the name as UTF-8, which should be equivalent to the original (probably ASCII;
        # but not specified), except strip out any trailing 0x7f characters which seem to occur
        # from time to time in the patches, they are trouble.
        name = patch_data[name_offset : name_offset + NAME_LENGTH].decode('UTF-8').rstrip('\x7f')

        patches.append({'name': name, 'index': p['index'], 'source_count': source_count,
            'size': size, 'padding': padding, 'tone': tone_ptr, 'sources': p['sources']})

    return {'patches': patches, 'base': base_ptr}
