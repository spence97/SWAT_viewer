from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from tethys_sdk.gizmos import *
from django.http import JsonResponse
from .rch_data_controller import extract_rch
from .model import write_csv
from .app import swat as app
import os

@login_required()
def home(request):
    """
    Controller for the Output Viewer page.
    """


    start_pick = DatePicker(name='start_pick',
                            autoclose=True,
                            format='MM yyyy',
                            min_view_mode='months',
                            start_date='January 2005',
                            end_date='December 2015',
                            start_view='decade',
                            today_button=False,
                            initial='Select Start Date')

    end_pick = DatePicker(name='end_pick',
                          autoclose=True,
                          format='MM yyyy',
                          min_view_mode='months',
                          start_date='January 2005',
                          end_date='December 2015',
                          start_view='decade',
                          today_button=False,
                          initial='Select End Date'
                          )

    param_select = SelectInput(name='param_select',
                               multiple=True,
                               original=False,
                               options=[('Stream Inflow (cms)', 'FLOW_INcms'),
                                        ('Stream Outflow (cms)', 'FLOW_OUTcms'),('Evaporation (cms)', 'EVAPcms'),
                                        ('Sediment Inflow (tons)', 'SED_INtons'), ('Sediment Outflow (tons)', 'SED_OUTtons'),
                                        ('Sediment Concentration (mg/kg)', 'SEDCONCmg/kg'), ('Nitrogen Inflow (kg)', 'ORGN_INkg'),
                                        ('Nitrogen Outflow (kg)', 'ORGN_OUTkg'), ('Phosphorus Inflow (kg)', 'ORGP_INkg'),
                                        ('Phosphorus Outflow (kg)', 'ORGP_OUTkg'), ('Dissolved Oxygen Inflow (kg)', 'DISOX_INkg')],
                               select2_options={'placeholder': 'Select a Parameter to View',
                                                'allowClear': False},
                               )

    app_workspace = app.get_app_workspace()
    csv_download_path = os.path.join(app_workspace.path, 'download', 'swat_data.csv')



    context = {
        'start_pick': start_pick,
        'end_pick': end_pick,
        'param_select': param_select,
        'csv_download_path': csv_download_path
    }

    return render(request, 'swat/home.html', context)


def timeseries(request):
    """
    Controller for the time-series plot.
    """

    start = request.POST.get('startDate')
    end = request.POST.get(str('endDate'))
    parameters = request.POST.getlist('parameters[]')
    streamID = request.POST.get('streamID')


    timeseries_dict = extract_rch(start,end,parameters,streamID)


    dates = timeseries_dict['Dates']
    values = timeseries_dict['Values']

    write_csv(streamID, parameters, dates, values)

    json_dict = JsonResponse(timeseries_dict)
    return (json_dict)