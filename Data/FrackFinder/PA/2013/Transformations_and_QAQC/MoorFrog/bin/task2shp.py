#!/usr/bin/env python


# This document is part of CrowdProjects
# https://github.com/SkyTruth/CrowdTools


# =================================================================================== #
#
#  New BSD License
#
#  Copyright (c) 2014, SkyTruth
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
#  * The names of its contributors may not be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#  FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#  DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#  OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# =================================================================================== #


"""
Convert MoorFrog output to a spatial format
"""

from __future__ import print_function

import os
import sys
import json
from os.path import *
try:
    from osgeo import ogr
    from osgeo import osr
except ImportError:
    import ogr
    import osr
ogr.UseExceptions()
osr.UseExceptions()


__docname__ = basename(__file__)
__all__ = ['print_usage', 'print_help', 'print_license', 'print_help_info', 'print_version', 'main']


#/* ======================================================================= */#
#/*     Build Information
#/* ======================================================================= */#
__author__ = 'Kevin Wurster'
__release__ = '2014-06-17'
__version__ = '0.1-dev'
__license__ = '''
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
'''


#/* ======================================================================= */#
#/*     Define print_usage() function
#/* ======================================================================= */#

def print_usage():

    """
    Print commandline usage

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    print("""
Usage: %s --help-info [options] task.json task_run.json

Options:
  --overwrite -> Overwrite output files
  --bbox path -> Output bounding box file
  --clicks path -> Output clicks file
  --wellpads path -> Output wellpads file
  --of=driver -> Output driver name/file type - default='ESRI Shapefile'
  --epsg=int  -> EPSG code for coordinates in task.json - default=4326
""" % __docname__)

    return 1


#/* ======================================================================= */#
#/*     Define print_help() function
#/* ======================================================================= */#

def print_help():

    """
    Print more detailed help information

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    print("""
Help: {0}
------{1}
Input is task.json and task_run.json from MoorFrog
Output is a set of bounding boxes, well pad points,
and pond clicks.
    """.format(__docname__, '-' * len(__docname__)))

    return 1


#/* ======================================================================= */#
#/*     Define print_license() function
#/* ======================================================================= */#

def print_license():

    """
    Print licensing information

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    print(__license__)

    return 1


#/* ======================================================================= */#
#/*     Define print_help_info() function
#/* ======================================================================= */#

def print_help_info():

    """
    Print a list of help related flags

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    print("""
Help Flags:
  --help    -> More detailed description of this utility
  --usage   -> Arguments, parameters, flags, options, etc.
  --version -> Version and ownership information
  --license -> License information
    """)

    return 1


#/* ======================================================================= */#
#/*     Define print_version() function
#/* ======================================================================= */#

