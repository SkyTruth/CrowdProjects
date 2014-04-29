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
from pprint import pprint


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
    print("Usage: %s --help-info [options]" % __docname__)
    print("")
    print("Required:")
    print("    --pt=str    -> Public task.json")
    print("    --ptr=str   -> Public task_run.json")
    print("    --fit=str   -> First Internal task.json")
    print("    --fitr=str  -> First Internal task_run.json")
    print("    --fint=str  -> Final Internal task.json")
    print("    --fintr=str -> Final Internal task_run.json")
    print("    --st=str    -> Sweeper task.json")
    print("    --str=str   -> Sweeper task_run.json")
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
              'n_oth_res': 0}
    #counts = {'n_frk_res': 0,
    #          'n_unk_res': 0,
    #          'n_oth_res': 0,
    #          'ERROR': 0}
    for task_run in task_runs_json_object:
        if input_id == task_run['task_id']:
            try:
                selection = task_run['info']['selection']
            except KeyError:
                #selection = 'ERROR'
                pass
            if selection == 'fracking':
                counts['n_frk_res'] += 1
            elif selection == 'unknown':
                counts['n_unk_res'] += 1
            elif selection == 'other':
                counts['n_oth_res'] += 1
            else:
                print("WARNING: Bad selection for task ID: %s" % str(input_id))
                #counts['ERROR'] += 1
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


