from django.db import models
import csv
import os
import datetime
from .config import temp_workspace



def write_csv(watershed, streamID, parameters, dates, values, timestep):
    # param_str = '&'.join(parameters).lower()
    # param_str = ''.join(param_str.split('_'))
    #
    # watershed = ''.join(watershed.split('_'))
    #
    # if timestep == 'Monthly':
    #     start = datetime.datetime.strptime(dates[0], '%b %y').strftime('%m%Y')
    #     end = datetime.datetime.strptime(dates[-1], '%b %y').strftime('%m%Y')
    # else:
    #     start = datetime.datetime.strptime(dates[0], '%b %d, %Y').strftime('%m%d%Y')
    #     end = datetime.datetime.strptime(dates[-1], '%b %d, %Y').strftime('%m%d%Y')
    #
    # file_name = 'SWAT_'+ watershed + '_rch' + streamID + '_' + param_str
    # print(file_name)

    csv_path = os.path.join(temp_workspace, 'swat_data.csv')
    try:
        os.remove(csv_path)
    except OSError:
        pass

    if timestep == 'Monthly':
        fieldnames = ['UTC Offset (sec)', 'Date (m/y)']
    else:
        fieldnames = ['UTC Offset (sec)', 'Date (m/d/y)']
    fieldnames.extend(parameters)

    with open(csv_path, 'w') as csvfile:
        fieldnames = fieldnames
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for i in range(0, len(dates)):
            if timestep == 'Monthly':
                row_dict = {fieldnames[0]: values[0][i][0]/1000, fieldnames[1]: datetime.datetime.strptime(dates[i], '%b %y').strftime('%-m/%Y')}
            else:
                row_dict = {fieldnames[0]: values[0][i][0]/1000, fieldnames[1]: datetime.datetime.strptime(dates[i], '%b %d, %Y').strftime('%-m/%d/%Y')}
            for j in range(0,len(parameters)):
                param = parameters[j]
                row_dict[param] = values[j][i][1]
            writer.writerow(row_dict)


def write_ascii(watershed, streamID, parameters, dates, values, timestep):
    ascii_path = os.path.join(temp_workspace, 'swat_data.txt')
    f = open(ascii_path, 'w+')

    f.write('Watershed:' + str(watershed) + '\n')
    f.write('StreamID: ' + str(streamID) + '\n')

    param_str = ','.join(str(param) for param in parameters).replace(',', ', ')
    f.write('Parameters: ' + param_str + '\n')

    if timestep == 'Monthly':
        start = datetime.datetime.strptime(dates[0], '%b %y').strftime('%b %Y')
        end = datetime.datetime.strptime(dates[-1], '%b %y').strftime('%b %Y')
        head_str = 'UTCoffset(sec)   Date(m/y)'
    else:
        start = datetime.datetime.strptime(dates[0], '%b %d, %Y').strftime('%m/%d/%Y')
        end = datetime.datetime.strptime(dates[-1], '%b %d, %Y').strftime('%m/%d/%Y')
        head_str = 'UTCoffset(sec)   Date(m/d/y)'

    f.write('Dates: ' + start + ' - ' + end + '\n')

    f.write('\n')
    f.write('\n')
    f.write('\n')

    for param in parameters:
        head_str += '   ' + param
    head_str_parts = head_str.split()

    f.write(head_str + '\n')

    for i in range(0, len(dates)):
        if timestep == 'Monthly':
            row_str = str(values[0][i][0] / 1000).ljust(len(head_str_parts[0]) + 3, ' ') + \
                      str(datetime.datetime.strptime(dates[i], '%b %y').strftime('%-m/%Y')) \
                          .ljust(len(head_str_parts[1]) + 3, ' ')
        else:
            row_str = str(values[0][i][0] / 1000).ljust(len(head_str_parts[0]) + 3, ' ') + \
                      str(datetime.datetime.strptime(dates[i], '%b %d, %Y').strftime('%-m/%-d/%Y')) \
                          .ljust(len(head_str_parts[1]) + 3, ' ')
        for j in range(0, len(parameters)):
            row_str += str(values[j][i][1]).ljust(len(head_str_parts[j + 2]) + 3, ' ')
        f.write(row_str + '\n')

class new_watershed(models.Model):
    watershed_name = models.CharField(max_length=50)
    streams_shapefile = models.FileField(upload_to='swat/')
    basins_shapefile = models.FileField(upload_to='swat/')
    monthly_rch_file = models.FileField(upload_to='swat/')
    daily_rch_file = models.FileField(upload_to='swat/')

