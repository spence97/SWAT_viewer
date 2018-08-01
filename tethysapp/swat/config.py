import os

# temp_workspace = os.path.join('/home/ubuntu/tethys_temp/swat/')
#
# data_path = os.path.join('/home/ubuntu/swat_data/')

# temp_workspace = os.path.join('/Users/Student/Documents/tethys_temp_files/swat')
#
# data_path = os.path.join('/Users/Student/Documents/tethysdev/swat_data')

temp_workspace = os.path.join('/home/ubuntu/Documents/tethys_temp/swat')

data_path = os.path.join('/home/ubuntu/Documents/swat_data')

watershed_xml_path = os.path.join('SWAT_viewer/tethysapp/swat/public/watershed_data/watershed_info.xml')

geoserver = {'rest_url':'http://216.218.240.206:8080/geoserver/rest/',
             'wms_url':'http://216.218.240.206:8080/geoserver/wms/',
             'wfs_url':'http://216.218.240.206:8080/geoserver/wfs/',
             'user':'admin',
             'password':'geoserver',
             'workspace':'swat'}
