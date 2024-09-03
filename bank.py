import struct
import typing

MAX_PATCH_COUNT = 128
MAX_SOURCE_COUNT = 6
POOL_SIZE = 0x20000
TONE_COMMON_DATA_SIZE = 82
NAME_OFFSET = 40
NAME_LENGTH = 8
SOURCE_COUNT_OFFSET = 51
SOURCE_DATA_SIZE = 86
ADD_KIT_SIZE = 806

# key = file size, value = tuple of (PCM count, ADD count)
# This is based on the table by Jens Groh.
SINGLE_INFO = {
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

def check_single_size(length: int) -> bool:
    return length in SINGLE_INFO

def get_single_name(number: int) -> str:
    if number in range(0, 128):
        return f'G{number + 1:03}'
    elif number in range(128, 256):
        return f'B{number - 128 + 1:03}'
    elif number in range(256, 384):
        return f'A{number - 256 + 1:03}'
    elif number in range(384, 512):
        return f'D{number - 384 + 1:03}'
    elif number in range(512, 640):
        return f'E{number - 512 + 1:03}'
    elif number in range(640, 768):
        return f'F{number - 640 + 1:03}'
    return ''

def get_pointer_table(data: bytes) -> list[dict[str, typing.Any]]:
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

def get_high_pointer(data: bytes) -> int:
    offset = MAX_PATCH_COUNT * 7 * 4  # 128 patch locations with seven pointers of four bytes each
    entry = struct.unpack_from('>I', data, offset)
    return int(entry[0])

def get_patch_data(data: bytes) -> bytes:
    offset = MAX_PATCH_COUNT * 7 * 4 + 4
    return data[offset : offset + POOL_SIZE]

def print_pointer_table(pt: dict[str, typing.Any]) -> None:
    for entry in pt:
        index = entry['index']
        print(f'index: {index}')
        tone = entry['tone']
        print(f'tone: {tone:X}')
        print('sources: ')
        for src in entry['sources']:
            print(hex(src))
        print()

def get_bank(data: bytes) -> dict[str, typing.Any]:
    pointer_table = get_pointer_table(data)
    sorted_pointer_table = sorted(pointer_table, key=lambda x: x['tone'])
    print(f"Pointer table has {len(sorted_pointer_table)} pointers")
    #print_pointer_table(sorted_pointer_table)

    high_ptr = get_high_pointer(data)
    print('high: {}'.format(hex(high_ptr)))

    base_ptr = sorted_pointer_table[0]['tone']
    print('base: {}'.format(hex(base_ptr)))

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
            'size': size, 'padding': padding, 'tone': tone_ptr, 'sources': p['sources'],
            'data': patch_data[tone_ptr : tone_ptr + size]})

    return {'patches': patches, 'base': base_ptr}
