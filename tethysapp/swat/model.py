# Put your persistent store models in this file
import csv
from .app import swat as app
import os


def write_csv(streamID, parameter, Dates, Values):
    app_workspace = app.get_app_workspace()
    csv_download_path = os.path.join(app_workspace.path, 'download', 'swat_data.csv')

    try:
        os.remove(csv_download_path)
    except OSError:
        pass

    with open(csv_download_path, 'w') as csvfile:
        fieldnames = ['UTC Offset (millisec)', 'Date', parameter]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for i in range(0,len(Dates)):
            writer.writerow({'UTC Offset (millisec)': Values[i][0],
                             'Date': Dates[i],
                             parameter: Values[i][1]})