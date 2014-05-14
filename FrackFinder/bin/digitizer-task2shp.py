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


__docname__ = basename(__file__)
ogr.UseExceptions()


def print_usage():
    print("")
    print('Usage %s: task_run.json outfile.shp' % __docname__)
    print("")
    return 1


def main(args):

    # Output file
    infile = args[0]
    outfile = args[1]

    # Validate input
    if not isfile(infile):
        print("ERROR: Can't find infile: %s" % infile)
        return 1

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
    layer = datasource.CreateLayer(layer_name, srs, ogr.wkbMultiPolygon)
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
            multipolygon = ogr.Geometry(ogr.wkbMultiPolygon)
            for shape in tr['info']['shapes']:
                coordinates = shape['coordinates'][0]
                ring = ogr.Geometry(ogr.wkbLinearRing)
                for x_y in coordinates:
                    x = x_y[0]
                    y = x_y[1]
                    ring.AddPoint(x, y)
                ring.CloseRings()
                polygon = ogr.Geometry(ogr.wkbPolygon)
                polygon.AddGeometry(ring)
                multipolygon.AddGeometry(polygon)
            feature.SetGeometry(multipolygon)

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
    if len(sys.argv) is 1:
        sys.exit(print_usage())
    else:
        sys.exit(main(sys.argv[1:]))