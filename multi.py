from dataclasses import dataclass
from typing import List, Tuple

from effect import EffectSettings


MULTI_COUNT = 64  # number of multis in a KCA bank
SECTION_COUNT = 4
MULTI_DATA_SIZE = 103

def check_size(length: int) -> bool:
    return length == MULTI_DATA_SIZE

def get_checksum(data: bytes) -> int:
    # The multi checksum is [(common data sum) + (section data sum) + 0xa5] & 0x7f
    common_data = data[:54]
    common_sum = 0
    for cd in common_data:
        common_sum += cd

    section_data = data[54:]
    section_sum = 0
    for sd in section_data:
        section_sum += sd

    return (common_sum + section_sum + 0xA5) & 0x7F

@dataclass
class VelocitySwitching:
    sw_type: int # 0=off, 1=loud, 2=soft
    amount: int # 1...127

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(
            sw_type=data[0],
            amount=data[1])

    def __bytes__(self) -> bytes:
        data = bytearray()
        data.append(self.sw_type)
        data.append(self.amount)
        return bytes(data)

@dataclass
class Section:
    instrument: int
    volume: int
    pan: int
    effect_path: int
    transpose: int
    tune: int
    zone: Tuple[int, int]  # low and high
    vel_sw: VelocitySwitching
    receive_channel: int

    @classmethod
    def from_bytes(cls, data: bytes):
        msb = bin(data[0])[2:].zfill(2) # strip off the '0b' prefix, pad left to two bits
        lsb = bin(data[1])[2:].zfill(7)
        single_number = int(msb + lsb, 2) # convert the combined msb + lsb bit string into a number

        return cls(
            instrument=single_number,
            volume=data[2],
            pan=data[3],
            effect_path=data[4],
            transpose=data[5] - 64,  # from 40~88 to -24~+24
            tune=data[6] - 64,  # from 1~127 to -63~+63
            zone=(data[7], data[8]),
            vel_sw=VelocitySwitching.from_data(data[9:11]),
            receive_channel=data[11] - 1  # from 0~15 to 1~16
        )

    def __bytes__(self) -> bytes:
        data = bytearray()

        # Make a bit string of the instrument number
        inst_bits = bin(self.instrument).zfill(9)  # should have nine bits now

        # Top two bits are MSB
        msb = inst_bits[:2]
        data.append(int(msb, 2))

        # Bottom seven bits are LSB
        lsb = inst_bits[2:]
        data.append(int(lsb, 2))

        data.append(self.volume)
        data.append(self.pan)
        data.append(self.effect_path)
        data.append(self.transpose + 64)
        data.append(self.tune + 64)
        data.append(self.zone[0])
        data.append(self.zone[1])

        data.extend(self.vel_sw.as_data())
        data.append(self.receive_channel - 1)

        return bytes(data)

@dataclass
class Control:
    source: int
    destination: int
    depth: int

    def __bytes__(self) -> bytes:
        data = bytearray([
            self.source,
            self.destination,
            self.depth])
        return bytes(data)

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(
            source=data[0],
            destination=data[1],
            depth=data[2])

@dataclass
class Common:
    effect_settings: EffectSettings
    name: str
    volume: int
    mutes: List[bool]  # 0=mute for sections 1...4
    control1: Control
    control2: Control

    def __bytes__(self) -> bytes:
        data = bytearray()

        data.extend(bytes(self.effect_settings))

        # Pad with spaces from right if less than eight characters
        data.append(self.name.ljust(8).encode('ascii'))

        data.append(self.volume)

        # Generate a string of bit values to represent the mutes
        mute_bits = ['0' if m else '1' for m in reversed(self.mutes)]
        # Convert bit string to byte and append to result
        data.extend(int(mute_bits, 2))

        data.extend(self.control1.as_data())
        data.extend(self.control2.as_data())

        return bytes(data)

    @classmethod
    def from_bytes(cls, data: bytes):
        mute_byte = data[47] & 0x0f  # mask off top 4 bits in case there is junk
        mute_bits = bin(mute_byte)[2:].zfill(4)  # strip off the '0b' prefix, pad left with zeros to four bits

        # 0=mute, 1=active
        m = [False if mb == '1' else True for mb in reversed(mute_bits)] # reversed to get natural section order

        return cls(
            effect_settings=EffectSettings.from_data(data[:38]),
            name=data[38:46].decode(encoding='ascii'),
            volume=data[46],
            mutes=m,  # collected from data[9]
            control1=Control.from_data(data[48:51]),
            control2=Control.from_data(data[51:54]))

@dataclass
class MultiPatch:
    checksum: int
    common: Common
    sections: List[Section]

    @classmethod
    def from_bytes(cls, data: bytes):
        c = Common.from_data(data[:55])

        section_data = data[55:]
        section_chunks = [section_data[i:i + 12] for i in range(0, len(section_data), 12)]
        s = []
        for chunk in section_chunks:
            s.append(Section.from_data(chunk))

        return cls(checksum=data[0], common=c, sections=s)

    def __bytes__(self) -> bytes:
        data = bytearray()

        data.extend(bytes(self.common))

        for s in self.sections:
            data.extend(s.as_data())

        checksum = get_checksum(data)
        data.insert(0, checksum)  # insert checksum in front

        return bytes(data)
