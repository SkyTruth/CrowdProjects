#!/usr/bin/env python


import os
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
    print('Usage: %s [options] task_run.json outfile.shp' % __docname__)
    print("")
    print("Options:")
    print("  --process-county -> Input task runs have a county attribute")
    print("  --process-year   -> Input task runs have a year attribute")
    print("  --overwrite -> Overwrite output.shp")
    print("  --class=str -> Add a classification field with a uniform value")
    print("  --of=driver -> Specify output OGR driver - defaults to 'ESRI Shapefile'")
    print("")
    return 1


def get_polygon(coordinates):

    polygon = ogr.Geometry(ogr.wkbPolygon)
    ring = ogr.Geometry(ogr.wkbLinearRing)
    for x_y in coordinates:
        x, y = x_y
        ring.AddPoint(x, y)
    ring.CloseRings()
    polygon.AddGeometry(ring)

    return polygon


def get_multipolygon(shapes_key):

    multipolygon = ogr.Geometry(ogr.wkbMultiPolygon)
    for shape in shapes_key:
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

    return multipolygon


def main(args):

    #/* ======================================================================= */#
    #/*     Defaults
    #/* ======================================================================= */#

    # task_run.json fields
    process_year = False
    process_county = False

    # Input/output configuration
    overwrite_outfile = False
    output_driver = 'ESRI Shapefile'
    feature_classification = None

    #/* ======================================================================= */#
    #/*     Containers
    #/* ======================================================================= */#
    infile = None
    outfile = None

    #/* ======================================================================= */#
    #/*     Parse Arguments
    #/* ======================================================================= */#

    arg_error = False
    for arg in args:

        # Help arguments
        if arg in ('--usage', '--help', '--help-info'):
            return print_usage()

        # Additional options
        elif arg == '--process-year':
            process_year = True
        elif arg == '--process-county':
            process_county = True
        elif arg == '--overwrite':
            overwrite_outfile = True
        elif '--of=' in arg:
            output_driver = arg.split('=', 1)[1]
        elif '--class=' in arg:
            feature_classification = arg.split('=', 1)[1]

        # Positional arguments and errors
        else:
            # Catch input task_run.json
            if infile is None:
                infile = arg
            # Catch output shapefile.shp
            elif outfile is None:
                outfile = arg
            # Assume to be an invalid argument
            else:
                print("ERROR: Invalid argument: %s" % arg)
                arg_error = True

    #/* ======================================================================= */#
    #/*     Validate
    #/* ======================================================================= */#

    bail = False
    if arg_error:
        print("ERROR: Did not successfully parse arguments")
        bail = True

    # Input/output files
    if infile is None:
        print("ERROR: Need an infile")
        bail = True
    if outfile is None:
        print("ERROR: Need an output file")
        bail = True
    if infile is not None and not isfile(infile):
        print("ERROR: Can't find infile: %s" % infile)
        bail = True
    if outfile is not None and isfile(outfile) and not overwrite_outfile:
        print("ERROR: Output file exists and overwrite=%s" % str(overwrite_outfile))
        bail = True

    if bail:
        return 1

    #/* ======================================================================= */#
    #/*     Analyze Task Runs
    #/* ======================================================================= */#

    # Open JSON file
    with open(infile) as f:
        task_runs = json.load(f)

    # Delete output file if it exists
    if isfile(outfile):
        driver = ogr.GetDriverByName(output_driver)
        driver.DeleteDataSource(outfile)

    # Create the datasource
    driver = ogr.GetDriverByName(output_driver)
    datasource = driver.CreateDataSource(outfile)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)

    # Create layers and define fields
    layer_name = basename(outfile).split('.', 1)[1]
    layer = datasource.CreateLayer(layer_name, srs, ogr.wkbMultiPolygon)
    field_definitions = [('selection', 254, ogr.OFTString),
                         ('task_id', 10, ogr.OFTInteger)]
    if process_year:
        field_definitions.append(('year', 10, ogr.OFTInteger))
    if process_county:
        field_definitions.append(('county', 254, ogr.OFTString))
    if feature_classification is not None:
        field_definitions.append(('class', 254, ogr.OFTString))

    # Add fields to layer
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

        # Only create a geometry if the task run was digitized/kept its fracking classification
        if selection == 'done':

            geometry = None

            # Account for polygon vs. multipolygon change
            if 'shapes' in tr['info']:
                geometry = get_multipolygon(tr['info']['shapes'])
            elif 'shape' in tr['info']:
                geometry = get_polygon(tr['info']['shape']['coordinates'][0])

            # Set attributes and geometry
            if geometry is not None:
                task_id = int(tr['task_id'])
                feature = ogr.Feature(layer.GetLayerDefn())
                feature.SetGeometry(geometry)
                feature.SetField('selection', selection)
                feature.SetField('task_id', task_id)
                if process_year:
                    feature.SetField('year', tr['year'])
                if process_county:
                    feature.SetField('county', str(tr['county']))
                if feature_classification is not None:
                    feature.SetField('class', str(feature_classification))

                # Create the feature in the layer
                layer.CreateFeature(feature)

            # Cleanup
            feature = None

    # Cleanup
    driver = None
    datasource = None
    srs = None

    # Success
    return 0


#/* ======================================================================= */#
#/*     Command Line Execution
#/* ======================================================================= */#
if __name__ == '__main__':

    # Didn't get enough arguments - print usage
    if len(sys.argv) is 1:
        sys.exit(print_usage())

    # Got enough arguments - drop the first argument since its the script name and give the rest to main()
    else:
        sys.exit(main(sys.argv[1:]))