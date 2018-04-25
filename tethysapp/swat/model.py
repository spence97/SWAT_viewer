import csv
from .app import swat as app
import os
import datetime


def write_csv(streamID, parameters, dates, values, timestep):
    # app_workspace = app.get_app_workspace()
    # csv_path = os.path.join(app_workspace.path, 'download', 'swat_data.csv')
    csv_path = os.path.join('/Users/Student/tethys/src/tethys_apps/tethysapp/swat/public/data/swat_data.csv')
    try:
        os.remove(csv_path)
    except OSError:
        pass

    fieldnames = ['UTC Offset (millisec)', 'Date']
    fieldnames.extend(parameters)

    with open(csv_path, 'w') as csvfile:
        fieldnames = fieldnames
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for i in range(0, len(dates)):
            if timestep == 'Monthly':
                row_dict = {fieldnames[0]: values[0][i][0], fieldnames[1]: datetime.datetime.strptime(dates[i], '%b %y').strftime('%-m/%Y')}
            else:
                row_dict = {fieldnames[0]: values[0][i][0], fieldnames[1]: datetime.datetime.strptime(dates[i], '%b %d, %y').strftime('%-m/%d/%Y')}
            for j in range(0,len(parameters)):
                param = parameters[j]
                row_dict[param] = values[j][i][1]
            writer.writerow(row_dict)


def write_ascii(streamID, parameters, dates, values):
    # app_workspace = app.get_app_workspace()
    # ascii_path = os.path.join(app_workspace.path, 'download', 'swat_data.txt')
    ascii_path = os.path.join('/Users/Student/tethys/src/tethys_apps/tethysapp/swat/public/data/swat_data.txt')
    f = open(ascii_path, 'w+')

    f.write('StreamID: ' + streamID +'\n')

    param_str = ','.join(str(param) for param in parameters).replace(',', ', ')
    f.write('Parameters: ' + param_str + '\n')

    start = datetime.datetime.strptime(dates[0], '%b %y').strftime('%b %Y')
    end = datetime.datetime.strptime(dates[-1], '%b %y').strftime('%b %Y')
    f.write ('Dates: ' + start + ' - ' + end + '\n')

    f.write('\n')
    f.write('\n')
    f.write('\n')

    head_str = 'UTCoffset(sec)   Date(m/y)'
    for param in parameters:
        head_str += '   ' + param
    head_str_parts = head_str.split()
    f.write(head_str + '\n')

    for i in range(0, len(dates)):
        if timestep == 'Monthly':
            row_str = str(values[0][i][0]/1000).ljust(len(head_str_parts[0])+3,' ') + \
                      str(datetime.datetime.strptime(dates[i], '%b %d %y').strftime('%-m/%Y'))\
                      .ljust(len(head_str_parts[1])+3, ' ')
        else:
            row_str = str(values[0][i][0] / 1000).ljust(len(head_str_parts[0]) + 3, ' ') + \
                      str(datetime.datetime.strptime(dates[i], '%b %y').strftime('%-m/%Y')) \
                      .ljust(len(head_str_parts[1]) + 3, ' ')
        for j in range(0, len(parameters)):
            row_str += str(values[j][i][1]).ljust(len(head_str_parts[j+2])+ 3, ' ')
        f.write(row_str + '\n')




