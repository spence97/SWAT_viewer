from django.db import models
from tethys_sdk.services import get_spatial_dataset_engine
from .config import temp_workspace, data_path, geoserver, param_names, watershed_xml_path, WORKSPACE, GEOSERVER_URI, nasaaccess_path, nasaaccess_temp
from .GLDASpolyCentroid import GLDASpolyCentroid
from .GPMpolyCentroid import GPMpolyCentroid
from .GPMswat import GPMswat
from .GLDASwat import GLDASwat
from dbfread import DBF
from shutil import copyfile
from osgeo import gdal
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import numpy as np
import pandas as pd
import xml.etree.cElementTree as ET
import csv, os, subprocess, requests, smtplib, fiona, json

def extract_monthly_rch(watershed, start, end, parameters, reachid):

    monthly_rch_path = os.path.join(data_path, watershed, 'output_monthly.rch')
    param_vals = ['']
    with open(monthly_rch_path) as f:
        for line in f:
            if 'RCH' in line:
                paramstring = line.strip()
                for i in range(0, len(paramstring)-1):
                    if paramstring[i].islower() and paramstring[i+1].isupper() and paramstring[i] != 'c':
                        paramstring = paramstring[0:i+1] + ' ' + paramstring[i+1:]
                param_vals = param_vals + paramstring.split()
                for i in range(0,len(param_vals)-3):
                    if param_vals[i] == 'TOT':
                        new_val = param_vals[i]+param_vals[i+1]
                        param_vals[i] = new_val
                        param_vals.pop(i+1)
                break



    dt_start = datetime.strptime(start, '%B %Y')
    dt_end = datetime.strptime(end, '%B %Y')

    year_start = dt_start.year
    month_start = dt_start.month
    year_end = dt_end.year
    month_end = dt_end.month

    date_year = [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015]
    start_year_index = date_year.index(year_start)
    end_year_index = date_year.index(year_end)
    start_index = start_year_index * 12 + month_start - 1
    end_index = end_year_index * 12 + month_end - 1

    daterange = pd.date_range(start, end, freq='1M')
    daterange = daterange.union([daterange[-1] + 1])
    daterange_str = [d.strftime('%b %y') for d in daterange]
    daterange_mil = [int(d.strftime('%s')) * 1000 for d in daterange]

    rchDict = {'Dates': daterange_str, 'ReachID': reachid, 'Parameters': parameters, 'Values':{}, 'Names': [], 'Timestep': 'Monthly'}
    for x in range(0,len(parameters)):
        param_index = param_vals.index(parameters[x])
        param_name = param_names[parameters[x]]
        data = []
        f = open(monthly_rch_path)

        header1 = f.readline()
        header2 = f.readline()
        header3 = f.readline()
        header4 = f.readline()
        header5 = f.readline()
        header6 = f.readline()
        header7 = f.readline()
        header8 = f.readline()
        header9 = f.readline()

        for num, line in enumerate(f,1):
            line = line.strip()
            columns = line.split()
            if columns[1] == reachid and 1 <= float(columns[3]) <= 12:
                data.append(float(columns[param_index]))

        f.close()
        ts = []
        data = data[start_index:end_index + 1]
        i = 0
        while i < len(data):
            ts.append([daterange_mil[i],data[i]])
            i += 1


        rchDict['Values'][x] = ts
        rchDict['Names'].append(param_name)

    return rchDict


