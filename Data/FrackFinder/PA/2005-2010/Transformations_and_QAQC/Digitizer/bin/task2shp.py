#!/usr/bin/env python


"""
Convert task_run.json from the digitizer app to a pond vector layer

Sample command:

digitizer-task2shp.py \


./digitizer-task2shp.py \
    --process-extra-fields \
    ../digitizer/2005-2008/Merged_Task_runs.json \
    ../digitizer/2005-2008/Deliverable_Ponds/Deliverable_Ponds.shp \
    --overwrite




Mark intersecting task_id's for deletion

CASE WHEN task_id = 104925 THEN 1
    WHEN task_id = 105634 THEN 1
    WHEN task_id = 104788 THEN 1
    WHEN task_id = 104753 THEN 1
    WHEN task_id = 105642 THEN 1
    WHEN task_id = 104543 THEN 1
    WHEN task_id = 105642 THEN 1
    WHEN task_id = 104486 THEN 1
    WHEN task_id = 104508 THEN 1
    WHEN task_id = 104783 THEN 1
END
"""


# TODO: Add tasks['id']
# TODO: Add tasks['info']['year']
# TODO: Add tasks['info']['county']


import sys
import json
import math
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


#/* ======================================================================= */#
#/*     Define print_usage() function
#/* ======================================================================= */#

def print_usage():

    """
    Commandline usage

    :return: returns 1 for for exit code purposes
    :rtype: int
    """
    print("")
    print('Usage: %s [options] task_run.json outfile.shp' % __docname__)
    print("")
    print("Options:")
    print("  --process-extra-fields -> Input task runs have attributes from task.json")
    print("  --overwrite -> Overwrite output.shp")
    print("  --class=str -> Add a classification field with a uniform value - use '%<field>' to pull from JSON")
    print("  --of=driver -> Specify output OGR driver - defaults to 'ESRI Shapefile'")
    print("  --no-check-intersect -> Don't check for intersecting geometries")
    print("  --no-split-multi     -> Don't split multi-polygon ponds into single parts")
    print("  --no-compute-area    -> Don't compute each feature's area")
    print("  --intersect-keep=str -> Keeps intersecting features based on their classified value")
    print("")

    return 1


#/* ======================================================================= */#
#/*     Define get_polygon() function
#/* ======================================================================= */#

def get_polygon(coordinates):

    """
    Convert a set of coordinates generated in the DartFrog PyBossa application
    to an OGR Geometry object containing a single polygon

    :param coordinates: coordinates from a PyBossa DartFrog generated task_run
    :type coordinates: list|tuple

    :return: OGR Geometry object containing a single polygon
    :rtype: <class 'osgeo.ogr.Geometry'>
    """

    polygon = ogr.Geometry(ogr.wkbPolygon)
    ring = ogr.Geometry(ogr.wkbLinearRing)
    for x_y in coordinates:
        x, y = x_y
        ring.AddPoint(x, y)
    ring.CloseRings()
    polygon.AddGeometry(ring)

    return polygon


#/* ======================================================================= */#
#/*     Define get_multipolygon() function
#/* ======================================================================= */#

def get_multipolygon(shapes_key):

    """
    Convert a set of coordinates generated in the DartFrog PyBossa application
    to an OGR Geometry object containing a multipolygon

    :param shapes_key: coordinates from a PyBossa DartFrog generated task_run
    :type shapes_key: list|tuple

    :return: OGR Geometry object containing a multipolygon
    :rtype: <class 'osgeo.ogr.Geometry'>
    """

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


#/* ======================================================================= */#
#/*     Define get_epsg_code() function
#/* ======================================================================= */#

def get_epsg_code(lat, lng):

    """
    Get a UTM EPSG code from the latitude and longitude

    :param lat: point's degree of latitude
    :type lat: float
    :param lng: point's degree longitude
    :type lng: float

    :return: EPSG code
    :rtype: int
    """

    zone = int(math.floor((lng + 180) / 6.0) + 1)

    epsg = 32600 + zone

    if lat < 0:
        epsg += 100

    return epsg


