import xml.etree.cElementTree as ET

et = ET.parse('/Users/Student/Documents/tethysdev/tethysapp-swat/tethysapp/swat/public/watershed_data/watershed_info.xml')
watershed = ET.SubElement(et.getroot(), 'watershed')

ET.SubElement(watershed, "name").text = "red_river"
ET.SubElement(watershed, "month_start_date").text = 'January 2005'
ET.SubElement(watershed, "month_end_date").text = 'December 2015'
ET.SubElement(watershed, "month_params").text = 'FLOW_INcms, FLOW_OUTcms'
ET.SubElement(watershed, "day_start_date").text = 'January 01, 2011'
ET.SubElement(watershed, "day_end_date").text = 'January 02, 2011'
ET.SubElement(watershed, "day_params").text = 'FLOW_INcms, FLOW_OUTcms'

tree = ET.ElementTree(et.getroot())
tree.write('/Users/Student/Documents/tethysdev/tethysapp-swat/tethysapp/swat/public/watershed_data/watershed_info.xml')