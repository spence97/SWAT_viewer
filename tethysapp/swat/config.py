import os

# temp_workspace = os.path.join('/home/ubuntu/tethys_temp/swat/')
#
# data_path = os.path.join('/home/ubuntu/swat_data/')

# temp_workspace = os.path.join('/Users/Student/Documents/tethys_temp_files/swat')
#
# data_path = os.path.join('/Users/Student/Documents/tethysdev/swat_data')

temp_workspace = os.path.join('/home/ubuntu/Documents/tethys_temp/swat')

data_path = os.path.join('/home/ubuntu/Documents/swat_data')

nasaaccess_path = os.path.join('/home/ubuntu/Documents/nasaaccess_data')

nasaaccess_temp = os.path.join('/home/ubuntu/Documents/tethys_temp/nasaaccess')

watershed_xml_path = os.path.join('SWAT_viewer/tethysapp/swat/public/watershed_data/watershed_info.xml')

geoserver = {'rest_url':'http://216.218.240.206:8080/geoserver/rest/',
             'wms_url':'http://216.218.240.206:8080/geoserver/wms/',
             'wfs_url':'http://216.218.240.206:8080/geoserver/wfs/',
             'user':'admin',
             'password':'geoserver',
             'workspace':'swat'}

param_names = {'':'', 'RCH':'Reach', 'GIS':'GIS',  'MON':'Month', 'DA':'Day', 'YR':'Year', 'AREAkm2':'Area (km2)',
               'FLOW_INcms':'Inflow (cms)', 'FLOW_OUTcms':'Outflow (cms)', 'EVAPcms':'Evaporation (cms)',
               'TLOSScms':'Transpiration Loss (cms)', 'SED_INtons':'Sediment Inflow (tons)', 'SED_OUTtons':'Sediment Outflow (tons)',
               'SEDCONCmg/kg':'Sediment Concentration (mg/kg)', 'ORGN_INkg':'Organic Nitrogen Inflow (kg)',
               'ORGN_OUTkg':'Organic Nitrogen Outflow (kg)', 'ORGP_INkg':'Organic Phosphorus Inflow (kg)',
               'ORGP_OUTkg':'Organic Phosphorus Outflow (kg)', 'NO3_INkg':'Nitrate Inflow (kg)','NO3_OUTkg':'Nitrate Outflow (kg)',
               'NH4_INkg':'Ammonia Inflow (kg)', 'NH4_OUTkg': 'Ammonia Outflow (kg)', 'NO2_INkg': 'Nitrogen Dioxide Inflow (kg)',
               'NO2_OUTkg': 'Nitrogen Dioxide Outflow (kg)', 'MINP_INkg':'Mineral Phosphorus Inflow (kg)',
               'MINP_OUTkg':'Mineral Phosphorus Outflow (kg)', 'CHLA_INkg':'Chlorophyll-a Inflow (kg)', 'CHLA_OUTkg': 'Chlorophyll-a Outflow (kg)',
               'CBOD_INkg':'Carbonaceous BOD Inflow (kg)','CBOD_OUTkg': 'Carbonaceous BOD Outflow (kg)',
               'DISOX_INkg': 'Dissolved Oxygen Inflow (kg)', 'DISOX_OUTkg': 'Dissolved Oxygen Outflow (kg)',
               'SOLPST_INmg': 'Soluble Pesticide Inflow (mg)', 'SOLPST_OUTmg':'Soluble Pesticide Outflow (mg)',
               'SORPST_INmg':'Pesticide Sorbed to Sediment Transport Inflow (mg)',
               'SORPST_OUTmg':'Pesticide Sorbed to Sediment Transport Outflow (mg)', 'REACTPSTmg':'Loss of Pesticide from Water by Reaction (mg)',
               'VOLPSTmg':'Loss of Pesticide from Water by Volatilization (mg)', 'SETTLPSTmg':'Pesticide Transfer from Water to River Bed Sediment (mg)',
               'RESUSP_PSTmg':'Resuspension of Pesticide from River Bed to Water (mg)', 'DIFFUSEPSTmg':'Diffusion of Pesticide from Water to River Bed Sediment (mg)',
               'REACBEDPSTmg':'Loss of Pesticide from River Bed by Reaction (mg)', 'BURYPSTmg':'Loss of Pesticide from River Bed by Burial (mg)',
               'BED_PSTmg':'Pesticide in River Bed Sediment (mg)', 'BACTP_OUTct':'Persistent Bacterial Outflow (count)',
               'BACTLP_OUT':'Less Persistent Bacterial Outflow (count)', 'CMETAL#1kg':'Conservative metal #1 Outflow (kg)',
               'CMETAL#2kg': 'Conservative Metal #2 Outflow (kg)', 'CMETAL#3kg':'Conservative Metal #3 Outflow (kg)', 'TOTNkg':'Total Nitrogen (kg)',
               'TOTPkg':'Total Phosphourus (kg)', 'NO3ConcMg/l':'Nitrate Concentration (mg/l)','WTMPdegc':'Water Temperature (deg C)'
               }

WORKSPACE = 'swat'
GEOSERVER_URI = 'http://www.example.com/swat'