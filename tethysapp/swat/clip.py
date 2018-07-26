import os, json, fiona
from shapely.geometry import shape
from .config import temp_workspace


def write_shp(id):
    json_path = os.path.join(temp_workspace, id)
    print(json_path)
    upstream_json = json.loads(open(json_path + '/upstream.json').read())

    coords = []
    print(len(upstream_json['features']))

    for i in range(0, len(upstream_json['features'])):
        geom = upstream_json['features'][i]['geometry']
        result = shape(geom).buffer(0)
        print(result)
        coordinates = upstream_json['features'][i]['geometry']['coordinates'][0][0]
        coords.append(coordinates)

    new_json = {'type': 'Polygon', 'coordinates': coords}


    schema = {'geometry': 'Polygon', 'properties': {'fld_a': 'str:50'}}
    with fiona.open(json_path + '/upstream.shp', 'w', 'ESRI Shapefile', schema) as layer:
        layer.write({'geometry': new_json, 'properties': {'fld_a': 'test'}})