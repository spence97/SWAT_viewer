from django.http import JsonResponse
from datetime import datetime
import pandas as pd
import os
from .app import swat as app


app_workspace = app.get_app_workspace()
monthly_rch_path = os.path.join(app_workspace.path, 'Output Data', 'output_monthly.rch')
daily_rch_path = os.path.join(app_workspace.path, 'Output Data', 'output_daily_15years.rch')


def extract_monthly_rch(start, end, parameters, reachid):
    param_vals = ['', 'RCH', 'GIS', 'MON', 'AREAkm2', 'FLOW_INcms', 'FLOW_OUTcms',
                  'EVAPcms', 'TLOSScms', 'SED_INtons', 'SED_OUTtons', 'SEDCONCmg/kg',
                  'ORGN_INkg', 'ORGN_OUTkg', 'ORGP_INkg', 'ORGP_OUTkg', 'NO3_INkg',
                  'NO3_OUTkg', 'NH4_INkg', 'NH4_OUTkg', 'NO2_INkg', 'NO2_OUTkg',
                  'MINP_INkg', 'MINP_OUTkg', 'CHLA_INkg', 'CHLA_OUTkg', 'CBOD_INkg',
                  'CBOD_OUTkg', 'DISOX_INkg', 'DISOX_OUTkg', 'SOLPST_INmg', 'SOLPST_OUTmg',
                  'SORPST_INmg', 'SORPST_OUTmg', 'REACTPSTmg', 'VOLPSTmg', 'SETTLPSTmg',
                  'RESUSP_PSTmg', 'DIFFUSEPSTmg', 'REACBEDPSTmg', 'BURYPSTmg', 'BED_PSTmg',
                  'BACTP_OUTct', 'BACTLP_OUTct', 'CMETAL']

    param_names = ['', 'Reach', 'GIS', 'Month', 'Area (km2)', 'Inflow (cms)', 'Outflow (cms)',
                   'Evaporation (cms)', 'Transpiration Loss (cms)', 'Sediment Inflow (tons)', 'Sediment Outflow (tons)',
                   'Sediment Concentration (mg/kg)', 'Organic Nitrogen Inflow (kg)', 'Organic Nitrogen Outflow (kg)',
                   'Organic Phosphorus Inflow (kg)', 'Organic Phosphorus Outflow (kg)', 'Nitrate Inflow (kg)',
                   'Nitrate Outflow (kg)'
                   ]
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
        param_name = param_names[param_index]
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


def extract_daily_rch(start, end, parameters, reachid):
    param_vals = ['', 'RCH', 'GIS', 'MO', 'DA', 'YR', 'AREAkm2', 'FLOW_INcms', 'FLOW_OUTcms',
                  'EVAPcms', 'TLOSScms', 'SED_INtons', 'SED_OUTtons', 'SEDCONCmg/kg',
                  'ORGN_INkg', 'ORGN_OUTkg', 'ORGP_INkg', 'ORGP_OUTkg', 'NO3_INkg',
                  'NO3_OUTkg', 'NH4_INkg', 'NH4_OUTkg', 'NO2_INkg', 'NO2_OUTkg',
                  'MINP_INkg', 'MINP_OUTkg', 'CHLA_INkg', 'CHLA_OUTkg', 'CBOD_INkg',
                  'CBOD_OUTkg', 'DISOX_INkg', 'DISOX_OUTkg', 'SOLPST_INmg', 'SOLPST_OUTmg',
                  'SORPST_INmg', 'SORPST_OUTmg', 'REACTPSTmg', 'VOLPSTmg', 'SETTLPSTmg',
                  'RESUSP_PSTmg', 'DIFFUSEPSTmg', 'REACBEDPSTmg', 'BURYPSTmg', 'BED_PSTmg',
                  'BACTP_OUTct', 'BACTLP_OUTct', 'CMETAL']

    param_names = ['', 'Reach', 'GIS', 'Month', 'Day', 'Year', 'Area (km2)', 'Inflow (cms)', 'Outflow (cms)',
                   'Evaporation (cms)', 'Transpiration Loss (cms)', 'Sediment Inflow (tons)', 'Sediment Outflow (tons)',
                   'Sediment Concentration (mg/kg)', 'Organic Nitrogen Inflow (kg)', 'Organic Nitrogen Outflow (kg)',
                   'Organic Phosphorus Inflow (kg)', 'Organic Phosphorus Outflow (kg)', 'Nitrate Inflow (kg)',
                   'Nitrate Outflow (kg)'
                   ]

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
        param_name = param_names[param_index]

        data = []
        f = open(daily_rch_path)

        header1 = f.readline()
        header2 = f.readline()
        header3 = f.readline()
        header4 = f.readline()
        header5 = f.readline()
        header6 = f.readline()
        header7 = f.readline()
        header8 = f.readline()
        header9 = f.readline()

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

