#!/usr/bin/env python


# See global __license__ variable for license information


"""
Convert a FrackFinder JSON export to a shapefile
containing 1 point per pond and aggregated response
metrics.
"""


import os
import sys
import json
import inspect
from os.path import isfile
from os.path import basename
import ogr
import osr


# Global parameters
DEBUG = False


# Build information
__author__ = 'Kevin Wurster'
__copyright__ = 'Copyright (c) 2014, SkyTruth'
__version__ = '0.1'
__release__ = '2014/04/07'
__docname__ = basename(inspect.getfile(inspect.currentframe()))
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


def pdebug(message):
    """
    Easily handle printing debug information
    """
    global DEBUG
    if DEBUG is True:
        print(message)


def print_usage():
    """
    Command line usage information
    """
    print("")
    print("Usage: %s [options] task.json task_run.json outfile.shp" % __docname__)
    print("")
    print("Options:")
    print("  --help-info -> Print out a list of help related flags")
    print("  --of=driver -> Output driver name/file type - default='ESRI Shapefile'")
    print("  --epsg=int  -> EPSG code for coordinates in task.json - default=4326")
    print("")
    return 1


def print_license():
    """
    Print out license information
    """
    print('\n' + __license__ + '\n')
    return 1


def print_help():
    """
    Detailed help information
    """
    print("")
    print("%s Detailed Help" % __docname__)
    print("--------------" + "-" * len(__docname__))
    print("PyBossa exports tasks in two ways: task.json and task_run.json")
    print("This utility looks at each task in task.json and sifts through")
    print("its matching task_run.json to calculate a variety of metrics,")
    print("like how many times the task was shown, how many times the crowd,")
    print("how many times the crowd picked each possible answer, and how")
    print("confident the crowd was in its decision.")
    print("")
    print("It is possible for the crowd to be split and pick two different")
    print("choices an equal number of times.  The output for these cases")
    print("is pipe delimited.")
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


def get_crowd_selection(selection_count, selection_map):
    """
    Figure out what the crowd actually selected
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


def get_crowd_selection_counts(input_id, task_runs_json_object):
    """
    Figure out how many times the crowd selected each option
    """
    counts = {'n_frk_res': 0,
              'n_unk_res': 0,
              'n_oth_res': 0,
              'ERROR': 0}
    for task_run in task_runs_json_object:
        if input_id == task_run['task_id']:
            try:
                selection = task_run['info']['selection']
            except KeyError:
                selection = 'ERROR'
            if selection == 'fracking':
                counts['n_frk_res'] += 1
            elif selection == 'unknown':
                counts['n_unk_res'] += 1
            elif selection == 'other':
                counts['n_oth_res'] += 1
            else:
                counts['ERROR'] += 1
    return counts


def get_percent_crowd_agreement(crowd_selection, selection_counts, total_responses, map_selection_field,
                                error_val=None):
    """
    Figure out how well the crowd agreed and if two answers tied, figure out the agreement for both
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


