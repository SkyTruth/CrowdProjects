#!/usr/bin/env python


# This document is part of CrowdProjects
# https://github.com/skytruth/CrowdProjects


# =========================================================================== #
#
#  Copyright (c) 2014, SkyTruth
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer.
#
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
#  * Neither the name of the {organization} nor the names of its
#  contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#
# =========================================================================== #


"""
Convert a FrackFinder Tadpole 2013 JSON export to a shapefile
containing 1 point per input task and aggregated crowd response
metrics.
"""

from __future__ import print_function

import os
import sys
import json
from os.path import *
from pprint import pprint
try:
    from osgeo import ogr
    from osgeo import osr
except ImportError:
    import ogr
    import osr


#/* ======================================================================= */#
#/*     Build Information
#/* ======================================================================= */#

__author__ = 'Kevin Wurster'
__version__ = '0.1'
__release__ = '2014/06/11'
__docname__ = basename(__file__)
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


#/* ======================================================================= */#
#/*     Define print_usage() function
#/* ======================================================================= */#

def print_usage():

    """
    Command line usage information

    :return: 1 for exit code purposes
    :rtype: int
    """

    print("""
Usage: %s [options] task.json task_run.json outfile.shp

Options:
  --class=str -> Add a field containing a value, or use %%str to get a field from the JSON
  --help-info -> Print out a list of help related flags
  --of=driver -> Output driver name/file type - default='ESRI Shapefile'
  --epsg=int  -> EPSG code for coordinates in task.json - default='4326'
  --overwrite -> Overwrite the output file
""" % __docname__)
    return 1


#/* ======================================================================= */#
#/*     Define print_license() function
#/* ======================================================================= */#

def print_license():

    """
    Print out license information

    :return: 1 for exit code purposes
    :rtype: int
    """

    print(__license__)

    return 1


#/* ======================================================================= */#
#/*     Define print_help() function
#/* ======================================================================= */#

def print_help():

    """
    Detailed help information

    :return: 1 for exit code purposes
    :rtype: int
    """

    print("""
Help: {0}
------{1}

IMPORTANT NOTE: There is a {0} for both the 2005-2010 data AND
                2013 data.  While the names are the same, THIS utility has
                been modified to be 2013 data specific.  Mixing utilities
                and data across years may produce unexpected results.

PyBossa exports tasks in two ways: task.json and task_run.json  This utility
looks at each task in task.json and sifts through its matching task_run.json
to calculate a variety of metrics, like how many times the task was shown,
how many times the crowd, how many times the crowd picked each possible answer,
and how confident the crowd was in its decision.

It is possible for the crowd to be split and pick two different choices an
equal number of times.  The output for these cases is pipe delimited.
    """.format(__docname__, '-' * len(__docname__)))

    return 1


#/* ======================================================================= */#
#/*     Define print_help_info() function
#/* ======================================================================= */#

