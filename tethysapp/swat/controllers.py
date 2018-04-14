from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from tethys_sdk.gizmos import *
from django.http import JsonResponse
from .rch_data_controller import extract_rch
import plotly
import plotly.graph_objs as go
import pandas as pd


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
                               multiple=False,
                               original=False,
                               options=[('Select Parameter',''),('Stream Inflow (cms)', 'FLOW_INcms'),
                                        ('Stream Outflow (cms)', 'FLOW_OUTcms'),('Evaporation (cms)', 'EVAPcms'),
                                        ('Sediment Inflow (tons)', 'SED_INtons'), ('Sediment Outflow (tons)', 'SED_OUTtons'),
                                        ('Sediment Concentration (mg/kg)', 'SEDCONCmg/kg'), ('Nitrogen Inflow (kg)', 'ORGN_INkg'),
                                        ('Nitrogen Outflow (kg)', 'ORGN_OUTkg'), ('Phosphorus Inflow (kg)', 'ORGP_INkg'),
                                        ('Phosphorus Outflow (kg)', 'ORGP_OUTkg'), ('Dissolved Oxygen Inflow (kg)', 'DISOX_INkg')],
                               initial=['Select Parameter to View']
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


    x = ['Jan 14', 'Feb 14', 'Mar 14', 'Apr 14', 'May 14', 'Jun 14', 'Jul 14', 'Aug 14', 'Sep 14', 'Oct 14', 'Nov 14', 'Dec 14', 'Jan 15', 'Feb 15', 'Mar 15', 'Apr 15', 'May 15', 'Jun 15', 'Jul 15', 'Aug 15', 'Sep 15', 'Oct 15', 'Nov 15']
    y = [0.0, 0.0, 0.0, 0.0, 0.0, 40600.0, 183100.0, 32280.0, 31450.0, 2650.0, 0.3825, 0.0, 0.0, 0.0, 0.0004499, 0.000472, 0.0, 6887.0, 473.5, 56390.0, 86400.0, 163700.0, 7943.0, 0.0]

    data = [go.Scatter(x = x, y = y, name = 'NoData')]
    swat_plot = PlotlyView(data)


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

    get_data = request.POST
    print(get_data)

    start = request.POST.get('startDate')
    end = request.POST.get(str('endDate'))
    parameter = request.POST.get('parameter')
    streamID = request.POST.get('streamID')


    timeseries_dict = extract_rch(start,end,parameter,streamID)
    json_dict = JsonResponse(timeseries_dict)

    return(json_dict)


