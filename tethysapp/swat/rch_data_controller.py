from django.http import JsonResponse
from datetime import datetime
import pandas as pd
import os
from .app import swat as app
from .config import data_path, param_names


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

