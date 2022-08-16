# Identify and report on Kawai K5000 patch files
# (native or System Exclusive)

import sys
import os

import bank
import helpers
import multi


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
        #lines.append(f'Kind: {kind}')
        if kind == 'combi/multi':
            number = data[7] + 1
            lines.append(f'Contains {kind} patch M{number:02}')
            lines.extend(report_multi(data[8:-1]))
        elif kind == 'single':
            tone_num = data[8] + 1
            lines.append(f'Contains {kind} patch {location}{tone_num}')
    else:
        lines.append('Unable to determine patch information')

    return lines

def report_multi(data):
    lines = []

    #checksum = data[0]
    mute_byte = data[48] & 0x0f  # mask off top 4 bits in case there is junk
    mute_bits = bin(mute_byte)[2:].zfill(4)  # strip off the '0b' prefix, pad left with zeros to four bits
    #print(f'mute_bits = {mute_bits}')

    sections = []
    for i in range(0, 4):
        sections.append({'number': i + 1})

    section_num = 1
    for mb in reversed(mute_bits):  # reversed to get natural section order
        sections[section_num - 1]['mute'] = False if mb == '1' else True # 0=mute, 1=active
        section_num += 1

    section_data = data[55:]
    #print(section_data)
    #print(len(section_data))

    section_chunks = [section_data[i:i + 12] for i in range(0, len(section_data), 12)]
    #print(section_chunks)
    #for chunk in section_chunks:
    #    print(helpers.hexdump(chunk))
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

    lines.append(f'File size: {len(data)} bytes')

    source_line = ''
    if extension == 'kaa':
        lines.append('Use kaanalyz.py to get more information about this bank')
    elif extension == 'ka1':
        if bank.check_single_size(len(data)):
            counts = bank.SINGLE_INFO[len(data)]
            source_line = f'{counts[0]} PCM, {counts[1]} ADD sources'
        else:
            source_line = 'Does not match any valid KA1 file'
        lines.append(source_line)
    elif extension == 'kc1':
        if multi.check_size(len(data)):
            lines.extend(report_multi(data))
        else:
            source_line = "Does not look like a valid combi/multi KC1 file"
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
