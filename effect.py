from dataclasses import dataclass
from typing import List, Tuple
from enum import Enum, IntEnum

from datatypes import Level, EffectDepth

class EffectType(IntEnum):
    # Reverb types (0 ... 9)
    HALL1 = 0
    HALL2 = 1
    HALL3 = 2
    ROOM1 = 3
    ROOM2 = 4
    ROOM3 = 5
    PLATE1 = 6
    PLATE2 = 7
    PLATE3 = 8
    REVERSE = 9

    # Other effects (10 ... 47)
    LONG_DELAY = 10
    EARLY_REFLECTION_1 = 11
    EARLY_REFLECTION_2 = 12
    TAP_DELAY_1 = 13
    TAP_DELAY_2 = 14
    SINGLE_DELAY = 15
    DUAL_DELAY = 16
    STEREO_DELAY = 17
    CROSS_DELAY = 18
    AUTO_PAN = 19
    AUTO_PAN_AND_DELAY = 20
    CHORUS_1 = 21
    CHORUS_2 = 22
    CHORUS_1_AND_DELAY = 23
    CHORUS_2_AND_DELAY = 24
    FLANGER_1 = 25
    FLANGER_2 = 26
    FLANGER_1_AND_DELAY = 27
    FLANGER_2_AND_DELAY = 28
    ENSEMBLE = 29
    ENSEMBLE_AND_DELAY = 30
    CELESTE = 31
    CELESTE_AND_DELAY = 32
    TREMOLO = 33
    TREMOLO_AND_DELAY = 34
    PHASER_1 = 35
    PHASER_2 = 36
    PHASER_1_AND_DELAY = 37
    PHASER_2_AND_DELAY = 38
    ROTARY = 39
    AUTO_WAH = 40
    BAND_PASS = 41
    EXCITER = 42
    ENHANCER = 43
    OVERDRIVE = 44
    DISTORTION = 45
    OVERDRIVE_AND_DELAY = 46
    DISTORTION_AND_DELAY = 47

@dataclass
class Effect:
    effect_type: EffectType
    dry_wet: EffectDepth  # for reverb, this is dry_wet1
    param1: Level   # for reverb, this is dry_wet2 (0~100)
    param2: Level
    param3: Level
    param4: Level

    def __bytes__(self) -> bytes:
        data = [
            self.effect_type,
            self.dry_wet,
            self.param1,
            self.param2,
            self.param3,
            self.param4
        ]
        return bytes(data)

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(
            effect_type=EffectType(data[0]),
            dry_wet=data[1],
            param1=data[2],
            param2=data[3],
            param3=data[4],
            param4=data[5]
        )

class EffectAlgorithm(Enum):
    ALGORITHM1 = 0
    ALGORITHM2 = 1
    ALGORITHM3 = 2
    ALGORITHM4 = 3

@dataclass
class EffectSettings:
    algorithm: EffectAlgorithm
    reverb: Effect
    effect1: Effect
    effect2: Effect
    effect3: Effect
    effect4: Effect
    geq: List[int]  # seven frequency bands, 0...127

    def __bytes__(self) -> bytes:
        data = bytearray()

        data.append(self.algorithm + 1)

        data.extend(bytes(self.reverb))
        data.extend(bytes(self.effect1))
        data.extend(bytes(self.effect2))
        data.extend(bytes(self.effect3))
        data.extend(bytes(self.effect4))

        for b in self.geq:
            data.append(b)

        return bytes(data)

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls(
            algorithm=data[0],
            reverb=Effect.from_bytes(data[1:7]),
            effect1=Effect.from_bytes(data[7:13]),
            effect2=Effect.from_bytes(data[13:19]),
            effect3=Effect.from_bytes(data[19:25]),
            effect4=Effect.from_bytes(data[25:31]),
            geq=data[31:38]
        )
