import csv
from .app import swat as app
import os


def write_csv(streamID, parameters, dates, values):
    app_workspace = app.get_app_workspace()
    # csv_download_path = os.path.join(app_workspace.path, 'download', 'swat_data.csv')
    csv_download_path = os.path.join('/Users/Student/tethys/src/tethys_apps/tethysapp/swat/public/data/swat_data.csv')
    try:
        os.remove(csv_download_path)
    except OSError:
        pass

    fieldnames = ['UTC Offset (millisec)', 'Date']
    fieldnames.extend(parameters)

    with open(csv_download_path, 'w') as csvfile:
        fieldnames = fieldnames
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for i in range(0, len(dates)):
            row_dict = {fieldnames[0]: values[0][i][0], fieldnames[1]: dates[i]}
            for j in range(0,len(parameters)):
                param = parameters[j]
                row_dict[param] = values[j][i][1]
            writer.writerow(row_dict)