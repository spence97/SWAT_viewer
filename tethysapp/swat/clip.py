import os, subprocess, requests
from .config import data_path, temp_workspace, geoserver


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