def print_help_info():

    """
    Print a list of help related flags

    :return: 1 for exit code purposes
    :rtype: int
    """

    print("""
Help flags:
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
    Print script version information

    :return: 1 for exit code purposes
    :rtype: int
    """

    print("""
%s version %s - released %s
    """ % (__docname__, __version__, __release__))

    return 1


#/* ======================================================================= */#
#/*     Define get_crowd_selection() function
#/* ======================================================================= */#

def get_crowd_selection(selection_count, selection_map):

    """
    Figure out what the crowd actually selected

    :param selection_count: the number of responses for each selection
    :type selection_count: dict
    :param selection_map: maps output file fields to selections
    :type selection_map: dict

    :return: the crowd's selection for a given group of selections or None
    :rtype: str|None
    """

    # Cache containers
    crowd_selection = 'NONE'

    # Figure out what the maximum number of selections was
    max_selection = max(selection_count.values())

    # Build the crowd_selection
    if max_selection is 0:
        crowd_selection = None
    else:
        for selection, count in selection_count.iteritems():
            if count is max_selection:
                if crowd_selection == 'NONE':
                    crowd_selection = selection_map[selection]
                else:
                    crowd_selection += '|' + selection_map[selection]

    # Return to user
    return crowd_selection


#/* ======================================================================= */#
#/*     Define get_crowd_selection_counts() function
#/* ======================================================================= */#

def get_crowd_selection_counts(input_id, task_runs_json_object):

    """
    Figure out how many times the crowd selected each option

    :param input_id: the id for a given task
    :type input_id: int
    :param task_runs_json_object: all of the input task_runs from json.load(open('task_run.json'))
    :type task_runs_json_object: list

    :return: number of responses for each selection
    :rtype: dict
    """

    counts = {'n_nop_res': 0,
              'n_unk_res': 0,
              'n_pad_res': 0,
              'ERROR': 0}
    for task_run in task_runs_json_object:
        if input_id == task_run['task_id']:
            try:
                selection = task_run['info']['selection']
            except KeyError:
                selection = 'ERROR'
            if selection == 'nopad':
                counts['n_nop_res'] += 1
            elif selection == 'unknown':
                counts['n_unk_res'] += 1
            elif selection == 'pad':
                counts['n_pad_res'] += 1
            else:
                counts['ERROR'] += 1
    return counts


#/* ======================================================================= */#
#/*     Define get_percent_crowd_agreement() function
#/* ======================================================================= */#

def get_percent_crowd_agreement(crowd_selection, selection_counts, total_responses, map_selection_field,
                                error_val=None):

    """
    Figure out how well the crowd agreed and if two answers tied, figure out the agreement for both

    :param crowd_selection: the winning selection for a given task
    :type crowd_selection: str|None
    :param selection_counts: number of responses for each count
    :type selection_counts: dict
    :param total_responses: total number of responses
    :type total_responses: int
    :param map_selection_field: maps selections to output file field names
    :type map_selection_field: dict
    :param error_val: set crowd agreement to this value if any errors are encountered
    :type error_val: str|None

    :return: percent crowd agreement and percent crowd agreement
    :rtype: dict
    """

    # Compute crowd agreement
    # The try/except blocks are for situations where tasks have never been viewed, which yields zero total_responses
    per_crowd_agreement = None
    split_per_crowd_agreement = None

    # Make sure the crowd actually made a selection
    if crowd_selection is None:
        per_crowd_agreement = None
        split_per_crowd_agreement = None
    elif total_responses is 0:
        per_crowd_agreement = error_val
        split_per_crowd_agreement = error_val
    else:
        if '|' not in crowd_selection:
            try:
                per_crowd_agreement = int(selection_counts[map_selection_field[crowd_selection]] * 100 / total_responses)
            except ZeroDivisionError:
                per_crowd_agreement = error_val
        else:

            # Compute percent agreement for each split response
            for selection in crowd_selection.split('|'):
                field_name = map_selection_field[selection]
                selection_count = selection_counts[field_name]
                try:
                    per_crowd_agreement = int(selection_count * 100 / total_responses)
                except ZeroDivisionError:
                    per_crowd_agreement = error_val
                if split_per_crowd_agreement is None:
                    split_per_crowd_agreement = str(per_crowd_agreement)
                else:
                    split_per_crowd_agreement += '|' + str(per_crowd_agreement)

            # Make sure the percent crowd agreement field is None when there is a split response
            per_crowd_agreement = error_val
    return {'p_crd_a': per_crowd_agreement, 'p_s_crd_a': split_per_crowd_agreement}


#/* ======================================================================= */#
#/*     Define main() function
#/* ======================================================================= */#

def main(args):

    """
    Main routine

    :param args: arguments from the commandline (sys.argv[1:] in order to drop the script name)
    :type args: list

    :return: 0 on success and 1 on error
    :rtype: int
    """

    #/* ======================================================================= */#
    #/*     Defaults
    #/* ======================================================================= */#

    # OGR defaults
    outfile_driver = 'ESRI Shapefile'
    outfile_epsg_code = 4326

    # Output file
    overwrite_outfile = False

    #/* ======================================================================= */#
    #/*     Containers
    #/* ======================================================================= */#

    # Input/output files
    classification = None
    tasks_file = None
    task_runs_file = None
    outfile = None

    # Map field names to selections
    map_field_to_selection = {'n_nop_res': 'nopad',
                              'n_unk_res': 'unknown',
                              'n_pad_res': 'pad',
                              'ERROR': 'ERROR'}

    # Map selections to field names
    map_selection_to_field = {'nopad': 'n_nop_res',
                              'unknown': 'n_unk_res',
                              'pad': 'n_pad_res',
                              'ERROR': 'ERROR'}

    #/* ======================================================================= */#
    #/*     Defaults
    #/* ======================================================================= */#

    arg_error = False
    for arg in args:

        # Help arguments
        if arg in ('--license', '-license'):
            return print_license()
        elif arg in ('--usage', '-usage'):
            return print_usage()
        elif arg in ('--version', '-version'):
            return print_version()
        elif arg in ('--help', '-help'):
            return print_help()
        elif arg in ('--help-info', '-help-info', '--helpinfo', '--helpinfo'):
            return print_help_info()

        # OGR configuration
        elif '--of=' in arg:
            outfile_driver = arg.split('=', 1)[1]
        elif '--epsg=' in arg:
            outfile_epsg_code = arg.split('=', 1)[1]

        # Processing options
        elif '--class=' in arg:
            classification = arg.split('=', 1)[1]

        # Additional options
        elif arg == '--overwrite':
            overwrite_outfile = True

        # Positional arguments and errors
        else:

            # Catch task.json file
            if tasks_file is None:
                tasks_file = arg

            # Catch task_run.json file
            elif task_runs_file is None:
                task_runs_file = arg

            # Catch output file
            elif outfile is None:
                outfile = arg

            # Catch unrecognized arguments
            else:
                print("ERROR: Invalid argument: %s" % arg)
                arg_error = True

    #/* ======================================================================= */#
    #/*     Validate Parameters
    #/* ======================================================================= */#

    bail = False

    # Check arguments
    if arg_error:
        print("ERROR: Did not successfully parse arguments")
        bail = True

    # Check input task.json file
    if tasks_file is None:
        bail = True
        print("ERROR: Need a task file")
    elif not isfile(tasks_file) or not os.access(tasks_file, os.R_OK):
        bail = True
        print("ERROR: Can't access file: %s" % tasks_file)

    # Check input task_run.json file
    if task_runs_file is None:
        bail = True
        print("ERROR: Need a task run file")
    elif not isfile(task_runs_file) or not os.access(task_runs_file, os.R_OK):
        bail = True
        print("ERROR: Can't access task run file:" % task_runs_file)

    # Check output file
    if outfile is None:
        bail = True
        print("ERROR: Need an output file")
    elif not isdir(dirname(outfile)) and not os.access(dirname(outfile), os.W_OK):
        bail = True
        print("ERROR: Need write permission: %s" % dirname(outfile))
    elif not overwrite_outfile and isfile(outfile):
        bail = True
        print("ERROR: Output file exists and overwrite=%s: %s" % (str(overwrite_outfile), outfile))

    # Check EPSG code
    try:
        outfile_epsg_code = int(outfile_epsg_code)
    except ValueError:
        bail = True
        print("ERROR: Invalid EPSG code - must be an int: %s" % str(outfile_epsg_code))

    if bail:
        return 1

    #/* ======================================================================= */#
    #/*     Load JSON Data
    #/* ======================================================================= */#

    # Load task.json file into a JSON object
    print("Loading task file...")
    with open(tasks_file, 'r') as f:
        tasks_json = json.load(f)
    print("Found %s items" % str(len(tasks_json)))

    # Load task_run.json file into a JSON object
    print("Loading task run file...")
    with open(task_runs_file, 'r') as f:
        task_runs_json = json.load(f)
    print("Found %s items" % str(len(task_runs_json)))

    #/* ======================================================================= */#
    #/*     Create Output OGR Datasource/Layer/Definitions/etc.
    #/* ======================================================================= */#

    # Get driver and make sure its valid
    driver = ogr.GetDriverByName(outfile_driver)
    if driver is None:
        print("ERROR: Invalid OGR driver: %s" % outfile_driver)
        return 1

    # Overwrite output file if it exists then create new datasource
    if isfile(outfile):
        print("Overwriting output file: %s" % outfile)
        driver.DeleteDataSource(outfile)
    print("Creating output file: %s" % outfile)
    data_source = driver.CreateDataSource(outfile)

    # Define SRS
    print("Defining SRS ...")
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(outfile_epsg_code)

    # Create layer
    print("Creating layer ...")
    layer_name = basename(outfile).split('.')
    layer_name = ''.join(layer_name[:len(layer_name) - 1])
    layer = data_source.CreateLayer(layer_name, srs, ogr.wkbPoint)

    # Define fields
    print("Defining fields ...")
    fields_definitions = [('id', 10, ogr.OFTInteger),
                          ('site_id', 254, ogr.OFTString),
                          ('wms_url', 254, ogr.OFTString),
                          ('wms_id', 254, ogr.OFTString),
                          ('wms_v', 254, ogr.OFTString),
                          ('county', 254, ogr.OFTString),
                          ('state', 254, ogr.OFTString),
                          ('year', 10, ogr.OFTInteger),
                          ('location', 254, ogr.OFTString),
                          ('n_unk_res', 10, ogr.OFTInteger),
                          ('n_nop_res', 10, ogr.OFTInteger),
                          ('n_pad_res', 10, ogr.OFTInteger),
                          ('n_tot_res', 10, ogr.OFTInteger),
                          ('crowd_sel', 254, ogr.OFTString),
                          ('qaqc', 254, ogr.OFTString),
                          ('p_crd_a', 10, ogr.OFTReal),
                          ('p_s_crd_a', 254, ogr.OFTString)]

    # Add extra fields
    if classification is not None:
        fields_definitions.append(('class', 254, ogr.OFTString))

    # Create fields
    for field in fields_definitions:
        field_name = field[0]
        field_width = field[1]
        field_type = field[2]
        print("  " + field_name)
        field_object = ogr.FieldDefn(field_name, field_type)
        field_object.SetWidth(field_width)
        layer.CreateField(field_object)

    #/* ======================================================================= */#
    #/*     Analyze task.json Content
    #/* ======================================================================= */#

    # Loop through all task.json tasks
    len_tasks_json = len(tasks_json)
    i = 0
    print("Analyzing tasks ...")
    for task in tasks_json:

        # Update user
        i += 1
        sys.stdout.write("\r\x1b[K" + "  %s/%s" % (str(i), str(len_tasks_json)))
        sys.stdout.flush()

        # Cache some information
        input_task_id = task['id']
        task_location = ''.join([str(task['info']['latitude']), str(task['info']['longitude']),
                                 '---', str(task['info']['year'])])

        # Get initial set of attributes from task body
        # First value in the tuple goes into task_attributes, and second references the info block within the task
        # The third value in the tuple is the type object to be used
        task_attributes = {'location': task_location}
        initial_task_grab = [('id', 'id', int),
                             ('latitude', 'latitude', str),
                             ('longitude', 'longitude', str),
                             ('wms_url', 'url', str),
                             ('county', 'county', str),
                             ('state', 'state', str),
                             ('site_id', 'siteID', str),
                             ('year', 'year', int)]

        for attributes in initial_task_grab:
            attribute_name = attributes[0]
            info_reference = attributes[1]
            type_caster = attributes[2]
            try:
                task_attributes[attribute_name] = type_caster(task['info'][info_reference])
            except (TypeError, KeyError):
                task_attributes[attributes[0]] = None

        # Get the WMS version
        task_attributes['wms_v'] = str(task['info']['options']['version'])
        task_attributes['wms_id'] = str(task['info']['options']['layers'])

        # Get the crowd selection counts
        crowd_selection_counts = get_crowd_selection_counts(input_task_id, task_runs_json)
        task_attributes = dict(task_attributes.items() + crowd_selection_counts.items())

        # Figure out what the crowd actually selected and the total number of responses
        n_tot_res = int(sum(crowd_selection_counts.values()))
        task_attributes['n_tot_res'] = n_tot_res
        crowd_selection = get_crowd_selection(crowd_selection_counts, map_field_to_selection)
        task_attributes['crowd_sel'] = crowd_selection

        # Get crowd agreement levels
        task_attributes = dict(task_attributes.items()
                               + get_percent_crowd_agreement(task_attributes['crowd_sel'], crowd_selection_counts,
                                                             n_tot_res, map_selection_to_field).items())

        # Create the feature
        feature = ogr.Feature(layer.GetLayerDefn())
        field_values = [('id', task_attributes['id']),
                        ('site_id', task_attributes['site_id']),
                        ('wms_url', task_attributes['wms_url']),
                        ('wms_id', task_attributes['wms_id']),
                        ('wms_v', task_attributes['wms_v']),
                        ('county', task_attributes['county']),
                        ('state', task_attributes['state']),
                        ('year', task_attributes['year']),
                        ('location', task_attributes['location']),
                        ('n_unk_res', task_attributes['n_unk_res']),
                        ('n_nop_res', task_attributes['n_nop_res']),
                        ('n_pad_res', task_attributes['n_pad_res']),
                        ('n_tot_res', task_attributes['n_tot_res']),
                        ('crowd_sel', task_attributes['crowd_sel']),
                        ('p_crd_a', task_attributes['p_crd_a']),
                        ('p_s_crd_a', task_attributes['p_s_crd_a'])]

        # Set values for additional fields
        if classification is not None:
            if classification[0] == '%':
                field_values.append(('class', str(task[classification[1:]])))
            else:
                field_values.append(('class', str(classification)))

        # Populate fields
        for field, value in field_values:
            feature.SetField(field, value)
        wkt = "POINT(%f %f)" % (float(task_attributes['longitude']), float(task_attributes['latitude']))
        point = ogr.CreateGeometryFromWkt(wkt)
        feature.SetGeometry(point)
        layer.CreateFeature(feature)

        # Cleanup feature
        feature = None

    #/* ======================================================================= */#
    #/*     Cleanup
    #/* ======================================================================= */#

    # Destroy OGR objects
    data_source = None
    layer = None

    # Success
    print("  - Done.")
    return 0


#/* ======================================================================= */#
#/*     Commandline Execution
#/* ======================================================================= */#

if __name__ == '__main__':

    # Not enough arguments - print usage
    if len(sys.argv) is 1:
        sys.exit(print_usage())

    # Got enough arguments - give all but the first to the main() function
    else:
        sys.exit(main(sys.argv[1:]))
