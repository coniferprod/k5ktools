import sys
from xml.etree import ElementTree as ET
from xml.dom import minidom

def prettify(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

schema_namespace_prefix = "xs"
schema_namespace = "http://www.w3.org/2001/XMLSchema"
ET.register_namespace(schema_namespace_prefix, schema_namespace)
root = ET.Element("schema", attrib={f"xmlns:{schema_namespace_prefix}": schema_namespace})

class TypeDescriptor:
    def __init__(self, name: str, min_value: int, max_value: int):
        self.name = name
        self.min_value = min_value
        self.max_value = max_value

    def to_xml(self, parent: ET.Element) -> ET.Element:
        base = 'integer'

        # If the minimum value is non-negative, we can use the nonNegativeInteger type
        if self.min_value >= 0:
            base = 'nonNegativeInteger'
        
        element = ET.SubElement(parent, f"element", attrib={
            "name": self.name,
        })

        restriction = ET.SubElement(element, 'restriction', attrib={"base": base})

        min_inclusive = ET.SubElement(restriction, 'minInclusive', attrib={"value": str(self.min_value)})
        max_inclusive = ET.SubElement(restriction, 'maxInclusive', attrib={"value": str(self.max_value)})

        return element

td = TypeDescriptor("volume", 0, 127)
ET.ElementTree(root).write(sys.stdout.buffer)
