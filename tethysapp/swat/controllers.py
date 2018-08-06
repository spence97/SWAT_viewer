from django.shortcuts import *
from tethys_sdk.gizmos import *
from .forms import UploadWatershedForm
from .config import data_path
from datetime import datetime
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
        elif f.endswith('.xml'):
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

    na_start = 'Jan 01, 2000'
    na_end = datetime.now().strftime("%b %d, %Y")
    na_format = 'M d, yyyy'
    na_startView = 'decade'
    na_minView = 'days'

    watershed_select = SelectInput(name='watershed_select',
                                   multiple=False,
                                   original=False,
                                   options=watershed_options,
                                   initial=[('Lower Mekong', 'lower_mekong')],
                                   # select2_options={'placeholder': 'Select a Watershed to View',
                                   #                  'allowClear': False},
                                   )

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

    na_start_pick = DatePicker(name='na_start_pick',
                            autoclose=True,
                            format=na_format,
                            min_view_mode=na_minView,
                            start_date=na_start,
                            end_date=na_end,
                            start_view=na_startView,
                            today_button=False,
                            initial='Start Date')

    na_end_pick = DatePicker(name='na_end_pick',
                          autoclose=True,
                          format=na_format,
                          min_view_mode=na_minView,
                          start_date=na_start,
                          end_date=na_end,
                          start_view=na_startView,
                          today_button=False,
                          initial='End Date'
                          )

    param_select = SelectInput(name='param_select',
                               multiple=True,
                               original=False,
                               options=[('Stream Inflow (cms)', 'FLOW_INcms'),
                                        ('Stream Outflow (cms)', 'FLOW_OUTcms'),
                                        ('Evaporation (cms)', 'EVAPcms'),
                                        ('Transpiration Loss (cms)', 'TLOSScms'),
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
                                        ('Loss of Pesticide from River Bed by Burial (mg)','BURYPSTmg'),
                                        ('Pesticide in River Bed Sediment (mg)','BED_PSTmg'),
                                        ('Persistent Bacterial Outflow (count)','BACTP_OUTct'),
                                        ('Less Persistent Bacterial Outflow (count)','BACTLP_OUT'),
                                        ('Conservative metal #1 Outflow (kg)','CMETAL#1kg'),
                                        ('Conservative Metal #2 Outflow (kg)','CMETAL#2kg'),
                                        ('Conservative Metal #3 Outflow (kg)','CMETAL#3kg'),
                                        ('Total Nitrogen (kg)','TOTNkg'),
                                        ('Total Phosphourus (kg)','TOTPkg'),
                                        ('Nitrate Concentration (mg/l)','NO3ConcMg/l'),
                                        ('Water Temperature (deg C)','WTMPdegc')
                                        ],
                               select2_options={'placeholder': 'Select a Parameter to View',
                                                'allowClear': False},
                               )



    context = {
        'start_pick': start_pick,
        'end_pick': end_pick,
        'na_start_pick': na_start_pick,
        'na_end_pick': na_end_pick,
        'param_select': param_select,
        'watershed_select': watershed_select,
        'watershedform': watershedform
    }

    return render(request, 'swat/home.html', context)


def add_watershed(request):
    """
    Controller for the Add Watershed page.
    """

    # pass the upload watershed form into the view so it can be shown in the web page
    watershedform = UploadWatershedForm()



    context = {
        'watershedform': watershedform
    }

    return render(request, 'swat/add_watershed.html', context)






