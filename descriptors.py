class ParameterDescriptor:
    def __init__(self, name, min_value, max_value, default_value, incoming, outgoing):
        self.name = name
        self.min_value = min_value
        self.max_value = max_value
        self.default_value = default_value
        self.incoming = incoming
        self.outgoing = outgoing

    def encode(self, value: int) -> int:
        return value + self.incoming

    def decode(self, value: int) -> int:
        return value + self.outgoing

DESCRIPTOR_VALUES = [
    ('volume', 0, 127, 100, 0, 0),
]

DESCRIPTORS = {
    v[0]: ParameterDescriptor(v[0], v[1], v[2], v[3], v[4], v[5]) for v in DESCRIPTOR_VALUES
}