from xml.etree.ElementTree import (Element, SubElement)

def single_to_xml(data: bytes) -> Element:
    offset = 0

    root = Element('single')


    common = SubElement(root, 'common')

    effect_algorithm = data[offset] + 1  # adjust 0...3 to 1...4
    


    return root

