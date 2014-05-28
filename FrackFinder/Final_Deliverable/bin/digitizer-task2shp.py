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


# Get the script name
__docname__ = basename(__file__)


# Force OGR to use exceptions
ogr.UseExceptions()


def print_usage():
    print("")
    print('Usage: %s [options] task_run.json outfile.shp' % __docname__)
    print("")
    print("Options:")
    print("  --process-county -> Input task runs have a county attribute")
    print("  --process-year   -> Input task runs have a year attribute")
    print("  --overwrite -> Overwrite output.shp")
    print("  --class=str -> Add a classification field with a uniform value - use '%<field>' to pull from JSON")
    print("  --of=driver -> Specify output OGR driver - defaults to 'ESRI Shapefile'")
    print("  --check-intersect   -> Don't check for intersecting geometries")
    print("  --intersect-keep=str -> Keeps intersecting features based on their classified value")
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

    # Additional processing
    check_geom_intersect = False
    check_geom_intersect_keep = None

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

        # OGR Configuration
        elif '--of=' in arg:
            output_driver = arg.split('=', 1)[1]

        # Output file options
        elif arg == '--process-year':
            process_year = True
        elif arg == '--process-county':
            process_county = True
        elif arg == '--overwrite':
            overwrite_outfile = True
        elif '--class=' in arg:
            feature_classification = arg.split('=', 1)[1]

        # Additional processing
        elif arg == '--check-intersect':
            check_geom_intersect = True
        elif '--keep-intersect=' in arg:
            check_geom_intersect_keep = arg.split('=', 1)[1]

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
    if check_geom_intersect_keep is not None and feature_classification is None:
        print("ERROR: Need a classification in order to filter intersects")
        bail = True

    if bail:
        return 1

    #/* ======================================================================= */#
    #/*     Analyze Task Runs
    #/* ======================================================================= */#

    # Open JSON file
    with open(infile) as f:
        task_runs = json.load(f)
    print("Found %s task runs" % str(len(task_runs)))

    # Delete output file if it exists
    if isfile(outfile):
        print("Overwriting: %s" % outfile)
        driver = ogr.GetDriverByName(output_driver)
        driver.DeleteDataSource(outfile)

    # Create the datasource
    print("Creating OGR datasource")
    driver = ogr.GetDriverByName(output_driver)
    datasource = driver.CreateDataSource(outfile)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)

    # Create layers and define fields
    print("Creating layers and fields")
    layer_name = basename(outfile).split('.', 1)[1]
    layer = datasource.CreateLayer(layer_name, srs, ogr.wkbMultiPolygon)
    field_definitions = [('selection', 254, ogr.OFTString),
                         ('task_id', 10, ogr.OFTInteger),
                         ('intersect', 1, ogr.OFTInteger)]
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
    print("Processing task runs...")
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

                # Normal feature classification is just a simple write but the % indicates that the classification
                # is to be pulled from a field within the json
                if feature_classification is not None and feature_classification[0] != '%':
                    feature.SetField('class', str(feature_classification))
                elif feature_classification is not None and feature_classification[0] == '%':
                    try:
                        value = str(tr[feature_classification[1:]])
                    except KeyError:
                        value = None
                    feature.SetField('class', value)

                # Create the feature in the layer
                layer.CreateFeature(feature)

            # Cleanup
            feature = None

    # Loop through the output file and check for intersecting geometries
    if check_geom_intersect:

        print("Searching for intersecting geometries...")

        intersect_count = 0

        # Convert layer's features to a dictionary where keys are FID's and values are feature objects
        feature_fids = {i.GetFID(): i for i in layer}

        # Loop through layer
        layer.ResetReading()
        intersect_count = 0
        for p_feature in layer:

            # Make sure we're supposed to process this feature
            p_fid = p_feature.GetFID()

            # If we don't remove from the FID set, then an intersect will always be found
            del feature_fids[p_fid]

            # Loop through all the features we're comparing against and check for intersects
            for i_feature, i_feature in feature_fids.copy().items():

                # Prefixes: p=primary i=intersect - primary comes from outer loop
                p_geom = p_feature.GetGeometryRef()
                i_geom = i_feature.GetGeometryRef()
                if p_geom.IsSimple() and i_geom.IsSimple():
                    if p_geom.Intersect(i_geom):

                        intersect_count += 1

                        # Modify the primary feature in place
                        p_feature.SetField('intersect', 1)
                        layer.SetFeature(p_feature)

                        # Modify the intersecting feature so it has the appropriate attributes
                        i_feature.SetField('intersect', 1)
                        layer.SetFeature(i_feature)

                        # Filter out / delete one of the intersecting features if explicitly told to do so
                        if check_geom_intersect_keep is not None:
                            if p_feature.GetField('class') is i_feature.GetField('class'):
                                print("WARNING: Could not filter intersect: homogeneous class")
                            elif p_feature.GetField('class') != check_geom_intersect_keep:
                                layer.DeleteFeature(p_feature.GetFID())
                            elif i_feature.GetField('class') != check_geom_intersect_keep:
                                layer.DeleteFeature(i_feature.GetFID())

        # Update user
        print("Found %s intersecting geometries" % str(intersect_count))

    # Cleanup
    driver = None
    datasource = None
    srs = None

    # Success

    print("Done.")
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
