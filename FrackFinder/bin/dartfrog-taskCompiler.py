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
        lat = str(round(task['info']['latitude'], 8))
        lng = str(round(task['info']['longitude'], 8))
        year = str(task['info']['year'])
        location = lat + lng + '---' + year
        output_set.append(location)

    return list(set(output_set))


def get_task_runs(task_id, task_runs_json):

    """
    Search through all task runs to get the set matching the input task id
    """

    output_list = []
    for tr in task_runs_json:
        if task_id == tr['task_id']:
            output_list.append(tr)

    return output_list


def load_json(input_file):

    """
    Load a JSON file into a JSON object
    """

    with open(input_file, 'r') as f:
        output_json = json.load(f)
    return output_json


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
    compiled_output_csv_file = None
    public_tasks_file = None
    public_task_runs_file = None
    first_internal_tasks_file = None
    first_internal_task_runs_file = None
    final_internal_tasks_file = None
    final_internal_task_runs_file = None
    sweeper_tasks_file = None
    sweeper_task_runs_file = None

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
            public_tasks_file = arg.split('=', 1)[1]
        elif '--ptr=' in arg:
            public_task_runs_file = arg.split('=', 1)[1]

        # First internal JSON files
        elif '--fit=' in arg:
            first_internal_tasks_file = arg.split('=', 1)[1]
        elif '--fitr=' in arg:
            first_internal_task_runs_file = arg.split('=', 1)[1]

        # Final internal JSON files
        elif '--fint=' in arg:
            final_internal_tasks_file = arg.split('=', 1)[1]
        elif '--fintr=' in arg:
            final_internal_task_runs_file = arg.split('=', 1)[1]

        # Sweeper JSON files
        elif '--st=' in arg:
            sweeper_tasks_file = arg.split('=', 1)[1]
        elif '--str=' in arg:
            sweeper_task_runs_file = arg.split('=', 1)[1]

        # Compiled output CSV
        elif '--co=' in arg:
            compiled_output_csv_file = arg.split('=', 1)[1]

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
    if compiled_output_csv_file is None:
        print("ERROR: No compiled output CSV supplied")
        bail = True
    else:
        if isfile(compiled_output_csv_file):
            print("ERROR: Compiled output CSV exists: %s" % compiled_output_csv_file)
            bail = True
    if public_tasks_file is None or not os.access(public_tasks_file, os.R_OK):
        print("ERROR: Can't access public task file: %s" % public_tasks_file)
        bail = True
    if public_task_runs_file is None or not os.access(public_task_runs_file, os.R_OK):
        print("ERROR: Can't access public task run file: %s" % public_task_runs_file)
        bail = True
    if first_internal_tasks_file is None or not os.access(first_internal_tasks_file, os.R_OK):
        print("ERROR: Can't access first internal task file: %s" % first_internal_tasks_file)
        bail = True
    if first_internal_task_runs_file is None or not os.access(first_internal_task_runs_file, os.R_OK):
        print("ERROR: Can't access first internal task run file: %s" % first_internal_task_runs_file)
        bail = True
    if final_internal_tasks_file is None or not os.access(final_internal_tasks_file, os.R_OK):
        print("ERROR: Can't access final internal tasks: %s" % final_internal_tasks_file)
        bail = True
    if final_internal_task_runs_file is None or not os.access(final_internal_task_runs_file, os.R_OK):
        print("ERROR: Can't access final internal task runs: %s" % final_internal_task_runs_file)
        bail = True
    if sweeper_tasks_file is None or not os.access(sweeper_tasks_file, os.R_OK):
        print("ERROR: Can't access sweeper tasks: %s" % sweeper_tasks_file)
        bail = True
    if sweeper_task_runs_file is None or not os.access(sweeper_task_runs_file, os.R_OK):
        print("ERROR: Can't access sweeper task runs: %s" % sweeper_task_runs_file)
        bail = True
    if bail:
        return 1

    # == Load Data == #

    # Public task.json
    print("Loading public tasks: %s" % public_tasks_file)
    public_tasks = load_json(public_tasks_file)
    print("  %s" % str(len(public_tasks)))

    # Public task_run.json
    print("Loading public task runs: %s" % public_task_runs_file)
    public_task_runs = load_json(public_task_runs_file)
    print("  %s" % str(len(public_task_runs)))

    # First internal task.json
    print("Loading first internal tasks: %s" % first_internal_tasks_file)
    first_internal_tasks = load_json(first_internal_tasks_file)
    print("  %s" % str(len(first_internal_tasks)))

    # First internal task_run.json
    print("Loading first internal task runs: %s" % first_internal_task_runs_file)
    first_internal_task_runs = load_json(first_internal_task_runs_file)
    print("  %s" % str(len(first_internal_task_runs)))

    # Final internal task.json
    print("Loading final internal tasks: %s" % final_internal_tasks_file)
    final_internal_tasks = load_json(final_internal_tasks_file)
    print("  %s" % str(len(final_internal_tasks)))

    # Final internal task_run.json
    print("Loading final internal task runs: %s" % final_internal_task_runs_file)
    final_internal_task_runs = load_json(final_internal_task_runs_file)
    print("  %s" % str(len(final_internal_task_runs)))

    # Sweeper task.json
    print("Loading sweeper internal tasks: %s" % sweeper_tasks_file)
    sweeper_tasks = load_json(sweeper_tasks_file)
    print("  %s" % str(len(sweeper_tasks)))

    # Sweeper task_run.json
    print("Loading sweeper internal task runs: %s" % sweeper_task_runs_file)
    sweeper_task_runs = load_json(sweeper_task_runs_file)
    print("  %s" % str(len(sweeper_task_runs)))

    # == Get a set of locations to analyze == #

    # Get list
    print("Getting list of unique locations...")
    location_list = get_locations(public_tasks)
    print("Found %s locations" % str(len(location_list)))

    # Make sure locations are all accounted for
    drop_locations = []
    v_error = False
    p_missing = 0
    fi_missing = 0
    fn_missing = 0
    s_missing = 0
    print("Validating public locations...")
    for task in public_tasks:
        location = get_locations([task])[0]
        if location not in location_list:
            drop_locations.append(location)
            p_missing += 1
            v_error = True
    print("Validating first internal locations...")
    for task in first_internal_tasks:
        location = get_locations([task])[0]
        if location not in location_list:
            drop_locations.append(location)
            fi_missing += 1
            v_error = True
    print("Validating final internal locations...")
    for task in final_internal_tasks:
        location = get_locations([task])[0]
        if location not in location_list:
            drop_locations.append(location)
            fn_missing += 1
            v_error = True
    print("Validating sweeper internal locations...")
    for task in sweeper_tasks:
        location = get_locations([task])[0]
        if location not in location_list:
            drop_locations.append(location)
            s_missing += 1
            v_error = True
    if v_error:
        print("  Missing Public: %s" % str(p_missing))
        print("  Missing First Internal: %s" % str(fi_missing))
        print("  Missing Final Internal: %s" % str(fn_missing))
        print("  Missing Sweeper: %s" % str(s_missing))

    # Convert the location list into a dictionary based on the templates below
    stats_template = {'n_unk_res': None,
                      'n_frk_res': None,
                      'n_oth_res': None,
                      'n_tot_res': None,
                      'crowd_sel': None,
                      'p_crd_a': None,
                      'p_s_crd_a': None}
    location_template = {'lat': None,
                         'lng': None,
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
        locations[location] = location_template.copy()

    # == Analyze Public Tasks == #

    # Loop through tasks and collect public attributes
    print("Analyzing public tasks...")
    i = 0
    tot_tasks = len(public_tasks)
    for task in public_tasks[:100]:

        # Update user
        i += 1
        sys.stdout.write("\r\x1b[K" + "  %s/%s" % (str(i), str(tot_tasks)))
        sys.stdout.flush()

        # Cache important identifiers
        task_location = get_locations([task])[0]
        task_id = task['id']

        # Make sure the task location is actually in the master list - if not, delete it
        if task_location not in locations:
            print("Dropped location: %s" % task_location)

        else:

            # Store the easy stuff first
            locations[task_location]['lat'] = task['info']['latitude']
            locations[task_location]['lng'] = task['info']['longitude']
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

            # Add everything to the general task, public subsection
            for key, val in task_stats.iteritems():
                locations[task_location][key] = val
                locations[task_location]['public'][key] = val

    # Done with public
    print("  Done")

    # == Analyze First Internal Tasks == #

    # Loop through tasks and collect first internal attributes
    print("Analyzing first internal tasks...")
    i = 0
    tot_tasks = len(first_internal_tasks)
    for task in first_internal_tasks[:100]:

        # Update user
        i += 1
        sys.stdout.write("\r\x1b[K" + "  %s/%s" % (str(i), str(tot_tasks)))
        sys.stdout.flush()

        # Cache important identifiers
        task_location = get_locations([task])[0]
        task_id = task['id']

        # Make sure the task location is actually in the master list - if not, delete it
        if task_location not in locations:
            print("  Dropped location: %s" % task_location)

        else:

            # Store the easy stuff first
            locations[task_location]['lat'] = task['info']['latitude']
            locations[task_location]['lng'] = task['info']['longitude']
            locations[task_location]['year'] = task['info']['year']
            locations[task_location]['wms_url'] = task['info']['url']
            locations[task_location]['county'] = task['info']['county']
            locations[task_location]['comp_loc'] = 'first_internal'

            # Get selection counts
            task_stats = stats_template.copy()
            selection_counts = get_crowd_selection_counts(task_id, first_internal_task_runs)
            total_responses = sum(selection_counts.values())
            crowd_selection = get_crowd_selection(selection_counts, map_field_to_selection)
            crowd_agreement = get_percent_crowd_agreement(crowd_selection, selection_counts,
                                                          len(get_task_runs(task_id, first_internal_task_runs)),
                                                          map_selection_to_field)
            task_stats = dict(task_stats.items() + selection_counts.items())
            task_stats = dict(task_stats.items() + crowd_agreement.items())
            task_stats['n_tot_res'] = total_responses
            task_stats['crowd_sel'] = crowd_selection

            # Add everything to the general task, first internal subsection
            for key, val in task_stats.iteritems():
                locations[task_location][key] = val
                locations[task_location]['fi_intern'][key] = val

    # Done with first internal
    print("  Done")

    # == Analyze Final Internal Tasks == #

    # Loop through tasks and collect final internal attributes
    print("Analyzing final internal tasks...")
    i = 0
    tot_tasks = len(final_internal_tasks)
    for task in final_internal_tasks[:100]:

        # Update user
        i += 1
        sys.stdout.write("\r\x1b[K" + "  %s/%s" % (str(i), str(tot_tasks)))
        sys.stdout.flush()

        # Cache important identifiers
        task_location = get_locations([task])[0]
        task_id = task['id']

        # Make sure the task location is actually in the master list - if not, delete it
        if task_location not in locations:
            print("  Dropped location: %s" % task_location)

        else:

            # Store the easy stuff first
            locations[task_location]['lat'] = task['info']['latitude']
            locations[task_location]['lng'] = task['info']['longitude']
            locations[task_location]['year'] = task['info']['year']
            locations[task_location]['wms_url'] = task['info']['url']
            locations[task_location]['county'] = task['info']['county']
            locations[task_location]['comp_loc'] = 'final_internal'

            # Get selection counts
            task_stats = stats_template.copy()
            selection_counts = get_crowd_selection_counts(task_id, final_internal_task_runs)
            total_responses = sum(selection_counts.values())
            crowd_selection = get_crowd_selection(selection_counts, map_field_to_selection)
            crowd_agreement = get_percent_crowd_agreement(crowd_selection, selection_counts,
                                                          len(get_task_runs(task_id, final_internal_task_runs)),
                                                          map_selection_to_field)
            task_stats = dict(task_stats.items() + selection_counts.items())
            task_stats = dict(task_stats.items() + crowd_agreement.items())
            task_stats['n_tot_res'] = total_responses
            task_stats['crowd_sel'] = crowd_selection

            # Add everything to the general task, final internal subsection
            for key, val in task_stats.iteritems():
                locations[task_location][key] = val
                locations[task_location]['fn_intern'][key] = val

    # Done with final internal
    print("  Done")

    # == Analyze Sweeper Internal Tasks == #

    # Loop through tasks and collect sweeper internal attributes
    print("Analyzing sweeper internal tasks...")
    i = 0
    tot_tasks = len(sweeper_tasks)
    for task in sweeper_tasks[:100]:

        # Update user
        i += 1
        sys.stdout.write("\r\x1b[K" + "  %s/%s" % (str(i), str(tot_tasks)))
        sys.stdout.flush()

        # Cache important identifiers
        task_location = get_locations([task])[0]
        task_id = task['id']

        # Make sure the task location is actually in the master list - if not, delete it
        if task_location not in locations:
            print("  Dropped location: %s" % task_location)

        else:

            # Store the easy stuff first
            locations[task_location]['lat'] = task['info']['latitude']
            locations[task_location]['lng'] = task['info']['longitude']
            locations[task_location]['year'] = task['info']['year']
            locations[task_location]['wms_url'] = task['info']['url']
            locations[task_location]['county'] = task['info']['county']
            locations[task_location]['comp_loc'] = 'sweeper_internal'

            # Get selection counts
            task_stats = stats_template.copy()
            selection_counts = get_crowd_selection_counts(task_id, sweeper_task_runs)
            total_responses = sum(selection_counts.values())
            crowd_selection = get_crowd_selection(selection_counts, map_field_to_selection)
            crowd_agreement = get_percent_crowd_agreement(crowd_selection, selection_counts,
                                                          len(get_task_runs(task_id, sweeper_task_runs)),
                                                          map_selection_to_field)
            task_stats = dict(task_stats.items() + selection_counts.items())
            task_stats = dict(task_stats.items() + crowd_agreement.items())
            task_stats['n_tot_res'] = total_responses
            task_stats['crowd_sel'] = crowd_selection

            # Add everything to the general task, sweeper internal subsection
            for key, val in task_stats.iteritems():
                locations[task_location][key] = val
                locations[task_location]['fn_intern'][key] = val

    # Done with sweeper internal
    print("  Done")

    # == Write the Normal Output == #

    print("Writing compiled output CSV...")
    with open(compiled_output_csv_file, 'w') as f:
        json.dump(locations, f)

    # Success
    print("Done.")
    return 0


if __name__ == '__main__':
    if len(sys.argv) is 1:
        sys.exit(print_usage())
    else:
        sys.exit(main(sys.argv[1:]))
