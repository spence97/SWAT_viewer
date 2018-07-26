import fiona, geojson, gdal
from fiona.crs import from_epsg
from shapely.geometry import Polygon
import json


def json_to_shp(upstream_json):
    for feature in upstream_json['features']:
        polygons = Polygon(['geometry'])
        print(polygons)


