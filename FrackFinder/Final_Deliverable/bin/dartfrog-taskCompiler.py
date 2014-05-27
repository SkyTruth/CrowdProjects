#!/usr/bin/env python


"""
Compile disparate DartFrog tasks into a single cohesive dataset

Sample command:

./dartfrog-taskCompiler.py \
  --pt=../Global_QAQC/dartfrog/transform/public/tasks/task.json \
  --ptr=../Global_QAQC/dartfrog/transform/public/tasks/task_run.json \
  --fit=../Global_QAQC/dartfrog/transform/first-internal/tasks/task.json \
  --fitr=../Global_QAQC/dartfrog/transform/first-internal/tasks/task_run.json \
  --fint=../Global_QAQC/dartfrog/transform/final-internal/tasks/task.json \
  --fintr=../Global_QAQC/dartfrog/transform/final-internal/tasks/task_run.json \
  --st=../Global_QAQC/dartfrog/transform/sweeper-internal/tasks/task.json \
  --str=../Global_QAQC/dartfrog/transform/sweeper-internal/tasks/task_run.json \
  --mt=../Global_QAQC/dartfrog/transform/missing_tasks/tasks/task.json \
  --mtr=../Global_QAQC/dartfrog/transform/missing_tasks/tasks/task_run.json \
  --co=CO_CSV.csv \
  --so=SO_CSV.csv \
  --cj=CO_JSON.json
"""


import os
import sys
import json
import copy
import inspect
from os import linesep
from os.path import isfile
from os.path import basename
from pprint import pprint


# Global parameters
ERROR_COUNT = 0
VERBOSE = False


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
    print("    --co=str    -> Target compiled output.csv")
    print("    --so=str    -> Target scrubbed output.csv")
    print("    --cj=str    -> Target compiled output.json")
    print("")
    print("Optional:")
    print("    --sample=int -> Sample number of tasks to process")
    print("    --validate   -> Perform a time consuming task run validation")
    print("    --overwrite  -> Overwrite all output files")
    print("    --verbose    -> Print out additional errors")
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
    crowd_selection = None

    # Figure out what the maximum number of selections was
    max_selection = max(selection_count.values())

    # Build the crowd_selection
    if max_selection is 0:
        crowd_selection = None
    else:
        for selection, count in selection_count.iteritems():
            if count is max_selection:
                if crowd_selection is None:
                    crowd_selection = selection_map[selection]
                else:
                    crowd_selection += '|' + selection_map[selection]

    # Return to user
    return crowd_selection


def get_crowd_selection_counts(input_id, task_runs_json_object, location):
    """
    Figure out how many times the crowd selected each option
    """

    global VERBOSE
    global ERROR_COUNT

    counts = {'n_frk_res': None,
              'n_unk_res': None,
              'n_oth_res': None}
    for task_run in task_runs_json_object:
        if input_id == task_run['task_id']:
            try:
                selection = task_run['info']['selection']
            except KeyError:
                if VERBOSE:
                    print("  -  task_id KeyError for get_crowd_selection_counts(): %s" % location)
                ERROR_COUNT += 1
            if selection == 'fracking':
                if counts['n_frk_res'] is None:
                    counts['n_frk_res'] = 1
                else:
                    counts['n_frk_res'] += 1
            elif selection == 'unknown':
                if counts['n_unk_res'] is None:
                    counts['n_unk_res'] = 1
                else:
                    counts['n_unk_res'] += 1
            elif selection == 'other':
                if counts['n_oth_res'] is None:
                    counts['n_oth_res'] = 1
                else:
                    counts['n_oth_res'] += 1
            else:
                raise ValueError("get_crowd_selection_counts()")
    if counts.values() == [None, None, None]:
        if VERBOSE:
            print("  -  No task runs in get_crowd_selection_counts(): %s" % location)
        ERROR_COUNT += 1
    return copy.deepcopy(counts)


def get_percent_crowd_agreement(crowd_selection, selection_counts, total_responses, map_selection_field,
                                error_val=None):
    """
    Figure out how well the crowd agreed and if two answers tied, figure out the agreement for both
    """

    # Compute crowd agreement
    # The try/except blocks are for situations where tasks have never been viewed, which yields zero total_responses
    per_crowd_agreement = None
    split_per_crowd_agreement = None
    o_dict = {}

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

    # Construct output and return
    o_dict['p_crd_a'] = per_crowd_agreement
    o_dict['p_s_crd_a'] = split_per_crowd_agreement

    return copy.deepcopy(o_dict)


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