def print_version():

    """
    Print the module version information

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    print("""
%s version %s - released %s"
    """ % (__docname__, __version__, __release__))

    return 1


#/* ======================================================================= */#
#/*     Define create_bboxes() function
#/* ======================================================================= */#

def create_bboxes(outfile=None, driver='ESRI Shapefile', layer_name='bboxes', epsg=None, tasks=None, overwrite=False):

    """
    Create a bbox file

    :param outfile: output file path
    :type outfile: str
    :param driver: outfile OGR driver
    :type driver: str
    :param layer_name: outfile layer name
    :type layer_name: str
    :param epsg: outfile EPSG code
    :type epsg: int
    :param tasks: input JSON object from json.load(open('task.json'))
    :type tasks: list|tuple
    :param overwrite: specifies whether or not the output file should be overwritten
    :type overwrite: bool

    :return: True on success False on failure
    :rtype: bool
    """

    # Create OGR objects
    driver = ogr.GetDriverByName(driver)
    if not overwrite and isfile(outfile):
        raise IOError("  ERROR: Overwrite=%s and output wellpad file exists: %s" % outfile)
    elif overwrite and isfile(outfile):
        driver.DeleteDataSource(outfile)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg)
    datasource = driver.CreateDataSource(outfile)
    layer = datasource.CreateLayer(layer_name, srs, ogr.wkbPolygon)

    # Define fields
    fields_definitions = (('id', 10, ogr.OFTInteger),
                          ('site_id', 254, ogr.OFTString),
                          ('location', 254, ogr.OFTString),
                          ('wms_url', 254, ogr.OFTString),
                          ('county', 254, ogr.OFTString),
                          ('year', 10, ogr.OFTInteger),
                          ('qaqc', 254, ogr.OFTString))

    # Create fields
    for field_name, field_width, field_type in fields_definitions:
        field_object = ogr.FieldDefn(field_name, field_type)
        field_object.SetWidth(field_width)
        layer.CreateField(field_object)

    # Loop through tasks and create features
    i = 0
    num_tasks = len(tasks)
    for task in tasks:

        # Progress
        i += 1
        sys.stdout.write("\r\x1b[K" + "  %s/%s" % (str(i), str(num_tasks)))
        sys.stdout.flush()

        # Define feature
        feature = ogr.Feature(layer.GetLayerDefn())
        polygon = ogr.Geometry(ogr.wkbLinearRing)
        west, south, east, north = task['info']['bbox'].split(',')
        polygon.AddPoint(west, north)
        polygon.AddPoint(west, south)
        polygon.AddPoint(east, south)
        polygon.AddPoint(east, north)
        polygon.CloseRings()
        geometry = ogr.Geometry(layer.GetLayerDefn())
        geometry.AddGeometry(polygon)
        feature.SetGeometry(geometry)

        # Get field content
        location = str(task['info']['latitude']) + ',' + str(task['info']['longitude']) + ',' + str(task['info']['year'])
        feature.SetField('id', int(task['id']))
        feature.SetField('site_id', str(task['info']['SiteID']))
        feature.SetField('location', location)
        feature.SetField('wms_url', str(task['info']['url']))
        feature.SetField('county', str(task['info']['county']))
        feature.SetField('year', int(task['info']['year']))

        # Add feature to layer
        layer.CreateFeature(feature)

    # Cleanup
    geometry = None
    feature = None
    layer = None
    datasource = None
    driver = None
    srs = None

    # Update user
    print(" - Done")
    return True


#/* ======================================================================= */#
#/*     Define create_clicks() function
#/* ======================================================================= */#

def create_clicks(outfile=None, driver='ESRI Shapefile', layer_name='clicks', epsg=None,
                  task_runs=None, overwrite=False):

    """
    Create a clicks file

    :param outfile: output file path
    :type outfile: str
    :param driver: outfile OGR driver
    :type driver: str
    :param layer_name: outfile layer name
    :type layer_name: str
    :param epsg: outfile EPSG code
    :type epsg: int
    :param task_runs: input JSON object from json.load(open('task_run.json'))
    :type task_runs: list|tuple
    :param overwrite: specifies whether or not the output file should be overwritten
    :type overwrite: bool

    :return: True on success False on failure
    :rtype: bool
    """

    # Create OGR objects
    driver = ogr.GetDriverByName(driver)
    if not overwrite and isfile(outfile):
        raise IOError("  ERROR: Overwrite=%s and output clicks file exists: %s" % outfile)
    elif overwrite and isfile(outfile):
        driver.DeleteDataSource(outfile)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg)
    datasource = driver.CreateDataSource(outfile)
    layer = datasource.CreateLayer(layer_name, srs, ogr.wkbPoint)

    # Define and create fields
    fields_definitions = (('id', 10, ogr.OFTInteger),
                          ('task_id', 10, ogr.OFTInteger),
                          ('qaqc', 254, ogr.OFTString))
    for field_name, field_width, field_type in fields_definitions:
        field_object = ogr.FieldDefn(field_name, field_type)
        field_object.SetWidth(field_width)
        layer.CreateField(field_object)

    # Loop through tasks and create features
    i = 0
    num_task_runs = len(task_runs)
    for task_run in task_runs:

        # Progress
        i += 1
        sys.stdout.write("\r\x1b[K" + "  %s/%s" % (str(i), str(num_task_runs)))
        sys.stdout.flush()

        # Get list of clicks
        for click in task_run['info']['positions']:

            # Define feature and set fields
            feature = ogr.Feature(layer.GetLayerDefn())
            geometry = ogr.Geometry(layer.GetLayerDefn())
            geometry.AddPoint(float(click['lon']), float(click['lat']))
            feature.SetGeometry(geometry)
            feature.SetField('id', int(task_run['id']))
            feature.SetField('task_id', int(task_run['task_id']))

            # Add feature to layer
            layer.CreateFeature(feature)

    # Cleanup
    geometry = None
    feature = None
    layer = None
    datasource = None
    driver = None
    srs = None

    # Update user
    print(" - Done")

    # Success
    return True


#/* ======================================================================= */#
#/*     Define create_wellpads() function
#/* ======================================================================= */#

def create_wellpads(outfile=None, driver='ESRI Shapefile', layer_name='wellpads', epsg=None, tasks=None, overwrite=False):

    """
    Create a wellpads file

    :param outfile: output file path
    :type outfile: str
    :param driver: outfile OGR driver
    :type driver: str
    :param layer_name: outfile layer name
    :type layer_name: str
    :param epsg: outfile EPSG code
    :type epsg: int
    :param tasks: input JSON object from json.load(open('task.json'))
    :type tasks: list|tuple
    :param overwrite: specifies whether or not the output file should be overwritten
    :type overwrite: bool

    :return: True on success False on failure
    :rtype: bool
    """

    # Create OGR objects
    driver = ogr.GetDriverByName(driver)
    if not overwrite and isfile(outfile):
        raise IOError("  ERROR: Overwrite=%s and output wellpad file exists: %s" % outfile)
    elif overwrite and isfile(outfile):
        driver.DeleteDataSource(outfile)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg)
    datasource = driver.CreateDataSource(outfile)
    layer = datasource.CreateLayer(layer_name, srs, ogr.wkbPoint)

    # Define and create fields
    field_definitions = (('id', 10, ogr.OFTInteger),
                         ('site_id', 254, ogr.OFTString),
                         ('location', 254, ogr.OFTString),
                         ('wms_url', 254, ogr.OFTString),
                         ('county', 254, ogr.OFTString),
                         ('year', 10, ogr.OFTInteger),
                         ('qaqc', 254, ogr.OFTString))
    for field_name, field_width, field_type in field_definitions:
        field_object = ogr.FieldDefn(field_name, field_type)
        field_object.SetWidth(field_width)
        layer.CreateField(field_object)

    # Loop through tasks and create features
    num_tasks = len(tasks)
    i = 0
    for task in tasks:

        # Progress
        i += 1
        sys.stdout.write("\r\x1b[K" + "  %s/%s" % (str(i), str(num_tasks)))
        sys.stdout.flush()

        # Define feature
        feature = ogr.Feature(layer.GetLayerDefn())
        geometry = ogr.Geometry(layer.GetLayerDefn())
        geometry.AddPoint(float(task['info']['longitude']), float(task['info']['latitude']))
        feature.SetGeometry(geometry)

        # Populate fields
        location = str(task['info']['latitude']) + ',' + str(task['info']['longitude']) + ',' + str(task['info']['year'])
        feature.SetField('location', location)
        feature.SetField('id', int(task['id']))
        feature.SetField('site_id', str(task['info']['SiteID']))
        feature.SetField('wms_url', str(task['info']['url']))
        feature.SetField('county', str(task['info']['county']))
        feature.SetField('year', int(task['info']['year']))

        # Add feature to layer
        layer.CreateFeature(feature)

    # Cleanup
    geometry = None
    feature = None
    layer = None
    datasource = None
    driver = None
    srs = None

    # Update user
    print(" - Done")

    # Success
    return True


#/* ======================================================================= */#
#/*     Define main()
#/* ======================================================================= */#

def main(args):

    """
    Commandline logic

    :param args: commandline arguments from sys.argv[1:]
    :type args: list|tuple

    :return: 0 on success and 1 on failure
    :rtype: int
    """

    #/* ======================================================================= */#
    #/*     Defaults
    #/* ======================================================================= */#

    # OGR defaults
    output_epsg_code = 4326
    output_driver = 'ESRI Shapefile'

    # Additional options
    overwrite_mode = False

    #/* ======================================================================= */#
    #/*     Containers
    #/* ======================================================================= */#

    # Input/Output file
    task_file = None
    task_run_file = None
    outfile_bbox = None
    outfile_wellpads = None
    outfile_clicks = None

    #/* ======================================================================= */#
    #/*     Containers
    #/* ======================================================================= */#

    i = 0
    arg_error = False
    for arg in args:

        try:
            arg = args[i]

            # Help arguments
            if arg in ('--help', '-help'):
                return print_help()
            elif arg in ('--help-info', '-help-info', '--helpinfo', '--helpinfo'):
                return print_help_info()
            elif arg in ('--license', '-license'):
                return print_license()
            elif arg in ('--version', '-version'):
                return print_version()

            # Configure file names
            elif arg in ('--bbox', '-bbox', '-b'):
                i += 2
                outfile_bbox = args[i - 1]
            elif arg in ('--wellpads', '-pads', '-p'):
                i += 2
                outfile_wellpads = args[i - 1]
            elif arg in ('--clicks', '-clicks', '-c'):
                i += 2
                outfile_clicks = args[i - 1]

            # OGR options
            elif '--epsg=' in arg:
                i += 1
                output_epsg_code = arg.split('=', 1)[1]
            elif '--of=' in arg:
                i += 1
                output_driver = arg.split('=', 1)[1]

            # Additional options
            elif arg == '--overwrite':
                i += 1
                overwrite_mode = True

            # Positional arguments
            else:

                # Get task.json file
                if task_file is None:
                    i += 1
                    task_file = arg

                # Get task_run.json file
                elif task_run_file is None:
                    i += 1
                    task_run_file = arg

                # Argument is unrecognized - throw an error
                else:
                    i += 1
                    arg_error = True
                    print("ERROR: Invalid argument: %s" % str(arg))

        # An argument with parameters likely didn't iterate 'i' properly
        except IndexError:
            i += 1
            arg_error = True
            print("ERROR: An argument has invalid parameters: %s" % arg)

    #/* ======================================================================= */#
    #/*     Validate
    #/* ======================================================================= */#

    bail = False

    # Check arguments
    if arg_error:
        bail = True
        print("ERROR: Did not successfully parse arguments")

    # Check input files
    if task_file is None:
        bail = True
        print("ERROR: Need a task file")
    elif not os.access(task_file, os.R_OK):
        bail = True
        print("ERROR: Can't access task file: %s" % task_file)
    if task_run_file is None:
        bail = True
        print("ERROR: Need a task run file")
    elif not os.access(task_run_file, os.R_OK):
        bail = True
        print("ERROR: Can't access task run file: %s" % task_run_file)

    # Check output files
    if outfile_clicks is not None and not overwrite_mode and isfile(outfile_clicks):
        bail = True
        print("ERROR: Overwrite=%s and output click file exists: %s" % (str(overwrite_mode), outfile_clicks))
    if outfile_wellpads is not None and not overwrite_mode and isfile(outfile_wellpads):
        bail = True
        print("ERROR: Overwrite=%s and output wellpad file exists: %s" % (str(overwrite_mode), outfile_wellpads))
    if outfile_bbox is not None and not overwrite_mode and isfile(outfile_bbox):
        bail = True
        print("ERROR: Overwrite=%s and output bbox file exists: %s" % (str(overwrite_mode), outfile_bbox))
    if outfile_clicks is None and outfile_wellpads is None and outfile_bbox is None:
        bail = True
        print("ERROR: No output file specified - nothing to do")

    # Check OGR EPSG code
    try:
        output_epsg_code = int(output_epsg_code)
    except ValueError:
        bail = True
        print("ERROR: EPSG code must be an int: %s" % str(output_epsg_code))

    # Check OGR driver
    if output_driver not in [ogr.GetDriver(i).GetName() for i in range(ogr.GetDriverCount())]:
        bail = True
        print("ERROR: Invalid OGR driver: %s" % output_driver)

    if bail:
        return 1

    #/* ======================================================================= */#
    #/*     Create Files
    #/* ======================================================================= */#

    # Convert files to json
    print("Extracting JSON...")
    try:
        with open(task_file, 'r') as f:
            tasks_json = json.load(f)
        with open(task_run_file, 'r') as f:
            task_runs_json = json.load(f)
    except ValueError:
        print("ERROR: An input JSON file could not be decoded")
        return 1
    print("  Num tasks: %s" % str(len(tasks_json)))
    print("  Num task runs: %s" % str(len(task_runs_json)))

    #/* ======================================================================= */#
    #/*     Process Data
    #/* ======================================================================= */#

    if outfile_bbox is not None:
        print("Creating bounding boxes ...")
        try:
            create_bboxes(outfile=outfile_bbox, driver=output_driver, epsg=output_epsg_code,
                          tasks=tasks_json, overwrite=overwrite_mode)
        except IOError, e:
            print(e)
            return 1
    if outfile_clicks is not None:
        print("Creating clicks ...")
        try:
            create_clicks(outfile=outfile_clicks, driver=output_driver, epsg=output_epsg_code,
                          task_runs=task_runs_json, overwrite=overwrite_mode)
        except IOError, e:
            print(e)
            return 1
    if outfile_wellpads:
        print("Creating wellpads ...")
        try:
            create_wellpads(outfile=outfile_wellpads, driver=output_driver, epsg=output_epsg_code,
                            tasks=tasks_json, overwrite=overwrite_mode)
        except IOError, e:
            print(e)
            return 1

    #/* ======================================================================= */#
    #/*     Cleanup
    #/* ======================================================================= */#

    # Success
    print("")  # Required for formatting due to progress printers
    print("Done.")

    return 0


#/* ======================================================================= */#
#/*     Commandline Execution
#/* ======================================================================= */#

if __name__ == '__main__':

    # Didn't get enough arguments - print usage and exit
    if len(sys.argv) is 1:
        sys.exit(print_usage())

    # Got enough arguments - give sys.argv[1:] to main()
    else:
        sys.exit(main(sys.argv[1:]))
