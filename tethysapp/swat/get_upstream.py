from dbfread import DBF
import os
from .config import data_path



def get_upstreams(watershed, streamID):
    dbf_path = os.path.join(data_path, watershed, 'Reach.dbf')
    upstreams = [int(streamID)]
    temp_upstreams = [int(streamID)]
    table = DBF(dbf_path, load=True)

    while len(temp_upstreams)>0:
        reach = temp_upstreams[0]
        for record in table:
            if record['TO_NODE'] == reach:
                temp_upstreams.append(record['Subbasin'])
                upstreams.append(record['Subbasin'])
        temp_upstreams.remove(reach)
    return upstreams