def analyze_tasks(locations, tasks, task_runs, comp_loc, comp_key, sample=None):

    """
    Do DartFrog specific stuff
    """

    global VERBOSE
    global ERROR_COUNT

    # == Analyze Public Tasks == #

    # Get a sample if necessary
    if sample is not None:
        tasks = tasks[:sample]

    # Map field names to selections
    map_field_to_selection = {'n_frk_res': 'fracking',
                              'n_oth_res': 'other',
                              'n_unk_res': 'unknown'}

    # Map selections to field names
    map_selection_to_field = {'fracking': 'n_frk_res',
                              'other': 'n_oth_res',
                              'unknown': 'n_unk_res'}

    # Loop through tasks and collect public attributes
    print("Analyzing %s tasks..." % comp_loc)
    i = 0
    tot_tasks = len(tasks)
    for task in tasks:

        # Update user
        i += 1
        sys.stdout.write("\r\x1b[K" + "  %s/%s" % (str(i), str(tot_tasks)))
        sys.stdout.flush()

        # Cache important identifiers
        task_location = get_locations([task])[0]
        task_id = task['id']

        # Make sure the task location is actually in the master list - if not, delete it
        if task_location not in locations:
            if VERBOSE:
                print("  -  Dropped location: %s" % task_location)
            ERROR_COUNT += 1
        else:

            # Store the easy stuff first
            locations[task_location]['lat'] = task['info']['latitude']
            locations[task_location]['lng'] = task['info']['longitude']
            locations[task_location]['year'] = task['info']['year']
            locations[task_location]['wms_url'] = task['info']['url']
            locations[task_location]['county'] = task['info']['county']
            locations[task_location]['comp_loc'] = comp_loc

            # Get selection counts
            task_stats_template = {'n_unk_res': None,
                                   'n_frk_res': None,
                                   'n_oth_res': None,
                                   'n_tot_res': None,
                                   'crowd_sel': None,
                                   'p_crd_a': None,
                                   'p_s_crd_a': None}
            task_stats = copy.deepcopy(task_stats_template)
            selection_counts = get_crowd_selection_counts(task_id, task_runs, task_location)
            total_responses = sum([sc for sc in selection_counts.values() if sc is not None])
            if total_responses is 0:
                total_responses = None
            crowd_selection = get_crowd_selection(selection_counts, map_field_to_selection)
            crowd_agreement = get_percent_crowd_agreement(crowd_selection, selection_counts,
                                                          len(get_task_runs(task_id, task_runs)),
                                                          map_selection_to_field)
            task_stats = dict(task_stats.items() + selection_counts.items())
            task_stats = dict(task_stats.items() + crowd_agreement.items())
            task_stats['n_tot_res'] = total_responses
            task_stats['crowd_sel'] = crowd_selection

            # Add everything to the general task, public subsection
            for key, val in task_stats.iteritems():
                locations[task_location][key] = val
                locations[task_location][comp_key][key] = val

    # Done with public
    print("  -  Done")
    return copy.deepcopy(locations)


def is_location_complete(location, tasks, task_runs):

    """
    Figure out if a given location was completed in a given tas/task_run set
    """

    # Translate location to a task.json ID
    task_id = None
    for task in tasks:
        if location == get_locations([task]):
            task_id = task['id']
            break
    else:
        print("ERROR: is_location_complete(): No task id for: %s" % location)
        return False

    # Get task_runs
    for task_run in task_runs:
        if str(task_id) == str(task_run['task_id']):
            return True


