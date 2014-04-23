#!/usr/bin/env python


__license__ = """
Copyright (c) 2014, SkyTruth
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the {organization} nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


import os
import sys
import json
import inspect
from os import sep
from os.path import isfile
from os.path import basename

try:
    from osgeo import ogr
    from osgeo import osr
except ImportError:
    import ogr
    import osr


# Build information
__author__ = 'Kevin Wurster'
__copyright__ = 'Copyright (c) 2014, SkyTruth'
__version__ = '0.1'
__release__ = '2014/04/23'
__docname__ = basename(inspect.getfile(inspect.currentframe()))


def print_usage():

    """
    Command line usage information
    """

    print("")
    print("Usage: %s [options] task.json task_run.json output/directory" % __docname__)
    print("")
    print("Options:")
    print("  --help-info  -> Print out a list of help related flags")
    print("  --overwrite  -> Overwrite output files")
    print("  --prefix=str -> Output filename prefix")
    print("  --wellpad-file-name=str -> Defaults to 'wellpad.shp")
    print("  --bbox-file-name=str -> Defaults to 'bbox.shp")
    print("  --clicks-file-name=str -> Defaults to 'clicks.shp")
    print("")
    print("OGR Options:")
    print("  --of=driver  -> Output driver name/file type - default='ESRI Shapefile'")
    print("  --epsg=int   -> EPSG code for coordinates in task.json - default=4326")
    print("")

    return 1


def print_license():

    """
    Print out license information
    """

    print(__license__)

    return 1


def print_help():

    """
    Detailed help information
    """

    print("")
    print("%s Detailed Help" % __docname__)
    print("--------------" + "-" * len(__docname__))
    print("Input is task.json and task_run.json from MooreFrog")
    print("Output is a set of bounding boxes, well pad points, ")
    print("and pond clicks.")
    print("")

    return 1


def print_help_info():
    """
    Print a list of help related flags
    """
    print("")
    print("Help flags:")
    print("  --help    -> More detailed description of this utility")
    print("  --usage   -> Arguments, parameters, flags, options, etc.")
    print("  --version -> Version and ownership information")
    print("  --license -> License information")
    print("  ")

    return 1


def print_version():

    """
    Print script version information
    """

    print("")
    print('%s version %s - released %s' % (__docname__, __version__, __release__))
    print(__copyright__)
    print("")

    return 1


def create_bboxes(tasks, layer):

    """
    Add bounding boxes to input layer
    """

    # Update user
    print("Creating bounding boxes")

    # Define fields
    print("  Defining bbox fields...")
    fields_definitions = (('id', 10, ogr.OFTInteger),
                          ('site_id', 254, ogr.OFTString),
                          ('location', 254, ogr.OFTString),
                          ('wms_url', 254, ogr.OFTString),
                          ('county', 254, ogr.OFTString),
                          ('year', 10, ogr.OFTInteger),
                          ('qaqc', 254, ogr.OFTString))

    # Create fields
    for field_name, field_width, field_type in fields_definitions:
        print("    " + field_name)
        field_object = ogr.FieldDefn(field_name, field_type)
        field_object.SetWidth(field_width)
        layer.CreateField(field_object)

    # Loop through tasks and create features
    print("  Processing %s tasks..." % str(len(tasks)))
    for task in tasks:

        # Get field content
        location = str(task['info']['latitude']) + str(task['info']['longitude']) + '---' + str(task['info']['year'])
        field_values = {'id': int(task['id']),
                        'site_id': str(task['info']['SiteID']),
                        'location': str(location),
                        'wms_url': str(task['info']['url']),
                        'county': str(task['info']['county']),
                        'year': int(task['info']['year'])}

        # Get corner coordinates and assemble into a geometry
        coordinates = task['info']['bbox'].split(',')
        x_min = float(coordinates[2])
        x_max = float(coordinates[0])
        y_min = float(coordinates[1])
        y_max = float(coordinates[3])
        ring = ogr.Geometry(ogr.wkbLinearRing)
        ring.AddPoint(x_min, y_max)
        ring.AddPoint(x_min, y_min)
        ring.AddPoint(x_max, y_min)
        ring.AddPoint(x_max, y_max)
        ring.CloseRings()

        # Create a new feature and assign geometry and field values
        rectangle = ogr.Geometry(ogr.wkbPolygon)
        rectangle.AddGeometry(ring)
        feature = ogr.Feature(layer.GetLayerDefn())
        feature.SetGeometry(rectangle)
        layer.CreateFeature(feature)
        for field, value in field_values.iteritems():
            feature.SetField(field, value)
        rectangle.Destroy()
        feature.Destroy()

    # Update user
    print("  Done")
    return True


def create_clicks(task_runs, layer):

    """
    Add click points to layer
    """

    # Update user
    print("Creating clicks")

    # Define fields
    print("  Defining click fields...")
    fields_definitions = (('id', 10, ogr.OFTInteger),
                          ('task_id', 10, ogr.OFTInteger),
                          ('qaqc', 254, ogr.OFTString))

    # Create fields
    for field_name, field_width, field_type in fields_definitions:
        print("    " + field_name)
        field_object = ogr.FieldDefn(field_name, field_type)
        field_object.SetWidth(field_width)
        layer.CreateField(field_object)

    # Loop through tasks and create features
    print("  Processing %s tasks..." % str(len(task_runs)))
    for task_run in task_runs:

        # Get field content
        field_values = {'id': int(task_run['id']),
                        'task_id': int(task_run['task_id'])}

        # Get list of clicks
        clicks = task_run['info']['positions']
        for click in clicks:
            feature = ogr.Feature(layer.GetLayerDefn())

            # Set field attributes and geometry
            point = ogr.CreateGeometryFromWkt("POINT(%f %f)" % (float(click['lon']), float(click['lat'])))
            feature.SetGeometry(point)
            for field, value in field_values.iteritems():
                feature.SetField(field, value)
            layer.CreateFeature(feature)
            feature.Destroy()

    # Update user
    print("  Done")
    return True


def create_wellpads(tasks, layer):

    """
    Add click points to layer
    """

    # Update user
    print("Creating wellpads")

    # Define fields
    print("  Defining layer fields...")
    fields_definitions = (('id', 10, ogr.OFTInteger),
                          ('site_id', 254, ogr.OFTString),
                          ('location', 254, ogr.OFTString),
                          ('wms_url', 254, ogr.OFTString),
                          ('county', 254, ogr.OFTString),
                          ('year', 10, ogr.OFTInteger),
                          ('qaqc', 254, ogr.OFTString))

    # Create fields
    for field_name, field_width, field_type in fields_definitions:
        print("    " + field_name)
        field_object = ogr.FieldDefn(field_name, field_type)
        field_object.SetWidth(field_width)
        layer.CreateField(field_object)

    # Loop through tasks and create features
    print("  Processing %s tasks..." % str(len(tasks)))
    for task in tasks:

        # Get field content
        location = str(task['info']['latitude']) + str(task['info']['longitude']) + '---' + str(task['info']['year'])
        field_values = {'id': int(task['id']),
                        'site_id': str(task['info']['SiteID']),
                        'location': location,
                        'wms_url': str(task['info']['url']),
                        'county': str(task['info']['county']),
                        'year': int(task['info']['year'])}

        # Define and create feature
        feature = ogr.Feature(layer.GetLayerDefn())
        wkt = "POINT(%f %f)" % (float(task['info']['longitude']), float(task['info']['latitude']))
        point = ogr.CreateGeometryFromWkt(wkt)
        feature.SetGeometry(point)
        for field, value in field_values.iteritems():
            feature.SetField(field, value)
        layer.CreateFeature(feature)
        feature.Destroy()

    # Update user
    print("  Done")
    return True


def main(args):

    # Containers
    task_file_path = None
    task_run_file_path = None
    output_directory = None
    output_prefix = ''

    # Defaults
    overwrite = False
    bbox_file_name = 'bbox.shp'
    wellpad_file_name = 'wellpads.shp'
    clicks_file_name = 'clicks.shp'
    epsg_code = 4326
    vector_driver = 'ESRI Shapefile'

    # Parse arguments
    arg_error = False
    for arg in args:

        # Help arguments
        if arg in ('--help', '-help'):
            return print_help()
        elif arg in ('--help-info', '-help-info', '--helpinfo', '--helpinfo'):
            return print_help_info()
        elif arg in ('--license', '-license'):
            return print_license()
        elif arg in ('--version', '-version'):
            return print_version()

        # Additional options
        elif '--prefix=' in arg:
            output_prefix = arg.split('=', 1)[1]
        elif '--bbox-file-name=' in arg:
            bbox_file_name = arg.split('=', 1)[1]
        elif '--wellpad-file-name=' in arg or '--well-pad-file-name=' in arg:
            wellpad_file_name = arg.split('=', 1)[1]
        elif '--clicks-file-name=' in arg:
            clicks_file_name = arg.split('=', 1)[1]
        elif '--epsg=' in arg:
            epsg_code = arg.split('=', 1)[1]
        elif arg == '--overwrite':
            overwrite = True

        # Ignore empty arguments
        elif arg == '':
            pass

        # Positional arguments
        else:

            # Get task.json file
            if task_file_path is None:
                task_file_path = arg

            # Get task_run.json file
            elif task_run_file_path is None:
                task_run_file_path = arg

            # Get output directory
            elif output_directory is None:
                output_directory = arg

            # Argument is unrecognized - throw an error
            else:
                print("ERROR: Invalid argument: %s" % str(arg))
                arg_error = True

    # Define output file paths
    clicks_file_path = sep.join([output_directory, output_prefix + clicks_file_name])
    bbox_file_path = sep.join([output_directory, output_prefix + bbox_file_name])
    wellpad_file_path = sep.join([output_directory, output_prefix + wellpad_file_name])

    # Validate
    bail = False
    if arg_error:
        print("ERROR: Did not successfully parse arguments")
        bail = True
    if output_directory is None or not os.access(output_directory, os.W_OK):
        print("ERROR: Can't access output directory: %s" % output_directory)
        bail = True
    if task_file_path is None or not os.access(task_file_path, os.R_OK):
        print("ERROR: Can't access task file: %s" % task_file_path)
        bail = True
    if task_run_file_path is None or not os.access(task_run_file_path, os.R_OK):
        print("ERROR: Can't access task run file: %s" % task_run_file_path)
        bail = True
    if not overwrite:
        for filepath in [clicks_file_path, bbox_file_path, wellpad_file_path]:
            if isfile(filepath):
                print("ERROR: Output file exists: %s" % filepath)
                bail = True
    try:
        epsg_code = int(epsg_code)
    except ValueError:
        print("ERROR: EPSG code must be an int: %s" % str(epsg_code))
        bail = True
    if bail:
        return 1

    # Update user
    print("Task file: %s" % task_file_path)
    print("Task run file: %s" % task_run_file_path)
    print("Output directory: %s" % output_directory)

    # Convert files to json
    print("Extracting JSON...")
    with open(task_file_path, 'r') as f:
        task_json = json.load(f)
    with open(task_run_file_path, 'r') as f:
        task_run_json = json.load(f)
    print("  Num tasks: %s" % str(len(task_json)))
    print("  Num task runs: %s" % str(len(task_run_json)))

    # Get SRS and driver objects
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg_code)
    driver = ogr.GetDriverByName(vector_driver)

    # Delete existing files if in overwrite mode
    if overwrite:
        print("Overwriting existing files...")
        for filepath in [clicks_file_path, bbox_file_path, wellpad_file_path]:
            if isfile(filepath):
                driver.DeleteDataSource(filepath)
                print("  Deleted %s" % filepath)

    # Create clicks file OGR object
    clicks_layer_name = clicks_file_name.split('.', 1)[0]
    print("Creating empty clicks outfile...")
    print("  Path: %s" % clicks_file_path)
    print("  Layer: %s" % clicks_layer_name)
    clicks_datasource = driver.CreateDataSource(clicks_file_path)
    clicks_layer = clicks_datasource.CreateLayer(clicks_layer_name, srs, ogr.wkbPoint)

    # Create bounding box OGR object
    bbox_layer_name = bbox_file_name.split('.', 1)[0]
    print("Creating empty bbox outfile...")
    print("  Path: %s" % bbox_file_path)
    print("  Layer: %s" % bbox_layer_name)
    bbox_datasource = driver.CreateDataSource(bbox_file_path)
    bbox_layer = bbox_datasource.CreateLayer(bbox_layer_name, srs, ogr.wkbPolygon)

    # Create wellpad OGR object
    wellpad_layer_name = wellpad_file_name.split('.', 1)[0]
    print("Creating empty wellpad outfile...")
    print("  Path: %s" % wellpad_file_path)
    print("  Layer: %s" % wellpad_layer_name)
    wellpad_datasource = driver.CreateDataSource(wellpad_file_path)
    wellpad_layer = wellpad_datasource.CreateLayer(wellpad_layer_name, srs, ogr.wkbPoint)

    # == Create Files == #
    if not create_bboxes(task_json, bbox_layer):
        print("ERROR: Problem creating bounding boxes")
    if not create_clicks(task_run_json, clicks_layer):
        print("ERROR: Problem creating clicks")
    if not create_wellpads(task_json, wellpad_layer):
        print("ERROR: Problem creating wellpads")

    # Cleanup OGR data sources
    print("Cleaning up...")
    srs = None
    driver = None
    clicks_layer = None
    bbox_layer = None
    wellpad_layer = None
    clicks_datasource.Destroy()
    bbox_datasource.Destroy()
    wellpad_datasource.Destroy()

    # Success
    print("Done.")
    return 0


if __name__ == '__main__':
    if len(sys.argv) is 1:
        sys.exit(print_usage())
    else:
        sys.exit(main(sys.argv[1:]))
