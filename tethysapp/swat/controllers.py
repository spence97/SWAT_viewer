from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from tethys_sdk.gizmos import *
from django.http import JsonResponse
from .rch_data_controller import extract_rch
from .model import write_csv

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

    # view_options = MVView(
    #     projection='EPSG:3857',
    #     center=[11569508.601244, 1952336.603654],
    #     zoom=6,
    #     maxZoom=15,
    #     minZoom=2,
    # )

    # mekong_streams = MVLayer(
    #     source='ImageWMS',
    #     options={'url': 'http://localhost:8080/geoserver/wms',
    #              'params': {'LAYERS': 'swat_mekong:reach'}},
    #     legend_title='streams',
    #     legend_extent=[-173, 17, -65, 72],
    #     feature_selection=True,
    #     geometry_attribute='the_geom'
    # )
    #
    # mekong_subbasins = MVLayer(
    #     source='ImageWMS',
    #     options={'url': 'http://localhost:8080/geoserver/wms',
    #              'params': {'LAYERS': 'swat_mekong:subbasin'}},
    #     legend_title='subbasins',
    #     legend_extent=[-173, 17, -65, 72],
    #     feature_selection=False,
    #     geometry_attribute='the_geom'
    # )

    # mekong_monpoints = MVLayer(
    #     source='ImageWMS',
    #     options={'url': 'http://localhost:8080/geoserver/wms',
    #              'params': {'LAYERS': 'swat_mekong:monitoringpoint'}},
    #     legend_title='monitoring points',
    #     legend_extent=[-173, 17, -65, 72],
    #     feature_selection=False,
    #     geometry_attribute='the_geom'
    # )

    # map = MapView(
    #     height='600px',
    #     width='100%',
    #     controls=['ZoomSlider','Rotate','FullScreen'],
    #     layers=[mekong_streams,mekong_subbasins],
    #     view=view_options,
    #     basemap={'Bing': {
    #         'key': '5TC0yID7CYaqv3nVQLKe~xWVt4aXWMJq2Ed72cO4xsA~ApdeyQwHyH_btMjQS1NJ7OHKY8BK-W-EMQMrIavoQUMYXeZIQOUURnKGBOC7UCt4',
    #         'imagerySet': 'Aerial'}},
    #     legend=True
    # )



    context = {
        'start_pick': start_pick,
        'end_pick': end_pick,
        'param_select': param_select
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

    print(parameters)

    timeseries_dict = extract_rch(start,end,parameters,streamID)


    dates = timeseries_dict['Dates']
    values = timeseries_dict['Values']

    write_csv(streamID, parameters, dates, values)

    json_dict = JsonResponse(timeseries_dict)
    return (json_dict)