def main(args):

    """
    Main routine
    """

    global VERBOSE

    # Default
    overwrite_outfiles = False
    sample_size = None
    validate_tasks = False

    # Containers for storing input and output files
    compiled_output_csv_file = '../Global_QAQC/dartfrog/Compiled_Output.csv'
    compiled_output_json_file = '../Global_QAQC/dartfrog/Compiled_Output.json'
    scrubbed_output_csv_file = '../Global_QAQC/dartfrog/Scrubbed_Output.csv'
    public_tasks_file = '../Global_QAQC/dartfrog/transform/public/tasks/task.json'
    public_task_runs_file = '../Global_QAQC/dartfrog/transform/public/tasks/task_run.json'
    first_internal_tasks_file = '../Global_QAQC/dartfrog/transform/first-internal/tasks/task.json'
    first_internal_task_runs_file = '../Global_QAQC/dartfrog/transform/first-internal/tasks/task_run.json'
    final_internal_tasks_file = '../Global_QAQC/dartfrog/transform/final-internal/tasks/task.json'
    final_internal_task_runs_file = '../Global_QAQC/dartfrog/transform/final-internal/tasks/task_run.json'
    sweeper_tasks_file = '../Global_QAQC/dartfrog/transform/sweeper-internal/tasks/task.json'
    sweeper_task_runs_file = '../Global_QAQC/dartfrog/transform/sweeper-internal/tasks/task_run.json'
    missing_tasks_file = '../Global_QAQC/dartfrog/transform/missing_tasks/tasks/task.json'
    missing_task_runs_file = '../Global_QAQC/dartfrog/transform/missing_tasks/tasks/task_run.json'

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

        # Missing tasks JSON files
        elif '--mt=' in arg:
            missing_tasks_file = arg.split('=', 1)[1]
        elif '--mtr=' in arg:
            missing_task_runs_file = arg.split('=', 1)[1]

        # Compiled output CSV
        elif '--co=' in arg:
            compiled_output_csv_file = arg.split('=', 1)[1]

        # Scrubbed output CSV
        elif '--so=' in arg:
            scrubbed_output_csv_file = arg.split('=', 1)[1]

        # Compiled output JSON
        elif '--cj=' in arg:
            compiled_output_json_file = arg.split('=', 1)[1]

        # Process a sample set
        elif '--sample=' in arg:
            sample_size = int(arg.split('=', 1)[1])

        # Include time consuming validation step
        elif arg == '--validate':
            validate_tasks = True

        # Overwrite output files
        elif arg == '--overwrite':
            overwrite_outfiles = True

        # Print out additional error messages
        elif arg == '--verbose':
            VERBOSE = True

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
        if isfile(compiled_output_csv_file) and not overwrite_outfiles:
            print("ERROR: Compiled output CSV exists: %s" % compiled_output_csv_file)
            bail = True
    if compiled_output_json_file is None:
        print("ERROR: No compiled output JSON supplied")
        bail = True
    else:
        if isfile(compiled_output_json_file) and not overwrite_outfiles:
            print("ERROR: Compiled output JSON exists: %s" % compiled_output_json_file)
            bail = True
    if scrubbed_output_csv_file is None:
        print("ERROR: No scrubbed output CSV supplied")
        bail = True
    else:
        if isfile(scrubbed_output_csv_file) and not overwrite_outfiles:
            print("ERROR: Scrubbed output CSV exists: %s" % scrubbed_output_csv_file)
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
    if missing_tasks_file is None or not os.access(missing_tasks_file, os.R_OK):
        print("ERROR: Can't access missing tasks: %s" % missing_tasks_file)
        bail = True
    if missing_task_runs_file is None or not os.access(missing_task_runs_file, os.R_OK):
        print("ERROR: Can't access missing task runs: %s" % missing_task_runs_file)
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

    # Missing task.json
    print("Loading missing internal tasks: %s" % missing_tasks_file)
    missing_tasks = load_json(missing_tasks_file)
    print("  %s" % str(len(missing_tasks)))

    # Missing task_runs.json
    print("Loading missing internal task_runs...")
    missing_task_runs = load_json(missing_task_runs_file)
    print("  %s" % str(len(missing_task_runs)))

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
    sw_missing = 0
    mt_missing = 0
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
            sw_missing += 1
            v_error = True
    print("Validating missing internal locations...")
    for task in missing_tasks:
        location = get_locations([task])[0]
        if location not in location_list:
            drop_locations.append(location)
            mt_missing += 1
            v_error = True
    if v_error:
        print("  Missing Public: %s" % str(p_missing))
        print("  Missing First Internal: %s" % str(fi_missing))
        print("  Missing Final Internal: %s" % str(fn_missing))
        print("  Missing Sweeper: %s" % str(sw_missing))
        print("  Missing missing: %s" % str(mt_missing))

    # Validate task runs
    if validate_tasks:
        locations_no_task_runs = []
        p_missing = 0
        fi_missing = 0
        fn_missing = 0
        sw_missing = 0
        mt_missing = 0
        v_error = False
        print("Validating public task runs...")
        for task in public_tasks:
            if len(get_task_runs(task['id'], public_task_runs)) is 0:
                p_missing += 1
                v_error = True
                task_location = get_locations([task])
                if task_location not in locations_no_task_runs:
                    locations_no_task_runs.append(task_location)
        print("Validating first internal task runs...")
        for task in first_internal_tasks:
            if len(get_task_runs(task['id'], first_internal_task_runs)) is 0:
                fi_missing += 1
                v_error = True
                if task_location not in locations_no_task_runs:
                    locations_no_task_runs.append(task_location)
        print("Validating final internal task runs...")
        for task in final_internal_tasks:
            if len(get_task_runs(task['id'], final_internal_task_runs)) is 0:
                fn_missing += 1
                v_error = True
                if task_location not in locations_no_task_runs:
                    locations_no_task_runs.append(task_location)
        print("Validating sweeper internal runs...")
        for task in sweeper_tasks:
            if len(get_task_runs(task['id'], sweeper_task_runs)) is 0:
                sw_missing += 1
                v_error = True
                if task_location not in locations_no_task_runs:
                    locations_no_task_runs.append(task_location)
        print("Validating missing internal runs...")
        for task in missing_tasks:
            if len(get_task_runs(task['id'], missing_tasks)) is 0:
                mt_missing += 1
                v_error = True
                if task_location not in locations_no_task_runs:
                    locations_no_task_runs.append(task_location)
        if v_error:
            print("  Public with no task runs: %s" % str(p_missing))
            print("  First internal with no task runs: %s" % str(fi_missing))
            print("  Final internal with no task runs: %s" % str(fn_missing))
            print("  Sweeper internal with no task runs: %s" % str(sw_missing))
            print("  Missing internal with no task runs: %s" % str(mt_missing))
            print("  Total unique with locations no task runs: %s " % str(len(locations_no_task_runs)))

        # Figure out if a location with no task runs was actually completed somewhere
        still_bad = []
        print("Looking for locations without task runs in public...")
        for location in locations_no_task_runs:
            if location not in still_bad:
                if not is_location_complete(location, public_tasks, public_task_runs):
                    still_bad.append(location)
        print("Looking for locations without task runs in first internal...")
        for location in locations_no_task_runs:
            if location not in still_bad:
                if not is_location_complete(location, first_internal_tasks, first_internal_task_runs):
                    still_bad.append(location)
        print("Looking for locations without task runs in final internal...")
        for location in locations_no_task_runs:
            if location not in still_bad:
                if not is_location_complete(location, final_internal_tasks, final_internal_task_runs):
                    still_bad.append(location)
        print("Looking for locations without task runs in sweeper internal...")
        for location in locations_no_task_runs:
            if location not in still_bad:
                if not is_location_complete(location, sweeper_tasks, sweeper_task_runs):
                    still_bad.append(location)
        print("Looking for locations without task runs in missing internal...")
        for location in locations_no_task_runs:
            if location not in still_bad:
                if not is_location_complete(location, missing_tasks, missing_task_runs):
                    still_bad.append(location)
        print("  Still bad: %s" % len(still_bad))

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
                         'public': copy.deepcopy(stats_template),
                         'fi_intern': copy.deepcopy(stats_template),
                         'fn_intern': copy.deepcopy(stats_template),
                         'sw_intern': copy.deepcopy(stats_template),
                         'mt_intern': copy.deepcopy(stats_template)}
    locations = {}
    for location in location_list:
        locations[location] = copy.deepcopy(location_template)

    # == Analyze Tasks == #

    # Public tasks
    locations = analyze_tasks(locations, public_tasks, public_task_runs,
                              'public', 'public', sample=sample_size)

    # First internal tasks
    locations = analyze_tasks(locations, first_internal_tasks, first_internal_task_runs,
                              'first_internal', 'fi_intern', sample=sample_size)

    # Final internal tasks
    locations = analyze_tasks(locations, final_internal_tasks, final_internal_task_runs,
                              'final_internal', 'fn_intern', sample=sample_size)

    # Sweeper internal tasks
    locations = analyze_tasks(locations, sweeper_tasks, sweeper_task_runs,
                              'sweeper_internal', 'sw_intern', sample=sample_size)

    # Missing internal tasks
    locations = analyze_tasks(locations, missing_tasks, missing_task_runs,
                              'missing_internal', 'mt_intern', sample=sample_size)

    # == Write the Compiled JSON Output == #

    print("Writing compiled JSON output...")
    with open(compiled_output_json_file, 'w') as f:
        json.dump(locations, f)

    # == Write the Scrubbed CSV Output == #

    # Convert compiled output to lines
    header = ['location', 'wms_url', 'lat', 'lng', 'year', 'county', 'comp_loc', 'n_frk_res', 'n_oth_res',
              'n_unk_res', 'n_tot_res', 'crowd_sel', 'p_crd_a', 'p_s_crd_a']
    scrubbed_lines = []
    for location, attributes in locations.iteritems():
        line = ['' for i in header]
        for item in header:
            if item == 'location':
                line[header.index(item)] = '"' + location + '"'
            else:
                content = attributes[item]
                if content is None:
                    content = ''
                line[header.index(item)] = '"' + str(content) + '"'
        scrubbed_lines.append(line)

    # Write lines
    print("Writing scrubbed output CSV...")
    with open(scrubbed_output_csv_file, 'w') as f:
        f.write(', '.join(['"' + i + '"' for i in header]) + linesep)
        for line in scrubbed_lines:
            f.write(','.join(line) + linesep)

    # == Write the Compiled Output CSV == #

    # Define the header and output container
    compiled_lines = []
    header = [# Location information
              'location', 'wms_url', 'lat', 'lng', 'year', 'county',
              # Final answer information
              'n_frk_res', 'n_oth_res', 'n_unk_res', 'n_tot_res', 'comp_loc', 'crowd_sel', 'p_crd_a', 'p_s_crd_a',
              # Public responses
              'p_n_frk_res', 'p_n_oth_res', 'p_n_unk_res', 'p_n_tot_res', 'p_crowd_sel', 'p_p_crd_a', 'p_p_s_crd_a',
              # First internal responses
              'fi_n_frk_res', 'fi_n_oth_res', 'fi_n_unk_res', 'fi_n_tot_res', 'fi_crowd_sel', 'fi_p_crd_a', 'fi_p_s_crd_a',
              # Final internal responses
              'fn_n_frk_res', 'fn_n_oth_res', 'fn_n_unk_res', 'fn_n_tot_res', 'fn_crowd_sel', 'fn_p_crd_a', 'fn_p_s_crd_a',
              # Sweeper internal responses
              'sw_n_frk_res', 'sw_n_oth_res', 'sw_n_unk_res', 'sw_n_tot_res', 'sw_crowd_sel', 'sw_p_crd_a', 'sw_p_s_crd_a',
              # Missing internal responses
              'mt_n_frk_res', 'mt_n_oth_res', 'mt_n_unk_res', 'mt_n_tot_res', 'mt_crowd_sel', 'mt_p_crd_a', 'mt_p_s_crd_a']

    # Loop through the compiled JSON object and populate stuff
    for location, attributes in locations.iteritems():

        # Define a container for this specific line - default values are empty, which allows any value that is not
        # found in the compiled JSON object to be populated as NULL
        line = ['' for i in header]

        # Loop through the header and populate attributes in the line
        for item in header:

            # Get the easy stuff into the line first - all the final answers and location information
            if item in attributes:
                content = attributes[item]
                if content is None:
                    content = ''
                line[header.index(item)] = '"' + str(content) + '"'

            # Location is a special case since its part of what we're iterating over in the outer loop
            elif item == 'location':
                line[header.index(item)] = '"' + location + '"'

            # Everything else is application specific responses
            else:

                # Figure out which application to pull values from and specify identifying information
                if item[:2] == 'p_':
                    app_key = 'public'
                    field_prefix = 'p_'
                elif item[:3] == 'fi_':
                    app_key = 'fi_intern'
                    field_prefix = 'fi_'
                elif item[:3] == 'fn_':
                    app_key = 'fn_intern'
                    field_prefix = 'fn_'
                elif item[:3] == 'sw_':
                    app_key = 'sw_intern'
                    field_prefix = 'sw_'
                elif item[:3] == 'mt_':
                    app_key = 'mt_intern'
                    field_prefix = 'mt_'
                else:
                    raise ValueError("Can't pull values for item: %s" % item)

                # Pull values and populate line
                for app_attr, app_val in attributes[app_key].iteritems():
                    app_item = field_prefix + app_attr
                    app_content = app_val
                    if app_content is None:
                        app_content = ''

                    # Stick the field prefix back on
                    line[header.index(app_item)] = '"' + str(app_content) + '"'

        # Line is fully constructed
        compiled_lines.append(line)

    # Write lines
    print("Writing compiled output CSV...")
    with open(compiled_output_csv_file, 'w') as f:
        f.write(', '.join(['"' + i + '"' for i in header]) + linesep)
        for line in compiled_lines:
            f.write(','.join(line) + linesep)

    # Success
    if VERBOSE:
        print("Total errors: %s" % str(ERROR_COUNT))
    print("Done.")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
