import csv
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
                row_dict = {fieldnames[0]: values[0][i][0]/1000, fieldnames[1]: datetime.datetime.strptime(dates[i], '%b %y').strftime('%-m/%Y')}
            else:
                row_dict = {fieldnames[0]: values[0][i][0]/1000, fieldnames[1]: datetime.datetime.strptime(dates[i], '%b %d, %Y').strftime('%-m/%d/%Y')}
            for j in range(0,len(parameters)):
                param = parameters[j]
                row_dict[param] = values[j][i][1]
            writer.writerow(row_dict)



write_csv(182, [u'FLOW_INcms', u'ORGP_INkg'], ['Jan 2009', 'Feb 20'], {0: [[1293840000000, 1.663e-05], [1293926400000, 1.663e-05]], 1: [[1293840000000, 0.0004311], [1293926400000, 0.0004311]]}, 'Monthly')