#/* ======================================================================= */#
#/*     Define compute_area() function
#/* ======================================================================= */#

def compute_area(geometry, target_epsg):

    """
    Compute a geometry's area in a different projection

    :param geometry: an OGR Geometry object
    :type geometry: <class 'osgeo.ogr.Geometry'>
    :param target_epsg:
    :type target_epsg:

    :return: the input OGR Geometry object with the area field populated
    :rtype: <class 'osgeo.ogr.Geometry'>
    """

    # Generate SRS objects and coordinate transformation
    geom_srs = osr.SpatialReference()
    geom_srs.ImportFromEPSG(4326)
    target_srs = osr.SpatialReference()
    target_srs.ImportFromEPSG(target_epsg)
    coord_transform = osr.CoordinateTransformation(geom_srs, target_srs)

    # Copy the geometry to prevent modifying the original
    geometry = geometry.Clone()
    geometry.Transform(coord_transform)

    return geometry.GetArea()


#/* ======================================================================= */#
#/*     Define man() function
#/* ======================================================================= */#

def main(args):

    """
    Commandline logic

    :param args: commandline arguments
    :type args: list|tuple
    :return: success returns 0 and failure returns 1
    :rtype: int
    """

    #/* ======================================================================= */#
    #/*     Defaults
    #/* ======================================================================= */#

    # task_run.json fields
    process_extra_fields = False

    # Input/output configuration
    overwrite_outfile = False
    output_driver = 'ESRI Shapefile'
    feature_classification = None

    # Additional processing
    check_geom_intersect = True
    check_geom_intersect_keep = None
    split_multi_ponds = True
    compute_pond_area = True
    field_prefix = '_t_'

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
        elif arg == '--process-extra-fields':
            process_extra_fields = True
        elif arg == '--overwrite':
            overwrite_outfile = True
        elif '--class=' in arg:
            feature_classification = arg.split('=', 1)[1]
        elif arg == '--no-split-multi':
            split_multi_ponds = False
        elif arg == '--no-compute-area':
            compute_pond_area = False

        # Additional processing
        elif arg == '--check-intersect':
            check_geom_intersect = True
        elif '--intersect-keep=' in arg:
            print("")
            print("    +--------------------------------------------------------------------------+")
            print("    |                                                                          |")
            print("    |    ERROR: Argument '--intersect-keep=str' is currently not functional    |")
            print("    |                                                                          |")
            print("    +--------------------------------------------------------------------------+")
            print("")
            check_geom_intersect_keep = arg.split('=', 1)[1]
            return 1


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
    # Field definitions: (name, width, type, precision)
    print("Creating layers and fields")
    layer_name = basename(outfile).split('.', 1)[1]
    layer = datasource.CreateLayer(layer_name, srs, ogr.wkbMultiPolygon)
    field_definitions = [('selection', 254, ogr.OFTString, None),
                         ('task_id', 10, ogr.OFTInteger, None),
                         ('intersect', 1, ogr.OFTInteger, None)]
    if process_extra_fields:
        field_definitions.append(('comp_loc', 254, ogr.OFTString, None))
        field_definitions.append(('crowd_sel', 254, ogr.OFTString, None))
        field_definitions.append(('county', 254, ogr.OFTString, None))
        field_definitions.append(('state', 254, ogr.OFTString, None))
        field_definitions.append(('year', 254, ogr.OFTString, None))
        field_definitions.append(('location', 254, ogr.OFTString, None))
    if feature_classification is not None:
        field_definitions.append(('class', 254, ogr.OFTString, None))
    if compute_pond_area:
        field_definitions.append(('area_m', 254, ogr.OFTReal, 2))

    # Add fields to layer
    for field_name, field_width, field_type, field_precision in field_definitions:
        field_object = ogr.FieldDefn(field_name, field_type)
        field_object.SetWidth(field_width)
        if field_precision is not None:
            field_object.SetPrecision(field_precision)
        layer.CreateField(field_object)

    # Loop through task runs and assemble output shapefile
    print("Processing %s task runs..." % str(len(task_runs)))
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

            # If we're splitting multi-ponds into single ponds,
            geometry_iterator = [geometry]
            if split_multi_ponds and 'shapes' in tr['info'] and len(tr['info']['shapes']) > 1:
                geometry_iterator = [get_polygon(i['coordinates'][0]) for i in tr['info']['shapes']]

            # Set attributes and geometry - this is kinda messy buuuuuuut too bad I guess ...
            for geometry in geometry_iterator:

                # Compute the area
                geometry_area = None  # Default to Null in case the computation fails
                if compute_pond_area:
                    centroid = geometry.Centroid()
                    centroid_lat = centroid.GetY()
                    centroid_lng = centroid.GetX()
                    epsg = get_epsg_code(centroid_lat, centroid_lng)
                    geometry_area = compute_area(geometry, epsg)

                if geometry is not None:
                    task_id = int(tr['task_id'])
                    feature = ogr.Feature(layer.GetLayerDefn())
                    feature.SetGeometry(geometry)
                    feature.SetField('selection', selection)
                    feature.SetField('task_id', task_id)

                    # Get the extra fields
                    if process_extra_fields:
                        try:
                            comp_loc = str(tr[field_prefix + 'info']['comp_loc'])
                            feature.SetField('comp_loc', comp_loc)
                        except KeyError:
                            print("WARNING: No '%scomp_loc' field: %s" % (field_prefix, str(task_id)))
                        try:
                            crowd_sel = str(tr[field_prefix + 'info']['crowd_sel'])
                            feature.SetField('crowd_sel', crowd_sel)
                        except KeyError:
                            print("WARNING: No '%scrowd_sel' field for: %s" % (field_prefix, str(task_id)))
                        try:
                            county = str(tr[field_prefix + 'info']['county'])
                            feature.SetField('county', county)
                        except KeyError:
                            print("WARNING: No '%scounty' field for: %s" % (field_prefix, str(task_id)))
                        try:
                            state = str(tr[field_prefix + 'info']['state'])
                            feature.SetField('state', state)
                        except KeyError:
                            print("WARNING: No '%sstate' field for: %s" % (field_prefix, str(task_id)))
                        try:
                            year = str(tr[field_prefix + 'info']['year'])
                            feature.SetField('year', year)
                        except KeyError:
                            print("WARNING: No '%syear' field for: %s" % (field_prefix, str(task_id)))
                        try:
                            location = str(tr[field_prefix + 'info']['location'])
                            feature.SetField('location', location)
                        except KeyError:
                            print("WARNING: No '%slocation' field for: %s" % (field_prefix, str(task_id)))

                    # Compute area
                    if compute_pond_area:
                        feature.SetField('area_m', geometry_area)

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

    # Update user
    print("Found %s with geometry" % str(len(layer)))

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

            # If we don't remove from the FID list, then an intersect will always be found
            del feature_fids[p_fid]

            # Loop through all the features we're comparing against and check for intersects
            for i_fid, i_feature in feature_fids.items():

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
                                try:
                                    layer.DeleteFeature(p_feature.GetFID())
                                except RuntimeError:
                                    # Multiple intersections can cause a feature to be deleted twice, which is fine,
                                    # except that a second deletion throws an exception
                                    pass
                            elif i_feature.GetField('class') != check_geom_intersect_keep:
                                try:
                                    layer.DeleteFeature(i_feature.GetFID())
                                except RuntimeError:
                                    # Multiple intersections can cause a feature to be deleted twice, which is fine
                                    # except that a second deletion throws an exception
                                    pass

        # Update user
        print("Found %s intersecting geometries" % str(intersect_count))
        print("Datasource now contains %s features" % str(len(layer)))

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
