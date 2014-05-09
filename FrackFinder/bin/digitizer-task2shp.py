#!/usr/bin/env python


import sys
import json
from pprint import pprint
from os.path import isfile
from os.path import basename
try:
    from osgeo import ogr
    from osgeo import osr
except ImportError:
    import ogr
    import osr


def main(args):

    # Output file
    outfile = '/Users/kwurster/Desktop/TEST.shp'
    infile = '/Users/kwurster/Desktop/task_run.json'

    # Crack open input JSON file
    with open(infile) as f:
        task_runs = json.load(f)

    # Delete output file if it exists
    if isfile(outfile):
        driver = ogr.GetDriverByName("ESRI Shapefile")
        driver.DeleteDataSource(outfile)

    # Create the datasource
    driver = ogr.GetDriverByName("ESRI Shapefile")
    datasource = driver.CreateDataSource(outfile)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)

    # Create layers and define fields
    layer_name = basename(outfile).split('.', 1)[1]
    layer = datasource.CreateLayer(layer_name, srs, ogr.wkbPolygon)
    field_definitions = (('selection', 254, ogr.OFTString),
                         ('task_id', 10, ogr.OFTInteger))
    for f_def in field_definitions:
        field_name, field_width, field_type = f_def
        field_object = ogr.FieldDefn(field_name, field_type)
        field_object.SetWidth(field_width)
        layer.CreateField(field_object)

    # Loop through task runs and assemble output shapefile
    for tr in task_runs:
        try:
            selection = str(tr['info']['selection'])
        except KeyError:
            selection = 'ERROR'
        task_id = int(tr['task_id'])
        feature = ogr.Feature(layer.GetLayerDefn())
        feature.SetField('selection', selection)
        feature.SetField('task_id', task_id)

        # Only create a geometry if the task run was digitized/kept its fracking classification
        if selection == 'done':
            coordinates = tr['info']['shape']['coordinates'][0]
            polygon = ogr.Geometry(ogr.wkbPolygon)
            ring = ogr.Geometry(ogr.wkbLinearRing)
            for x_y in coordinates:
                x = x_y[0]
                y = x_y[1]
                ring.AddPoint(x, y)
            ring.CloseRings()
            polygon.AddGeometry(ring)
            feature.SetGeometry(polygon)

        # Create the feature in the layer
        layer.CreateFeature(feature)

        # Cleanup
        feature = None

    # Cleanup
    feature = None
    driver = None
    datasource = None
    srs = None

    # Success
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))