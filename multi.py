from dataclasses import dataclass
from typing import List, Tuple

MULTI_COUNT = 64  # number of multis in a KCA bank
SECTION_COUNT = 4
MULTI_DATA_SIZE = 103

def check_size(length):
    return length == MULTI_DATA_SIZE

def get_checksum(data):
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
    def from_data(cls, data: bytes):
        return cls(
            sw_type=data[0],
            amount=data[1]
        )

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
    def from_data(cls, data: bytes):
        msb = bin(data[0])[2:].zfill(2) # strip off the '0b' prefix, pad left to two bits
        lsb = bin(data[1])[2:].zfill(7)
        single_number = int(msb + lsb, 2) # convert the combined msb + lsb bit string into a number

        return cls(
            instrument=single_number,
            volume=data[2],
            pan=data[3],
            effect_path=data[4],
            transpose=data[5],
            tune=data[6],
            zone=(data[7], data[8]),
            vel_sw=VelocitySwitching.from_data(data[9:11]),
            receive_channel=data[11]
        )

@dataclass
class Control:
    source: int
    destination: int
    depth: int

    def as_data(self) -> bytes:
        data = bytearray(
            self.source,
            self.destination,
            self.depth
        )
        return bytes(data)

    @classmethod
    def from_data(cls, data: bytes):
        return cls(
            source=data[0],
            destination=data[1],
            depth=data[2]
        )

@dataclass
class Common:
    name: str
    volume: int
    mutes: List[bool]  # 0=mute for sections 1...4
    control1: Control
    control2: Control

    def as_data(self) -> bytes:
        data = bytearray()

        # TODO: get the bytes of the characters in name,
        # pad with spaces from right if less than eight characters

        data.append(self.volume)

        # TODO: Append section mutes

        data.append(self.control1.as_data())
        data.append(self.control2.as_data())

        return bytes(data)

    @classmethod
    def from_data(cls, data: bytes):
        mute_byte = data[9] & 0x0f  # mask off top 4 bits in case there is junk
        mute_bits = bin(mute_byte)[2:].zfill(4)  # strip off the '0b' prefix, pad left with zeros to four bits
        m = []
        for mb in reversed(mute_bits):  # reversed to get natural section order
            m.append(False if mb == '1' else True) # 0=mute, 1=active

        return cls(
            name=data[0:8].decode(encoding='ascii'),
            volume=data[8],
            mutes=m,  # collected from data[9]
            control1=Control.from_data(data[10:13]),
            control2=Control.from_data(data[13:16])
        )

@dataclass
class Reverb:
    reverb_type: int
    dry_wet1: int
    dry_wet2: int
    param2: int
    param3: int
    param4: int

    def as_data(self) -> bytes:
        data = bytearray(
            self.reverb_type,
            self.dry_wet1,
            self.dry_wet2,
            self.param2,
            self.param3,
            self.param4
        )
        return bytes(data)

    @classmethod
    def from_data(cls, data: bytes):
        return cls(
            reverb_type=data[0],
            dry_wet1=data[1],
            dry_wet2=data[2],
            param2=data[3],
            param3=data[4],
            param4=data[5]
        )

@dataclass
class Effect:
    effect_type: int
    dry_wet: int
    param1: int
    param2: int
    param3: int
    param4: int

    def as_data(self) -> bytes:
        data = bytearray(
            self.effect_type,
            self.dry_wet,
            self.param1,
            self.param2,
            self.param3,
            self.param4
        )
        return bytes(data)

    @classmethod
    def from_data(cls, data: bytes):
        return cls(
            effect_type=data[0],
            dry_wet=data[1],
            param1=data[2],
            param2=data[3],
            param3=data[4],
            param4=data[5]
        )

@dataclass
class EffectSettings:
    algorithm: int  # 1...4
    reverb: Reverb
    effect1: Effect
    effect2: Effect
    effect3: Effect
    effect4: Effect
    geq: List[int]  # seven frequency bands, 0...127

    def as_data(self) -> bytes:
        data = bytearray()

        data.append(self.algorithm + 1)

        for b in self.geq:
            data.append(b)

        return bytes(data)

    @classmethod
    def from_data(cls, data: bytes):
        return cls(
            algorithm=data[0],
            reverb=Reverb.from_data(data[1:7]),
            effect1=Effect.from_data(data[7:13]),
            effect2=Effect.from_data(data[13:19]),
            effect3=Effect.from_data(data[19:25]),
            effect4=Effect.from_data(data[25:31]),
            geq=data[31:38]
        )

@dataclass
class MultiPatch:
    checksum: int
    effect: EffectSettings
    common: Common
    sections: List[Section]

    @classmethod
    def from_data(cls, data: bytes):
        e = EffectSettings.from_data(data[:39])
        c = Common.from_data(data[39:55])

        section_data = data[55:]
        section_chunks = [section_data[i:i + 12] for i in range(0, len(section_data), 12)]
        s = []
        for chunk in section_chunks:
            s.append(Section.from_data(chunk))

        return cls(checksum=data[0], effect=e, common=c, sections=s)

    def as_data(self) -> bytes:
        data = bytearray()

        data.append(self.effect.as_data())
        data.append(self.common.as_data())

        return bytes(data)
