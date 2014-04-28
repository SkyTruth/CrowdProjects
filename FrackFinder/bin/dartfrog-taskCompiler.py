#!/usr/bin/env python


"""
Compile disparate DartFrog tasks into a single cohesive dataset
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
__release__ = '2014/04/28'
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


def get_locations(tasks):

    """
    Get a list of unique locations from a set of tasks
    """

    output_set = []
    for task in tasks:
        lat = str(task['info']['latitude'])
        lng = str(task['info']['longitude'])
        year = str(task['info']['year'])
        location = lat + lng + '---' + year
        if location not in output_set:
            output_set.append(location)

    return output_set


def main(args):

    """
    Main routine
    """

    global DEBUG

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

    # Containers for storing input and output files
    output_csv = None
    public_tasks = None
    public_task_runs = None
    first_internal_tasks = None
    first_internal_task_runs = None
    final_internal_tasks = None
    final_internal_task_runs = None
    sweeper_tasks = None
    sweeper_task_runs = None

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

        # Catch errors
        elif arg == '':
            pass
        else:
            print("ERROR: Invalid argument: %s" % arg)
            arg_error = True

    # == Validate Parameters == #

    # Check make sure files do/don't exist and that all parameters are appropriate
    bail = False
    if arg_error:
        print("ERROR: Did not successfully parse arguments")
        bail = True
    if output_csv is None:
        print("ERROR: No output CSV supplied")
        bail = True
    else:
        if isfile(output_csv):
            print("ERROR: Output CSV exists: %s" % output_csv)
            bail = True
    if public_tasks is None or not os.access(public_tasks, os.R_OK):
        print("ERROR: Can't access public task file: %s" % public_tasks)
        bail = True
    if public_task_runs is None or not os.access(public_task_runs, os.R_OK):
        print("ERROR: Can't access public task run file: %s" % public_task_runs)
        bail = True
    if first_internal_tasks is None or not os.access(first_internal_tasks, os.R_OK):
        print("ERROR: Can't access first internal task file: %s" % first_internal_tasks)
        bail = True
    if first_internal_task_runs is None or not os.access(first_internal_task_runs, os.R_OK):
        print("ERROR: Can't access first internal task run file: %s" % first_internal_task_runs)
        bail = True
    if final_internal_tasks is None or not os.access(final_internal_tasks, os.R_OK):
        print("ERROR: Can't access final internal tasks: %s" % final_internal_tasks)
        bail = True
    if final_internal_task_runs is None or not os.access(final_internal_task_runs, os.R_OK):
        print("ERROR: Can't access final internal task runs: %s" % final_internal_task_runs)
        bail = True
    if sweeper_tasks is None or not os.access(sweeper_tasks, os.R_OK):
        print("ERROR: Can't access sweeper tasks: %s" % sweeper_tasks)
        bail = True
    if sweeper_task_runs is None or not os.access(sweeper_task_runs, os.R_OK):
        print("ERROR: Can't access sweeper task runs: %s" % sweeper_task_runs)
        bail = True
    if bail:
        return 1

    # == Load Data == #

    # Load public task.json and task_run.json
    print("Loading: %s" % public_tasks)
    with open(public_tasks, 'r') as f:
        public_tasks = json.load(f)
    print("Loading: %s" % public_task_runs)
    with open(public_task_runs, 'r') as f:
        public_task_runs = json.load(f)
    print("Loading: %s" % first_internal_tasks)
    with open(first_internal_tasks, 'r') as f:
        first_internal_tasks = json.load(f)
    print("Loading: %s" % first_internal_task_runs)
    with open(first_internal_task_runs, 'r') as f:
        first_internal_task_runs = json.load(f)
    print("Loading: %s" % final_internal_tasks)
    with open(final_internal_tasks, 'r') as f:
        final_internal_tasks = json.load(f)
    print("Loading: %s" % final_internal_task_runs)
    with open(final_internal_task_runs, 'r') as f:
        final_internal_task_runs = json.load(f)
    print("Loading: %s" % sweeper_tasks)
    with open(sweeper_tasks, 'r') as f:
        sweeper_tasks = json.load(f)
    print("Loading: %s" % sweeper_task_runs)
    with open(sweeper_task_runs, 'r') as f:
        sweeper_task_runs = json.load(f)


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
        initial_task_grab = [['id', 'id', str],
                             ['latitude', 'latitude', str],
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
