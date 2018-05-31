from django.shortcuts import *
from tethys_sdk.gizmos import *
from django.http import JsonResponse, HttpResponseRedirect
from .rch_data_controller import extract_monthly_rch, extract_daily_rch
from .model import write_csv, write_ascii
from .app import swat as app
from .forms import UploadWatershedForm
from .upload_files import save_files
from .config import data_path
import os

def home(request):
    """
    Controller for the Output Viewer page.
    """
    # Get available watersheds (with rch data and wms capabilities) and set select_watershed options

    rch_path = os.path.join(data_path)
    watershed_options = []
    watershed_list = os.listdir(rch_path)
    for f in watershed_list:
        if f.startswith('.'):
            pass
        else:
            name = f.replace('_', ' ').title()
            value = f
            if name not in watershed_options:
                watershed_options.append((name,value))

    # pass the upload watershed form into the view so it can be shown in the web page
    watershedform = UploadWatershedForm()

    # set the initial date picker options
    start = 'January 2005'
    end = 'December 2015'
    format = 'MM yyyy'
    startView = 'decade'
    minView = 'months'

    start_pick = DatePicker(name='start_pick',
                            autoclose=True,
                            format=format,
                            min_view_mode=minView,
                            start_date=start,
                            end_date=end,
                            start_view=startView,
                            today_button=False,
                            initial='Start Date')

    end_pick = DatePicker(name='end_pick',
                          autoclose=True,
                          format=format,
                          min_view_mode=minView,
                          start_date=start,
                          end_date=end,
                          start_view=startView,
                          today_button=False,
                          initial='End Date'
                          )

    param_select = SelectInput(name='param_select',
                               multiple=True,
                               original=False,
                               options=[('Stream Inflow (cms)', 'FLOW_INcms'),
                                        ('Stream Outflow (cms)', 'FLOW_OUTcms'),
                                        ('Evaporation (cms)', 'EVAPcms'),
                                        ('Transpiration Loss (cms)', 'TLOSS'),
                                        ('Organic Nitrogen Inflow (kg)', 'ORGN_INkg'),
                                        ('Organic Nitrogen Outflow (kg)', 'ORGN_OUTkg'),
                                        ('Organic Phosphorus Inflow (kg)', 'ORGP_INkg'),
                                        ('Organic Phosphorus Outflow (kg)', 'ORGP_OUTkg'),
                                        ('Nitrate Inflow (kg)', 'NO3_INkg'),
                                        ('Nitrate Outflow (kg)', 'NO3_OUTkg'),
                                        ('Ammonia Inflow (kg)', 'NH4_INkg'),
                                        ('Ammonia Outflow (kg)', 'NH4_OUTkg'),
                                        ('Nitrogen Dioxide Inflow (kg)', 'NO2_INkg'),
                                        ('Nitrogen Dioxide Outflow (kg)', 'NO2_OUTkg'),
                                        ('Mineral Phosphorus Inflow (kg)', 'MINP_INkg'),
                                        ('Mineral Phosphorus Outflow (kg)', 'MINP_OUTkg'),
                                        ('Chlorophyll-a Inflow (kg)', 'CHLA_INkg'),
                                        ('Chlorophyll-a Outflow (kg)', 'CHLA_OUTkg'),
                                        ('CBOD Inflow (kg)', 'CBOD_INkg'),
                                        ('CBOD Outflow (kg)', 'CBOD_OUTkg'),
                                        ('Dissolved Oxygen Inflow (kg)', 'DISOX_INkg'),
                                        ('Dissolved Oxygen Outflow (kg)', 'DISOX_OUTkg'),
                                        ('Soluble Pesticide Inflow (mg)', 'SOLPST_INmg'),
                                        ('Soluble Pesticide Inflow (mg)', 'SOLPST_OUTmg'),
                                        ('Pesticide Sorbed to Sediment Transport Inflow (mg)','SORPST_INmg'),
                                        ('Pesticide Sorbed to Sediment Transport Outflow (mg)', 'SORPST_OUTmg'),
                                        ('Loss of Pesticide from Water by Reaction (mg)','REACTPSTmg'),
                                        ('Loss of Pesticide from Water by Volatilization (mg)','VOLPSTmg'),
                                        ('Pesticide Transfer from Water to River Bed Sediment (mg)','SETTLPSTmg'),
                                        ('Resuspension of Pesticide from River Bed to Water (mg)','RESUSP_PSTmg'),
                                        ('Diffusion of Pesticide from Water to River Bed Sediment (mg)','DIFFUSEPSTmg'),
                                        ('Loss of Pesticide from River Bed by Reaction (mg)','REACBEDPSTmg'),
                                        ('Loss of Pesticide from River Bed by Buryial (mg)','BURYPSTmg'),
                                        ('Pesticide in River Bed Sediment (mg)','BED_PSTmg'),
                                        ('Persistent Bacterial Outflow (count)','BACTP_OUTct'),
                                        ('Less Persistent Bacterial Outflow (count)','BACTLP_OUT'),
                                        ('Conservative metal #1 Outflow (kg)','CMETAL#1kg'),
                                        ('Conservative Metal #2 Outflow (kg)','CMETAL#2kg'),
                                        ('Conservative Metal #3 Outflow (kg)','CMETAL#3kg'),
                                        ('Total Nitrogen (kg)','TOT Nkg'),
                                        ('Total Phosphourus (kg)','TOT Pkg'),
                                        ('Nitrate Concentration (mg/l)','NO3ConcMg/l'),
                                        ('Water Temperature (deg C)','WTEMPdegc')
                                        ],
                               select2_options={'placeholder': 'Select a Parameter to View',
                                                'allowClear': False},
                               )

    watershed_select = SelectInput(name='watershed_select',
                               multiple=False,
                               original=False,
                               options=watershed_options,
                               select2_options={'placeholder': 'Select a Watershed to View',
                                                'allowClear': False},
                               )

    context = {
        'start_pick': start_pick,
        'end_pick': end_pick,
        'param_select': param_select,
        'watershed_select': watershed_select,
        'watershedform': watershedform
    }

    return render(request, 'swat/home.html', context)


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


    # Create a json object containing all necessary data to create timeseries plot in java script
    # dates = timeseries_dict['Dates']
    # values = timeseries_dict['Values']
    # timestep = timeseries_dict['Timestep']
    # write_csv(streamID, parameters, dates, values, timestep)
    # write_ascii(streamID, parameters, dates, values, timestep)

    # Return the json object back to main.js for timeseries plotting
    json_dict = JsonResponse(timeseries_dict)
    return (json_dict)

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