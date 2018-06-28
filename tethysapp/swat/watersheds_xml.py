import xml.etree.cElementTree as ET
import os
import datetime
from .config import data_path

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


    et = ET.parse(data_path + '/watershed_info.xml')
    watershed = ET.SubElement(et.getroot(), id)

    ET.SubElement(watershed, "month_start_date").text = month_start_date
    ET.SubElement(watershed, "month_end_date").text = month_end_date
    ET.SubElement(watershed, "month_params").text = month_params
    ET.SubElement(watershed, "day_start_date").text = day_start_date
    ET.SubElement(watershed, "day_end_date").text = day_end_date
    ET.SubElement(watershed, "day_params").text = day_params

    tree = ET.ElementTree(et.getroot())
    tree.write(data_path + '/watershed_info.xml')