def extract_daily_rch(watershed, start, end, parameters, reachid):

    daily_rch_path = os.path.join(data_path, watershed, 'output_daily.rch')

    param_vals = ['']
    with open(daily_rch_path) as f:
        for line in f:
            if 'RCH' in line:
                paramstring = line.strip()
                for i in range(0, len(paramstring)-1):
                    if paramstring[i].islower() and paramstring[i+1].isupper() and paramstring[i] != 'c':
                        paramstring = paramstring[0:i+1] + ' ' + paramstring[i+1:]
                param_vals = param_vals + paramstring.split()
                for i in range(0,len(param_vals)-3):
                    if param_vals[i] == 'TOT':
                        new_val = param_vals[i]+param_vals[i+1]
                        param_vals[i] = new_val
                        param_vals.pop(i+1)

                break

    dt_start = datetime.strptime(start, '%B %d, %Y')
    start_index = dt_start.timetuple().tm_yday
    dt_end = datetime.strptime(end, '%B %d, %Y')
    end_index = dt_end.timetuple().tm_yday

    year_start = str(dt_start.year)
    year_start_str = ' ' + year_start + ' '

    daterange = pd.date_range(start, end, freq='1d')
    daterange = daterange.union([daterange[-1]])
    daterange_str = [d.strftime('%b %d, %Y') for d in daterange]
    daterange_mil = [int(d.strftime('%s')) * 1000 for d in daterange]

    rchDict = {'Dates': daterange_str, 'ReachID': reachid, 'Parameters': parameters, 'Values': {}, 'Names': [], 'Timestep': 'Daily'}

    for x in range(0, len(parameters)):

        param_index = param_vals.index(parameters[x])
        param_name = param_names[parameters[x]]

        data = []
        f = open(daily_rch_path)

        for skip_line in f:
            if year_start_str in skip_line:
                break

        for num, line in enumerate(f,1):
            line = line.strip()
            columns = line.split()
            date = datetime.strptime(columns[3] + '/' + columns [4] + '/' + columns[5], '%m/%d/%Y')
            if columns[1] == str(reachid) and dt_start <= date <= dt_end:
                data.append(float(columns[param_index]))
            elif date > dt_end:
                break

        f.close()
        ts = []
        i = 0
        while i < len(data):
            ts.append([daterange_mil[i],data[i]])
            i += 1


        rchDict['Values'][x] = ts
        rchDict['Names'].append(param_name)


    return rchDict


def get_upstreams(watershed, streamID):
    dbf_path = os.path.join(data_path, watershed, 'Reach.dbf')
    upstreams = [int(streamID)]
    temp_upstreams = [int(streamID)]
    table = DBF(dbf_path, load=True)

    while len(temp_upstreams)>0:
        reach = temp_upstreams[0]
        for record in table:
            if record['TO_NODE'] == reach:
                temp_upstreams.append(record['Subbasin'])
                upstreams.append(record['Subbasin'])
        temp_upstreams.remove(reach)
    return upstreams

def write_shapefile(id):
    json_path = os.path.join(temp_workspace, id)

    upstream_json = json.loads(open(json_path + '/upstream.json').read())

    coords = []

    for i in range(0, len(upstream_json['features'])):
        coordinates = upstream_json['features'][i]['geometry']['coordinates'][0][0]
        coords.append(coordinates)

    new_json = {'type': 'Polygon', 'coordinates': coords}

    shapefile_path = os.path.join(temp_workspace, id, 'shapefile')
    os.makedirs(shapefile_path, 0777)

    shapefile_path = shapefile_path + '/upstream.shp'
    print(shapefile_path)

    schema = {'geometry': 'Polygon', 'properties': {'watershed': 'str:50'}}
    with fiona.open(shapefile_path, 'w', 'ESRI Shapefile', schema) as layer:
        layer.write({'geometry': new_json, 'properties': {'watershed': 'Lower Mekong'}})


