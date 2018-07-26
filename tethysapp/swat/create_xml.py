import xml.etree.cElementTree as ET
from .config import watershed_xml_path

watersheds = ET.Element("watersheds")

tree = ET.ElementTree(watersheds)
tree.write(watershed_xml_path)