def main(args):

    """
    Main routine
    """

    global DEBUG

    # Set defaults and cache containers
    tasks_file = None
    task_runs_file = None
    outfile = None
    outfile_driver = 'ESRI Shapefile'
    outfile_epsg_code = 4326

    # Map field names to selections
    map_field_to_selection = {'n_frk_res': 'fracking',
                              'n_oth_res': 'other',
                              'n_unk_res': 'unknown',
                              'ERROR': 'ERROR'}

    # Map selections to field names
    map_selection_to_field = {'fracking': 'n_frk_res',
                              'other': 'n_oth_res',
                              'unknown': 'n_unk_res',
                              'ERROR': 'ERROR'}

    # Parse arguments
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

        # Outfile specific options
        elif '--of=' in arg:
            outfile_driver = arg.split('=', 1)[1]
        elif '--epsg=' in arg:
            outfile_epsg_code = int(arg.split('=', 1)[1])

        # Additional options
        elif arg == '--debug':
            DEBUG = True

        # These are positional arguments
        else:
            if tasks_file is None:
                tasks_file = arg
            elif task_runs_file is None:
                task_runs_file = arg
            elif outfile is None:
                outfile = arg

            # Unrecognized options
            else:
                print("ERROR: Invalid argument: %s" % arg)
                arg_error = True

    # == Validate Parameters == #

    # Check make sure files do/don't exist and that all parameters are appropriate
    bail = False
    if arg_error:
        print("ERROR: Did not successfully parse arguments")
        bail = True
    if tasks_file is None or not isfile(tasks_file) or not os.access(tasks_file, os.R_OK):
        print("ERROR: Can't access task file: %s" % str(tasks_file))
        bail = True
    if task_runs_file is None or not isfile(task_runs_file) or not os.access(task_runs_file, os.R_OK):
        print("ERROR: Can't access task run file: %s" % str(task_runs_file))
        bail = True
    if outfile is None:
        print("ERROR: No outfile supplied")
        bail = True
    else:
        if isfile(outfile):
            print("ERROR: Outfile exists: %s" % outfile)
            bail = True
    if not isinstance(outfile_epsg_code, int):
        print("ERROR: EPSG code must be an integer: %s" % str(outfile_epsg_code))
        bail = True
    if bail:
        return 1

    # == Load Data == #

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

    # == Create Output File == #

    # Get driver
    print("Creating output file...")
    driver = ogr.GetDriverByName(outfile_driver)
    data_source = driver.CreateDataSource(outfile)

    # Define SRS
    print("Defining SRS...")
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(outfile_epsg_code)

    # Create layer
    print("Creating layer...")
    layer_name = basename(outfile).split('.')
    layer_name = ''.join(layer_name[:len(layer_name) - 1])
    layer = data_source.CreateLayer(layer_name, srs, ogr.wkbPoint)

    # Define fields
    print("Defining fields...")
    fields_definitions = (('id', 10, ogr.OFTInteger),
                          ('site_id', 254, ogr.OFTString),
                          ('wms_url', 254, ogr.OFTString),
                          ('county', 254, ogr.OFTString),
                          ('year', 10, ogr.OFTInteger),
                          ('location', 254, ogr.OFTString),
                          ('n_unk_res', 10, ogr.OFTInteger),
                          ('n_frk_res', 10, ogr.OFTInteger),
                          ('n_oth_res', 10, ogr.OFTInteger),
                          ('n_tot_res', 10, ogr.OFTInteger),
                          ('crowd_sel', 254, ogr.OFTString),
                          ('qaqc', 254, ogr.OFTString),
                          ('p_crd_a', 10, ogr.OFTReal),
                          ('p_s_crd_a', 254, ogr.OFTString))

    # Create fields
    for field in fields_definitions:
        field_name = field[0]
        field_width = field[1]
        field_type = field[2]
        print("  " + field_name)
        field_object = ogr.FieldDefn(field_name, field_type)
        field_object.SetWidth(field_width)
        layer.CreateField(field_object)

    # == Examine Task.json File == #

    # Loop through all task.json tasks
    len_tasks_json = len(tasks_json)
    i = 0
    print("Analyzing tasks...")
    for task in tasks_json:

        # Print some debug stuff
        i += 1
        pdebug("Processing task %s of %s" % (str(i), str(len_tasks_json)))

        # Cache some information
        input_task_id = task['id']
        task_location = ''.join([str(task['info']['latitude']), str(task['info']['longitude']),
                                 '---', str(task['info']['year'])])

        # Get initial set of attributes from task body
        # First value in the tuple goes into task_attributes, and second references the info block within the task
        # The third value in the tuple is the type object to be used
        task_attributes = {'location': task_location}
        initial_task_grab = [('id', 'id', str),
                             ('latitude', 'latitude', str),
                             ('longitude', 'longitude', str),
                             ('wms_url', 'url', str),
                             ('county', 'county', str),
                             ('site_id', 'SiteID', str),
                             ('year', 'year', int)]
        for attributes in initial_task_grab:
            attribute_name = attributes[0]
            info_reference = attributes[1]
            type_caster = attributes[2]
            try:
                task_attributes[attribute_name] = type_caster(task['info'][info_reference])
            except (TypeError, KeyError):
                task_attributes[attributes[0]] = None

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

        # Update user
        pdebug("  wms_url   = %s" % task_attributes['wms_url'][:40] + ' ...(truncated...)')
        pdebug("  latitude  = %s" % str(task_attributes['latitude']))
        pdebug("  longitude = %s" % str(task_attributes['longitude']))
        pdebug("  id        = %s" % task_attributes['id'])
        pdebug("  site_id   = %s" % task_attributes['site_id'])
        pdebug("  county    = %s" % task_attributes['county'])
        pdebug("  year      = %s" % str(task_attributes['year']))
        pdebug("  location  = %s" % task_attributes['location'])
        pdebug("  n_unk_res = %s" % str(task_attributes['n_unk_res']))
        pdebug("  n_frk_res = %s" % str(task_attributes['n_frk_res']))
        pdebug("  n_oth_res = %s" % str(task_attributes['n_oth_res']))
        pdebug("  n_tot_res = %s" % str(task_attributes['n_tot_res']))
        pdebug("  crowd_sel = %s" % task_attributes['crowd_sel'])
        #pdebug("  qaqc      = %s" % task_attributes['qaqc'])  # Currently a manual process so it has no key to populate
        pdebug("  p_crd_a   = %s" % str(task_attributes['p_crd_a']))
        pdebug("  p_s_crd_a = %s" % str(task_attributes['p_s_crd_a']))
        pdebug("")

        # Create the feature
        feature = ogr.Feature(layer.GetLayerDefn())
        field_values = [('id', task_attributes['id']),
                        ('site_id', task_attributes['site_id']),
                        ('wms_url', task_attributes['wms_url']),
                        ('county', task_attributes['county']),
                        ('year', task_attributes['year']),
                        ('location', task_attributes['location']),
                        ('n_unk_res', task_attributes['n_unk_res']),
                        ('n_frk_res', task_attributes['n_frk_res']),
                        ('n_oth_res', task_attributes['n_oth_res']),
                        ('n_tot_res', task_attributes['n_tot_res']),
                        ('crowd_sel', task_attributes['crowd_sel']),
                        ('p_crd_a', task_attributes['p_crd_a']),
                        ('p_s_crd_a', task_attributes['p_s_crd_a'])]
        for field, value in field_values:
            feature.SetField(field, value)
        wkt = "POINT(%f %f)" % (float(task_attributes['longitude']), float(task_attributes['latitude']))
        point = ogr.CreateGeometryFromWkt(wkt)
        feature.SetGeometry(point)
        layer.CreateFeature(feature)

        # Cleanup
        feature.Destroy()

    # Cleanup shapefile
    data_source.Destroy()

    # Update user
    print("Done.")

    # Everything executed properly
    return 0

if __name__ == '__main__':
    if len(sys.argv) is 1:
        sys.exit(print_usage())
    else:
        sys.exit(main(sys.argv[1:]))