def coverage_stats(watershed, id, raster_type):
    tif_path = temp_workspace + '/' + str(id) + '/upstream_' + str(raster_type) + '_' + str(id) + '.tif'
    ds = gdal.Open(tif_path)
    band = ds.GetRasterBand(1)
    array = np.array(band.ReadAsArray())
    size = array.size
    print(size)
    unique, counts = np.unique(array, return_counts=True)
    unique_dict = dict(zip(unique, counts))
    print(unique_dict)
    for x in unique_dict:
        if x == 127:
            nodata_size = unique_dict[x]
            size = size - nodata_size
            unique_dict[x] = 0
    print(size)
    color_key_path = os.path.join(data_path, watershed, 'lulc_colors.txt')

    for x in unique_dict:
        if x != 127:
            unique_dict[x] = float(unique_dict[x]) / size * 100
    print(unique_dict)
    if raster_type == 'lulc':
        lulc_dict = {'classes': {},'classValues': {}, 'classColors': {}, 'subclassValues': {}, 'subclassColors': {}}

        for val in unique_dict:
            with open(color_key_path) as f:
                for line in f:
                    splitline = line.split('  ')
                    splitline = [x.strip() for x in splitline]
                    if val != 127 and str(val) in splitline[0]:
                        lulc_dict['subclassColors'][splitline[2]] = splitline[-1]
                        lulc_dict['subclassValues'][splitline[2]] = unique_dict[val]
                        lulc_dict['classes'][splitline[2]] = splitline[1]
                        if splitline[1] not in lulc_dict['classValues'].keys():
                            lulc_dict['classValues'][splitline[1]] = unique_dict[val]
                            lulc_dict['classColors'][splitline[1]] = splitline[-2]
                        else:
                            lulc_dict['classValues'][splitline[1]] += unique_dict[val]


        return(lulc_dict)



def clip_raster(id, raster_type):
    input_json = os.path.join(temp_workspace, id, 'upstream.json')
    input_tif = os.path.join(data_path, 'lower_mekong', raster_type + '.tif')
    output_tif = os.path.join(temp_workspace, id, 'upstream_'+ raster_type + '_' + id + '.tif')

    subprocess.call(
        'gdalwarp --config GDALWARP_IGNORE_BAD_CUTLINE YES -cutline {0} -crop_to_cutline -dstalpha {1} {2}'.format(input_json, input_tif, output_tif),
        shell=True)

    storename = 'upstream_' + raster_type + '_' + id
    headers = {'Content-type': 'image/tiff', }
    user = geoserver['user']
    password = geoserver['password']
    data = open(output_tif, 'rb').read()

    request_url = '{0}workspaces/{1}/coveragestores/{2}/file.geotiff'.format(geoserver['rest_url'],
                                                                             geoserver['workspace'], storename)

    requests.put(request_url, verify=False, headers=headers, data=data, auth=(user, password))



def save_files(id):

    rch_path = os.path.join(data_path, id)
    print(rch_path)
    temp_path = temp_workspace
    print(temp_path)
    temp_files = os.listdir(temp_path)
    print(temp_files)

    for file in temp_files:
        if file.endswith('Store'):
            temp_file_path = os.path.join(temp_path, file)
            os.remove(temp_file_path)
            print('.DS_Store file removed')
        if file.endswith('.rch'):
            print('saving file to app workspace')
            temp_file_path = os.path.join(temp_path, file)
            perm_file_path = os.path.join(rch_path, file)
            copyfile(temp_file_path, perm_file_path)
            os.remove(temp_file_path)
        elif file.endswith('.zip'):
            print('uploading file to geoserver')
            temp_file_path = os.path.join(temp_path, file)
            '''
            Check to see if shapefile is on geoserver. If not, upload it.
            '''
            geoserver_engine = get_spatial_dataset_engine(name='ADPC')
            response = geoserver_engine.get_layer(file, debug=True)
            if response['success'] == False:

                #Create the workspace if it does not already exist
                response = geoserver_engine.list_workspaces()
                if response['success']:
                    workspaces = response['result']
                    if WORKSPACE not in workspaces:
                        geoserver_engine.create_workspace(workspace_id=WORKSPACE, uri=GEOSERVER_URI)

                #Create a string with the path to the zip archive
                zip_archive = temp_file_path

                # Upload shapefile to the workspaces
                if '-reach' in file or '-drainageline' in file or '-stream' in file:
                    store = id + '-reach'
                elif '-subbasin' in file or '-catch' in file or '-boundary' in file:
                    store = id + '-subbasin'
                print(store)
                store_id = WORKSPACE + ':' + store
                print(store_id)
                geoserver_engine.create_shapefile_resource(
                    store_id=store_id,
                    shapefile_zip=zip_archive,
                    overwrite=True
                )
            os.remove(temp_file_path)

    write_xml(id)


