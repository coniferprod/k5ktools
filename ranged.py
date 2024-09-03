class Ranged:
    def __init__(self, value=0, min_value=0, max_value=99, default_value=0):
        if min_value > max_value:
            raise ValueError(f"minimum value ({min_value}) must be less than maximum value ({max_value})")
        self._min_value = min_value
        self._max_value = max_value

        if not self._min_value <= default_value <= self._max_value:
            raise ValueError(f"default value ({default_value}) must be in range [{self._min_value}, {self._max_value}] ")
        self._default_value = default_value

        if not self._min_value <= value <= self._max_value:
            raise ValueError(f"value must be [{self._min_value}, {self._max_value}], was {value}")
        self._value = value

    @property
    def value(self):
        """The value property."""
        return self._value

    @value.setter
    def value(self, value):
        if not self._min_value <= value <= self._max_value:
            raise ValueError(f"value must be [{self._min_value}, {self._max_value}], was {value}")
        self._value = value

    @property
    def min_value(self):
        return self._min_value

    @property
    def max_value(self):
        return self._max_value

    @property
    def default_value(self):
        return self._default_value

    def __str__(self):
        return f"{self._value}"

    def __repr__(self):
        return (
            f"{type(self).__name__}"
            f'(value={self._value}, '
            f'min_value={self._min_value}, '
            f"max_value={self._max_value}, "
            f'default_value={self._default_value})'
        )

    def random_value(self):
        from random import randint
        return randint(self._min_value, self._max_value)
