from ranged import Ranged

class MIDIChannel(Ranged):
    def __init__(self, value=1):
        super().__init__(value, min_value=1, max_value=16, default_value=1)

class Level(Ranged):
    def __init__(self, value=0):
        super().__init__(value, min_value=0, max_value=127, default_value=0)

class EffectDepth(Ranged):
    def __init__(self, value=0):
        super().__init__(value, min_value=0, max_value=100, default_value=0)