def write_csv(watershed, streamID, parameters, dates, values, timestep):
    # param_str = '&'.join(parameters).lower()
    # param_str = ''.join(param_str.split('_'))
    #
    # watershed = ''.join(watershed.split('_'))
    #
    # if timestep == 'Monthly':
    #     start = datetime.datetime.strptime(dates[0], '%b %y').strftime('%m%Y')
    #     end = datetime.datetime.strptime(dates[-1], '%b %y').strftime('%m%Y')
    # else:
    #     start = datetime.datetime.strptime(dates[0], '%b %d, %Y').strftime('%m%d%Y')
    #     end = datetime.datetime.strptime(dates[-1], '%b %d, %Y').strftime('%m%d%Y')
    #
    # file_name = 'SWAT_'+ watershed + '_rch' + streamID + '_' + param_str
    # print(file_name)

    csv_path = os.path.join(temp_workspace, 'swat_data.csv')
    try:
        os.remove(csv_path)
    except OSError:
        pass

    if timestep == 'Monthly':
        fieldnames = ['UTC Offset (sec)', 'Date (m/y)']
    else:
        fieldnames = ['UTC Offset (sec)', 'Date (m/d/y)']
    fieldnames.extend(parameters)

    with open(csv_path, 'w') as csvfile:
        fieldnames = fieldnames
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for i in range(0, len(dates)):
            if timestep == 'Monthly':
                row_dict = {fieldnames[0]: values[0][i][0]/1000, fieldnames[1]: datetime.strptime(dates[i], '%b %y').strftime('%-m/%Y')}
            else:
                row_dict = {fieldnames[0]: values[0][i][0]/1000, fieldnames[1]: datetime.strptime(dates[i], '%b %d, %Y').strftime('%-m/%d/%Y')}
            for j in range(0,len(parameters)):
                param = parameters[j]
                row_dict[param] = values[j][i][1]
            writer.writerow(row_dict)


def write_ascii(watershed, streamID, parameters, dates, values, timestep):
    ascii_path = os.path.join(temp_workspace, 'swat_data.txt')
    f = open(ascii_path, 'w+')

    f.write('Watershed:' + str(watershed) + '\n')
    f.write('StreamID: ' + str(streamID) + '\n')

    param_str = ','.join(str(param) for param in parameters).replace(',', ', ')
    f.write('Parameters: ' + param_str + '\n')

    if timestep == 'Monthly':
        start = datetime.strptime(dates[0], '%b %y').strftime('%b %Y')
        end = datetime.strptime(dates[-1], '%b %y').strftime('%b %Y')
        head_str = 'UTCoffset(sec)   Date(m/y)'
    else:
        start = datetime.strptime(dates[0], '%b %d, %Y').strftime('%m/%d/%Y')
        end = datetime.strptime(dates[-1], '%b %d, %Y').strftime('%m/%d/%Y')
        head_str = 'UTCoffset(sec)   Date(m/d/y)'

    f.write('Dates: ' + start + ' - ' + end + '\n')

    f.write('\n')
    f.write('\n')
    f.write('\n')

    for param in parameters:
        head_str += '   ' + param
    head_str_parts = head_str.split()

    f.write(head_str + '\n')

    for i in range(0, len(dates)):
        if timestep == 'Monthly':
            row_str = str(values[0][i][0] / 1000).ljust(len(head_str_parts[0]) + 3, ' ') + \
                      str(datetime.strptime(dates[i], '%b %y').strftime('%-m/%Y')) \
                          .ljust(len(head_str_parts[1]) + 3, ' ')
        else:
            row_str = str(values[0][i][0] / 1000).ljust(len(head_str_parts[0]) + 3, ' ') + \
                      str(datetime.strptime(dates[i], '%b %d, %Y').strftime('%-m/%-d/%Y')) \
                          .ljust(len(head_str_parts[1]) + 3, ' ')
        for j in range(0, len(parameters)):
            row_str += str(values[j][i][1]).ljust(len(head_str_parts[j + 2]) + 3, ' ')
        f.write(row_str + '\n')


