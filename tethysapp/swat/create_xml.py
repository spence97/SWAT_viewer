import xml.etree.cElementTree as ET

watersheds = ET.Element("watersheds")

tree = ET.ElementTree(watersheds)
tree.write('/Users/Student/Documents/tethysdev/swat_data/watershed_info.xml')