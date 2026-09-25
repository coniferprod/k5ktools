class Integer:
    min_value = -1000
    max_value = 1000
    default_value = 0

    #def __init__(self, value=0, min_value=-1000, max_value=1000, default_value=0):
    #    if min_value > max_value:
    #        raise ValueError(f"minimum value ({min_value}) must be less than maximum value ({max_value})")
    #    self._min_value = min_value
    #    self._max_value = max_value

    #    if not self._min_value <= default_value <= self._max_value:
    #        raise ValueError(f"default value ({default_value}) must be in range [{self._min_value}, {self._max_value}] ")
    #    self._default_value = default_value

    #    if not self._min_value <= value <= self._max_value:
    #        raise ValueError(f"value must be [{self._min_value}, {self._max_value}], was {value}")
    #    self._value = value

    def __init__(self, value=0):
        minimum = type(self).min_value
        maximum = type(self).max_value
        if not minimum <= value <= maximum:
            raise ValueError(f"value must be {minimum}...{maximum}, was {value}")
        self._value = value

    @property
    def value(self):
        """The value property."""
        return self._value

#    @value.setter
#    def value(self, value):
#        if not self._min_value <= value <= self._max_value:
#            raise ValueError(f"value must be [{self._min_value}, {self._max_value}], was {value}")
#        self._value = value

    def __str__(self):
        return f"{self._value}"

    def __repr__(self):
        minimum = type(self).min_value
        maximum = type(self).max_value
        default = type(self).default_value
        return (
            f"{type(self).__name__}"
            f'(value={self._value}, '
            f'min_value={minimum}, '
            f"max_value={maximum}, "
            f'default_value={default})'
        )

    def random_value(self):
        from random import randint
        return randint(type(self).min_value, type(self).max_value)

    def decode(self, b) -> int:
        return int(b)

    def encode(self) -> int:
        return self.value