def write_xml(id):
    rch_dir = os.path.join(data_path, id)
    monthly_rch_path = os.path.join(rch_dir, 'output_monthly.rch')
    daily_rch_path = os.path.join(rch_dir, 'output_daily.rch')

    month_param_vals = []
    month_years = []
    year_line_num = []
    first_line_num = ''
    with open(monthly_rch_path) as f:
        for num, line in enumerate(f,1):
            if 'RCH' in line:
                first_line_num = num
                paramstring = line.strip()
                for i in range(0, len(paramstring) - 1):
                    if paramstring[i].islower() and paramstring[i + 1].isupper() and paramstring[i] != 'c':
                        paramstring = paramstring[0:i + 1] + ' ' + paramstring[i + 1:]
                month_param_vals = month_param_vals + paramstring.split()
                for i in range(0, len(month_param_vals) - 3):
                    if month_param_vals[i] == 'TOT':
                        new_val = month_param_vals[i] + month_param_vals[i + 1]
                        month_param_vals[i] = new_val
                        month_param_vals.pop(i + 1)
            elif 'REACH' in line:
                line = line.strip()
                columns = line.split()
                if float(columns[3]) > 12 and columns[3] not in month_years:
                    year_line_num.append(num)
                    month_years.append(columns[3])


    f = open(monthly_rch_path)
    lines=f.readlines()
    month_start_month = lines[int(first_line_num)].strip().split()[3]
    month_start_date = datetime.date(int(month_years[0]), int(month_start_month), 1).strftime('%B %Y')

    month_end_month = lines[int(year_line_num[-1])-2].strip().split()[3]
    month_end_date = datetime.date(int(month_years[-1]), int(month_end_month), 1).strftime('%B %Y')


    del month_param_vals[month_param_vals.index('RCH')]
    del month_param_vals[month_param_vals.index('GIS')]
    del month_param_vals[month_param_vals.index('MON')]
    del month_param_vals[month_param_vals.index('AREAkm2')]

    month_params = ', '.join(x for x in month_param_vals)


    day_param_vals = ['']
    first_line_num = ''
    with open(daily_rch_path) as f:
        for num, line in enumerate(f,1):
            if 'RCH' in line:
                first_line_num = num
                paramstring = line.strip()
                for i in range(0, len(paramstring) - 1):
                    if paramstring[i].islower() and paramstring[i + 1].isupper() and paramstring[i] != 'c':
                        paramstring = paramstring[0:i + 1] + ' ' + paramstring[i + 1:]
                day_param_vals = day_param_vals + paramstring.split()
                for i in range(0, len(day_param_vals) - 3):
                    if day_param_vals[i] == 'TOT':
                        new_val = day_param_vals[i] + day_param_vals[i + 1]
                        day_param_vals[i] = new_val
                        day_param_vals.pop(i + 1)
                break

    f = open(daily_rch_path)
    lines=f.readlines()
    day_start_month = lines[int(first_line_num)].strip().split()[3]
    day_start_day = lines[int(first_line_num)].strip().split()[4]
    day_start_year = lines[int(first_line_num)].strip().split()[5]

    day_start_date = datetime.date(int(day_start_year), int(day_start_month), int(day_start_day)).strftime('%B %d, %Y')

    day_end_month = lines[-1].strip().split()[3]
    day_end_day = lines[-1].strip().split()[4]
    day_end_year = lines[-1].strip().split()[5]

    day_end_date = datetime.date(int(day_end_year), int(day_end_month), int(day_end_day)).strftime('%B %d, %Y')


    del day_param_vals[day_param_vals.index('')]
    del day_param_vals[day_param_vals.index('RCH')]
    del day_param_vals[day_param_vals.index('GIS')]
    del day_param_vals[day_param_vals.index('MO')]
    del day_param_vals[day_param_vals.index('DA')]
    del day_param_vals[day_param_vals.index('YR')]
    del day_param_vals[day_param_vals.index('AREAkm2')]

    day_params = ', '.join(x for x in day_param_vals)


    et = ET.parse(watershed_xml_path)
    watershed = ET.SubElement(et.getroot(), 'watershed')

    ET.SubElement(watershed, "name").text = id
    ET.SubElement(watershed, "month_start_date").text = month_start_date
    ET.SubElement(watershed, "month_end_date").text = month_end_date
    ET.SubElement(watershed, "month_params").text = month_params
    ET.SubElement(watershed, "day_start_date").text = day_start_date
    ET.SubElement(watershed, "day_end_date").text = day_end_date
    ET.SubElement(watershed, "day_params").text = day_params

    tree = ET.ElementTree(et.getroot())
    tree.write(watershed_xml_path)


