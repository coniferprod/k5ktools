import os
import sys
import argparse

import helpers
import multi
import bank

def report_multi(data: bytes) -> list[str]:
    lines = []

    #checksum = data[0]
    mute_byte = data[48] & 0x0f  # mask off top 4 bits in case there is junk
    mute_bits = bin(mute_byte)[2:].zfill(4)  # strip off the '0b' prefix, pad left with zeros to four bits
    #print(f'mute_bits = {mute_bits}')

    sections = []
    for i in range(4):
        sections.append({'number': i + 1})

    section_num = 1
    for mb in reversed(mute_bits):  # reversed to get natural section order
        sections[section_num - 1]['mute'] = False if mb == '1' else True # 0=mute, 1=active
        section_num += 1

    section_data = data[55:]
    section_chunks = [section_data[i:i + 12] for i in range(0, len(section_data), 12)]
    section_num = 1
    for chunk in section_chunks:
        # Combine the MSB and LSB into a 9-bit value
        msb = bin(chunk[0])[2:].zfill(2) # strip off the '0b' prefix, pad left to two bits
        lsb = bin(chunk[1])[2:].zfill(7)
        single_number = int(msb + lsb, 2) # convert the combined msb + lsb bit string into a number
        sections[section_num - 1]['single'] = single_number
        section_num += 1

    for section in sections:
        if not section['mute']:
            lines.append(f'Section {section["number"]}: {bank.get_single_name(section["single"])}')

    #computed_checksum = multi.get_checksum(data)
    #if computed_checksum == checksum:
    #    lines.append(f'Checksum {checksum:02X}h matches')
    #else:
    #    lines.append(f'Checksum mismatch: original={checksum:02X}, computed={computed_checksum:02X}h')

    return lines

def report_multi_block(data: bytes) -> list[str]:
    lines = []

    multi_chunks = [data[i:i + multi.MULTI_DATA_SIZE] for i in range(0, len(data), multi.MULTI_DATA_SIZE)]
    print(f'multi chunk count = {len(multi_chunks)}')
    multi_number = 1
    for mc in multi_chunks:
        lines.append(f'Multi M{multi_number:02}')
        lines.extend(report_multi(mc))
        lines.append('')
        multi_number += 1

    return lines

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Report information about a Kawai K5000 .KCA file')
    parser.add_argument(dest='filenames', metavar='filename', nargs='*')
    args = parser.parse_args()

    filename = args.filenames[0]

    data = helpers.read_file_data(filename)
    if not multi.check_size(int(len(data) / multi.MULTI_COUNT)):
        print(f'File size does not appear to be valid (was {len(data)} bytes)')
        sys.exit(-1)

    lines = report_multi_block(data)
    for line in lines:
        print(line)

#    multis = []
#    for chunk in multi_chunks:
#        multis.append(multi.MultiPatch.from_data(chunk))

#    for n, m in enumerate(multis):
#        print(f'M{n+1:02} {m.common.name}')
