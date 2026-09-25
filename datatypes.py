from integer import Integer

class MIDIChannel(Integer):
    minimum_value = 1
    maximum_value = 16
    default_value = 1

    def __init__(self, value):
        super().__init__(value)

    def decode(self, b) -> int:
        return b + 1

    def encode(self) -> int:
        return self.value - 1


class Level(Integer):
    minimum_value = 0
    maximum_value = 127
    default_value = 0

    def __init__(self, value):
        super().__init__(value)


class EffectDepth(Integer):
    minimum_value = 0
    maximum_value = 100
    default_value = 0

    def __init__(self, value):
        super().__init__(value)