def nasaaccess_run(id, functions, watershed, start, end, email):
    shp_path = os.path.join(temp_workspace, id, 'upstream.shp')
    dem_path = os.path.join(data_path, watershed, 'dem.tif')
    unique_path = os.path.join(nasaaccess_path, 'outputs', id, 'nasaaccess_data')
    os.makedirs(unique_path, 0777)
    tempdir = os.path.join(nasaaccess_temp, id)
    os.makedirs(tempdir, 0777)
    cwd = os.getcwd()
    print(cwd)

    os.chdir(tempdir)

    for func in functions:
        if func == 'GPMpolyCentroid':
            output_path = unique_path + '/GPMpolyCentroid/'
            os.makedirs(output_path, 0777)
            print('running GPMpoly')
            GPMpolyCentroid(output_path, shp_path, dem_path, start, end)
        elif func == 'GPMswat':
            output_path = unique_path + '/GPMswat/'
            os.makedirs(output_path, 0777)
            print('running GPMswat')
            GPMswat(output_path, shp_path, dem_path, start, end)
        elif func == 'GLDASpolyCentroid':
            output_path = unique_path + '/GLDASpolyCentroid/'
            os.makedirs(output_path, 0777)
            print('running GLDASpoly')
            GLDASpolyCentroid(tempdir, output_path, shp_path, dem_path, start, end)
        elif func == 'GLDASwat':
            output_path = unique_path + '/GLDASwat/'
            os.makedirs(output_path, 0777)
            print('running GLDASwat')
            GLDASwat(output_path, shp_path, dem_path, start, end)

    from_email = 'nasaaccess@gmail.com'
    to_email = email

    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Your nasaaccess data is ready'

    msg['From'] = from_email
    msg['To'] = to_email

    message = """\
        <html>
            <head></head>
            <body>
                <p>Hello,<br>
                   Your nasaaccess data is ready for download at <a href="http://tethys-servir-mekong.adpc.net/apps/nasaaccess">http://tethys-servir-mekong.adpc.net/apps/nasaaccess</a><br>
                   Your unique access code is: <strong>""" + unique_id + """</strong><br>
                </p>
            </body>
        <html>
    """

    part1 = MIMEText(message, 'html')
    msg.attach(part1)

    gmail_user = 'nasaaccess@gmail.com'
    gmail_pwd = 'nasaaccess123'
    smtpserver = smtplib.SMTP('smtp.gmail.com', 587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo()
    smtpserver.login(gmail_user, gmail_pwd)
    smtpserver.sendmail(gmail_user, to_email, msg.as_string())
    smtpserver.close()




class new_watershed(models.Model):
    watershed_name = models.CharField(max_length=50)
    streams_shapefile = models.FileField(upload_to='swat/')
    basins_shapefile = models.FileField(upload_to='swat/')
    monthly_rch_file = models.FileField(upload_to='swat/')
    daily_rch_file = models.FileField(upload_to='swat/')

