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

class MultiPatch:
    effect: EffectSettings
    common: Common
    sections: List[Section]

    def checksum(self) -> int:
        return 0

    def as_data(self) -> bytes:
        data = bytearray()

        data.append(self.effect.as_data())
        data.append(self.common.as_data())

        return bytes(data)