def get_task_runs(task_id, task_runs_json):

    """
    Search through all task runs to get the set matching the input task id
    """

    output_list = []
    for tr in task_runs_json:
        if task_id == tr['task_id']:
            output_list.append(tr)

    return output_list


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
    compiled_output_csv = None
    scrubbed_output_csv = None
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

        # Public JSON files
        elif '--pt=' in arg:
            public_tasks = arg.split('=', 1)[1]
        elif '--ptr=' in arg:
            public_task_runs = arg.split('=', 1)[1]

        # First internal JSON files
        elif '--fit=' in arg:
            first_internal_tasks = arg.split('=', 1)[1]
        elif '--fitr=' in arg:
            first_internal_task_runs = arg.split('=', 1)[1]

        # Final internal JSON files
        elif '--fint=' in arg:
            final_internal_tasks = arg.split('=', 1)[1]
        elif '--fintr=' in arg:
            final_internal_task_runs = arg.split('=', 1)[1]

        # Sweeper JSON files
        elif '--st=' in arg:
            sweeper_tasks = arg.split('=', 1)[1]
        elif '--str=' in arg:
            sweeper_task_runs = arg.split('=', 1)[1]

        # Compiled output CSV
        elif '--co=' in arg:
            compiled_output_csv = arg.split('=', 1)[1]

        # Scrubbed output CSV
        elif '--so=' in arg:
            scrubbed_output_csv = arg.split('=', 1)[1]




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
    if compiled_output_csv is None:
        print("ERROR: No compiled output CSV supplied")
        bail = True
    else:
        if isfile(compiled_output_csv):
            print("ERROR: Compiled output CSV exists: %s" % compiled_output_csv)
            bail = True
    if scrubbed_output_csv is None:
        print("ERROR: No scrubbed output CSV supplied")
        bail = True
    else:
        if isfile(scrubbed_output_csv):
            print("ERROR: Scrubbed output CSV exists: %s" % scrubbed_output_csv)
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

    # Public
    print("Loading public tasks: %s" % public_tasks)
    with open(public_tasks, 'r') as f:
        public_tasks = json.load(f)
    print("  %s" % str(len(public_tasks)))
    print("Loading public task runs: %s" % public_task_runs)
    with open(public_task_runs, 'r') as f:
        public_task_runs = json.load(f)
    print("  %s" % str(len(public_task_runs)))

    # First internal
    print("Loading first internal tasks: %s" % first_internal_tasks)
    with open(first_internal_tasks, 'r') as f:
        first_internal_tasks = json.load(f)
    print("  %s" % str(len(first_internal_tasks)))
    print("Loading first internal task runs: %s" % first_internal_task_runs)
    with open(first_internal_task_runs, 'r') as f:
        first_internal_task_runs = json.load(f)
    print("  %s" % str(len(first_internal_task_runs)))

    # Final internal
    print("Loading final internal tasks: %s" % final_internal_tasks)
    with open(final_internal_tasks, 'r') as f:
        final_internal_tasks = json.load(f)
    print("  %s" % str(len(final_internal_tasks)))
    print("Loading final internal task runs: %s" % final_internal_task_runs)
    with open(final_internal_task_runs, 'r') as f:
        final_internal_task_runs = json.load(f)
    print("  %s" % str(len(final_internal_task_runs)))

    # Sweeper
    print("Loading sweeper internal tasks: %s" % sweeper_tasks)
    with open(sweeper_tasks, 'r') as f:
        sweeper_tasks = json.load(f)
    print("  %s" % str(len(sweeper_tasks)))
    print("Loading sweeper internal task runs: %s" % sweeper_task_runs)
    with open(sweeper_task_runs, 'r') as f:
        sweeper_task_runs = json.load(f)
    print("  %s" % str(len(sweeper_task_runs)))

    # == Get a set of locations to analyze == #

    # Get list
    print("Getting list of unique locations...")
    location_list = get_locations(public_tasks)
    print("Found %s locations" % str(len(location_list)))
    stats_template = {'n_unk_res': None,
                      'n_frk_res': None,
                      'n_oth_res': None,
                      'n_tot_res': None,
                      'crowd_sel': None,
                      'p_crd_a': None,
                      'p_s_crd_a': None}
    location_template = {'latitude': None,
                         'longitude': None,
                         'year': None,
                         'wms_url': None,
                         'county': None,
                         'n_unk_res': None,
                         'n_frk_res': None,
                         'n_oth_res': None,
                         'n_tot_res': None,
                         'crowd_sel': None,
                         'comp_loc': None,
                         'p_crd_a': None,
                         'p_s_crd_a': None,
                         'public': stats_template.copy(),
                         'fi_intern': stats_template.copy(),
                         'fn_intern': stats_template.copy(),
                         'sw_intern': stats_template.copy()}
    locations = {}
    for location in location_list:
        locations[location] = location_template

    # == Analyze Public Tasks == #

    # Loop through tasks and collect public attributes
    print("Analyzing public tasks...")
    for task in public_tasks:

        # Cache important identifiers
        task_location = get_locations([task])[0]
        task_id = task['id']

        # Store the easy stuff first
        locations[task_location]['latitude'] = task['info']['latitude']
        locations[task_location]['longitude'] = task['info']['longitude']
        locations[task_location]['year'] = task['info']['year']
        locations[task_location]['wms_url'] = task['info']['url']
        locations[task_location]['county'] = task['info']['county']
        locations[task_location]['comp_loc'] = 'public'

        # Get selection counts
        task_stats = stats_template.copy()
        selection_counts = get_crowd_selection_counts(task_id, public_task_runs)
        total_responses = sum(selection_counts.values())
        crowd_selection = get_crowd_selection(selection_counts, map_field_to_selection)
        crowd_agreement = get_percent_crowd_agreement(crowd_selection, selection_counts,
                                                      len(get_task_runs(task_id, public_task_runs)),
                                                      map_selection_to_field)
        task_stats = dict(task_stats.items() + selection_counts.items())
        task_stats = dict(task_stats.items() + crowd_agreement.items())
        task_stats['n_tot_res'] = total_responses
        task_stats['crowd_sel'] = crowd_selection

        for key, val in task_stats.iteritems():
            locations[task_location][key] = val
            locations[task_location]['public'][key] = val


        pprint(locations[task_location])
        return 0









        response_counts = get_crowd_selection_counts(task_id, public_task_runs)
        stats_cache = response_counts


        content_cache['crowd_sel'] = get_crowd_selection_counts(task_id, public_task_runs)



        content_cache['p_crd_a'] = get_percent_crowd_agreement(response_counts['crowd_sel'], )
        for response, count in response_counts:
            locations[task_location][response] = count
            locations[task_location]['public'][response] = count

    # Success
    return 0


if __name__ == '__main__':
    if len(sys.argv) is 1:
        sys.exit(print_usage())
    else:
        sys.exit(main(sys.argv[1:]))
