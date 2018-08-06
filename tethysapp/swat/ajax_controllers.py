from django.shortcuts import *
from tethys_sdk.gizmos import *
from django.http import JsonResponse, HttpResponseRedirect
from django.core.files import File
from .model import extract_monthly_rch, extract_daily_rch, clip_raster, get_upstreams, write_csv, write_ascii, save_files, coverage_stats, write_shapefile, nasaaccess_run
from .forms import UploadWatershedForm
from .config import data_path, temp_workspace
from datetime import datetime
import os, json

def get_upstream(request):
    """
    Controller to get list of all upstream reach ids and pass it to front end
    """
    watershed = request.POST.get('watershed')
    streamID = request.POST.get('streamID')
    unique_id = request.POST.get('id')
    print(unique_id)
    unique_path = os.path.join(temp_workspace, unique_id)
    os.makedirs(unique_path, 0777)

    upstreams = get_upstreams(watershed, streamID)

    json_dict = JsonResponse({'watershed': watershed, 'streamID': streamID, 'upstreams': upstreams})
    return json_dict

def save_json(request):
    """
    Controller to clip soil and lulc rasters to upstream boundary and run raster calcs on clipped extents for basin statistics
    """
    upstream_json = json.loads(request.body)
    bbox = upstream_json['bbox']
    srs = 'EPSG:'
    srs += upstream_json['crs']['properties']['name'].split(':')[-1]
    print(bbox)
    print(srs)
    unique_id = upstream_json['uniqueId']
    unique_path = os.path.join(temp_workspace, unique_id)
    with open(unique_path + '/upstream.json', 'w') as outfile:
        json.dump(upstream_json, outfile)

    json_dict = JsonResponse({'id': unique_id, 'bbox': bbox, 'srs': srs})
    return json_dict

def timeseries(request):
    """
    Controller for the time-series plot.
    """
    # Get values passed from the timeseries function in main.js
    watershed = request.POST.get('watershed')
    start = request.POST.get('startDate')
    end = request.POST.get(str('endDate'))
    parameters = request.POST.getlist('parameters[]')
    streamID = request.POST.get('streamID')
    monthOrDay = request.POST.get('monthOrDay')

    # Call the correct rch data parser function based on whether the monthly or daily toggle was selected
    if monthOrDay == 'Monthly':
        timeseries_dict = extract_monthly_rch(watershed, start, end, parameters, streamID)
    else:
        timeseries_dict = extract_daily_rch(watershed, start, end, parameters, streamID)


    # # Call functions to create csv and ascii files for the selected timeseries
    dates = timeseries_dict['Dates']
    values = timeseries_dict['Values']
    timestep = timeseries_dict['Timestep']
    write_csv(watershed, streamID, parameters, dates, values, timestep)
    write_ascii(watershed, streamID, parameters, dates, values, timestep)

    # Return the json object back to main.js for timeseries plotting
    json_dict = JsonResponse(timeseries_dict)
    return (json_dict)

def lulc_compute(request):
    """
    Controller for clipping the lulc file to the upstream catchment boundary and running coverage statistics
    """
    unique_id = request.POST.get('id')
    watershed = request.POST.get('watershed')
    raster_type = 'lulc'
    clip_raster(unique_id, raster_type)
    lulc_dict = coverage_stats(watershed, unique_id, raster_type)
    json_dict = JsonResponse(lulc_dict)
    print(json_dict)
    return(json_dict)


def upload_files(request):

    """
    Controller to upload new temp and .rch data files to app server and publish to geoserver
    """


    if request.method == 'POST':
        form = UploadWatershedForm(request.POST, request.FILES)
        watershed_name = request.POST['watershed_name']
        watershed_name = watershed_name.replace(' ', '_').lower()
        new_dir = os.path.join(data_path, watershed_name)
        if form.is_valid():
            form.save()
            os.makedirs(new_dir)
            save_files(watershed_name)

        return HttpResponseRedirect('../home/')
    else:
        return HttpResponseRedirect('../home/')

def download_csv(request):
    """
    Controller to download csv file
    """

    path_to_file = os.path.join(temp_workspace, 'swat_data.csv')
    f = open(path_to_file, 'r')
    myfile = File(f)

    response = HttpResponse(myfile, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=swat_data.csv'
    return response

def download_ascii(request):
    """
    Controller to download ascii file
    """

    path_to_file = os.path.join(temp_workspace,'swat_data.txt')
    f = open(path_to_file, 'r')
    myfile = File(f)
    response = HttpResponse(myfile, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=swat_data.txt'
    return response

def run_nasaaccess(request):

    """
    Controller to call nasaaccess R functions.
    """
    # Get selected parameters and pass them into nasaccess R scripts
    uniqueId = request.POST.get('uniqueId')
    write_shapefile(uniqueId)
    start = request.POST.get('startDate')
    d_start = str(datetime.strptime(start, '%b %d, %Y').strftime('%Y-%m-%d'))
    end = request.POST.get(str('endDate'))
    d_end = str(datetime.strptime(end, '%b %d, %Y').strftime('%Y-%m-%d'))
    functions = request.POST.getlist('functions[]')

    watershed = request.POST.get('watershed')
    email = request.POST.get('email')
    print(d_start, d_end, functions, watershed, email)
    nasaaccess_run(uniqueId, functions, watershed, d_start, d_end, email)
    return HttpResponseRedirect('../')