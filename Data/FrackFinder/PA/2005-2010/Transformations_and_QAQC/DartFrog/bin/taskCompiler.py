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
Compile disparate DartFrog 2005-2010 tasks into a single
cohesive dataset

Sample command:

./dartfrog-taskCompiler.py \
  --pt=../../Global_QAQC/dartfrog/transform/public/tasks/task.json \
  --ptr=../../Global_QAQC/dartfrog/transform/public/tasks/task_run.json \
  --fit=../../Global_QAQC/dartfrog/transform/first-internal/tasks/task.json \
  --fitr=../../Global_QAQC/dartfrog/transform/first-internal/tasks/task_run.json \
  --fint=../../Global_QAQC/dartfrog/transform/final-internal/tasks/task.json \
  --fintr=../../Global_QAQC/dartfrog/transform/final-internal/tasks/task_run.json \
  --st=../../Global_QAQC/dartfrog/transform/sweeper-internal/tasks/task.json \
  --str=../../Global_QAQC/dartfrog/transform/sweeper-internal/tasks/task_run.json \
  --mt=../../Global_QAQC/dartfrog/transform/missing_tasks/tasks/task.json \
  --mtr=../../Global_QAQC/dartfrog/transform/missing_tasks/tasks/task_run.json \
  --co=../CO_CSV.csv \
  --so=../SO_CSV.csv \
  --cj=../CO_JSON.json
"""


import os
import sys
import json
import copy
from os import linesep
from os.path import *


__docname__ = basename(__file__)


#/* ======================================================================= */#
#/*     Build Information
#/* ======================================================================= */#

__author__ = 'Kevin Wurster'
__release__ = '2014-06-19'
__version__ = '0.1-dev'
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
#/*     Global Variables and Constants
#/* ======================================================================= */#

ERROR_COUNT = 0
VERBOSE = False


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
Usage: %s --help-info [options]

Required:
    --pt=str    -> Public task.json
    --ptr=str   -> Public task_run.json
    --fit=str   -> First Internal task.json
    --fitr=str  -> First Internal task_run.json
    --fint=str  -> Final Internal task.json
    --fintr=str -> Final Internal task_run.json
    --st=str    -> Sweeper task.json
    --str=str   -> Sweeper task_run.json
    --co=str    -> Target compiled output.csv
    --so=str    -> Target scrubbed output.csv
    --cj=str    -> Target compiled output.json

Optional:
    --sample=int -> Sample number of tasks to process
    --validate   -> Perform a time consuming task run validation
    --overwrite  -> Overwrite all output files
    --verbose    -> Print out additional errors
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
Output file descriptions


Compiled Output
---------------
The `dartfrog-taskCompiler.py` utility analyzes tasks from all applications and constructs a full history
for each task, in addition to a final set of attributes.  The two `Compiled_Output.*` files contain the full
history and the `Scrubbed_Output.csv` contains just the final set of attributes, but when using for
analytical purposes it is probably best to pull this information out of the first several columns in the
`Compiled_Output.*` files due to how `Scrubbed_Output.csv` is generated.  The data isn't bad, it just isn't
generated the EXACT same way the `Compiled_Output.*` data is constructed.



Compiled Output Description
---------------------------

##### General Structure #####

Each row represents one task and each column represents some attribute.  The information in task_run.json
was analyzed for each task and condensed into a set of attributes that describe the actual input task,
which in turn describes a pond.

##### Application Prioritization #####

The applications were completed serially and when selecting which attributes to use for a given task, the
most recent application should always be used. For instance, if a task was only completed in the `public`
and `sweeper` applications, the final values should be selected from `sweeper application`.  This logic
was followed in the `dartfrog-taskCompiler.py` utility.  The hierarchy is as follows:

1. Missing
2. Sweeper
3. Final Internal
4. First Internal
5. Public

##### Additional Notes ######

The primary key between any given set of task.json and task_run.json files is the `id` field in the task
file and the `task_id` in the task run file.  This is fine when working with one application's output but
creates problems when working across applications.  Since each task represents a pond in space-time, a
unique location key can be generated from lat + long + year.  This works without issue EXCEPT that the
lat/long precision on the tasks that were moved to the first internal application was altered, so in order
to get a good match, all lat/long values were rounded (via Python's round() function) to the 8th decimal
place when generating location keys.  This worked, but about 50 ponds have a location that doesn't match
anything.  Re-processing data with the `dartfrog-taskCompiler.py` utility will produce errors with task ID's.

##### Fields #####

Note that the fields are the same for each application except for a few characters pre-pended to the field
name to denote which application they represent

>       -+= Final Attributes =+-
>
>       location      ->  Location key as described above - generated on the fly
>       wms_url       ->  Final selection - WMS URL from task.json
>       lat           ->  Final selection - degree of latitude from task.json
>       lng           ->  Final selection - degree of longitude from task.json
>       year          ->  Final selection - year from task.json
>       county        ->  Final selection - county name from task.json
>       comp_loc      ->  Name of application the final attributes were selected from
>       n_frk_res     ->  Number of times the crowd classified the pond as 'fracking'
>       n_oth_res     ->  Number of times the crowd classified the pond as 'other'
>       n_unk_res     ->  Number of times the crowd classified the pond as 'unknown'
>       n_tot_res     ->  Total number of times a member of the crowd examined the task (AKA the redundancy)
>       crowd_sel     ->  The classification the crowd chose for the pond
>
>
>       -+= Public Application Attributes =+-
>
>       p_crd_a
>       p_s_crd_a
>       p_n_frk_res
>       p_n_oth_res
>       p_n_unk_res
>       p_n_tot_res
>       p_crowd_sel
>       p_p_crd_a
>       p_p_s_crd_a
>
>
>       -+= Attributes from the First Internal =+-
>
>       fi_n_frk_res
>       fi_n_oth_res
>       fi_n_unk_res
>       fi_n_tot_res
>       fi_crowd_sel
>       fi_p_crd_a
>       fi_p_s_crd_a
>
>
>       -+= Attributes from the Final Internal Application =+->
>
>       fn_n_frk_res
>       fn_n_oth_res
>       fn_n_unk_res
>       fn_n_tot_res
>       fn_crowd_sel
>       fn_p_crd_a
>       fn_p_s_crd_a
>
>
>       -+= Attributes from the Sweeper Internal Application =+->
>
>       sw_n_frk_res
>       sw_n_oth_res
>       sw_n_unk_res
>       sw_n_tot_res
>       sw_crowd_sel
>       sw_p_crd_a
>       sw_p_s_crd_a
>
>
>       -+= Attributes from the Missing Internal Application =+->
>
>       mt_n_frk_res
>       mt_n_oth_res
>       mt_n_unk_res
>       mt_n_tot_res
>       mt_crowd_sel
>       mt_p_crd_a
>       mt_p_s_crd_a

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

    print("")
    print("Help flags:")
    print("  --help    -> More detailed description of this utility")
    print("  --usage   -> Arguments, parameters, flags, options, etc.")
    print("  --version -> Version and ownership information")
    print("  --license -> License information")
    print("")

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
#/*     Define get_crowd_selection() function
#/* ======================================================================= */#

def get_crowd_selection(selection_count, selection_map):
    """
    Figure out what the crowd actually selected

    :param selection_count: number of responses per selection
    :type selection_count: dict
    :param selection_map: maps selections to output fields
    :type selection_map: dict

    :return: the response with the most selections or tied responses separated by |
    :rtype: str|None
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


#/* ======================================================================= */#
#/*     Define get_crowd_selection_counts() function
#/* ======================================================================= */#

def get_crowd_selection_counts(input_id, task_runs_json_object, location):

    """
    Figure out how many times the crowd selected each option

    :param input_id: task.json['id']
    :type input_id: int
    :param task_runs_json_object: task runs from json.load(open('task_run.json'))
    :type task_runs_json_object: list
    :param location: unique location key (lat + long + year)
    :type location: str

    :return: number of times the crowd selected each classification for a given task
    :rtype: dict
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


#/* ======================================================================= */#
#/*     Define get_percent_crowd_agreement() function
#/* ======================================================================= */#

def get_percent_crowd_agreement(crowd_selection, selection_counts, total_responses, map_selection_field,
                                error_val=None):
    """
    Figure out how well the crowd agreed and if two answers tied, figure out the agreement for both

    :param crowd_selection:
    :type crowd_selection: str
    :param selection_counts:
    :type selection_counts:
    :param total_responses:
    :type total_responses:
    :param map_selection_field:
    :type map_selection_field:
    :param error_val:
    :type error_val:

    :return: crowd agreement level rounded by forcing to int()
    :rtype: int|None
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


#/* ======================================================================= */#
#/*     Define get_locations() function
#/* ======================================================================= */#

def get_locations(tasks):

    """
    Get a list of unique locations from a set of tasks

    :param tasks: tasks from json.load(open('task.json'))
    :type tasks: list

    :return: unique list of locations, which will be used as a primary key to link everything together
    :rtype: list
    """

    output_set = []
    for task in tasks:
        lat = str(round(task['info']['latitude'], 8))
        lng = str(round(task['info']['longitude'], 8))
        year = str(task['info']['year'])
        location = lat + lng + '---' + year
        output_set.append(location)

    return list(set(output_set))


#/* ======================================================================= */#
#/*     Define get_task_runs() function
#/* ======================================================================= */#

def get_task_runs(task_id, task_runs_json):

    """
    Search through all task runs to get the set matching the input task id

    :param task_id: task.json['id'] for the task we want the associated task runs for
    :type task_id: int
    :param task_runs_json: task runs from json.load(open('task_run.json'))
    :type task_runs_json: list

    :return: all task runs where task_run.json['task_id'] == :param task_id:
    :rtype: list
    """

    output_list = []
    for tr in task_runs_json:
        if task_id == tr['task_id']:
            output_list.append(tr)

    return output_list


#/* ======================================================================= */#
#/*     Define load_json() function
#/* ======================================================================= */#

def load_json(input_file):

    """
    Load a JSON file into a JSON object

    :param input_file:
    :type input_file:

    :return: loaded JSON object
    :rtype: list
    """

    with open(input_file, 'r') as f:
        output_json = json.load(f)

    return output_json


#/* ======================================================================= */#
#/*     Define analyze_tasks() function
#/* ======================================================================= */#

def analyze_tasks(locations, tasks, task_runs, comp_loc, comp_key, sample=None):

    """
    Create a dictionary with a location as a key and task stats as values,
    which includes the number of times each task was responded to, how many
    times a given classification was chosen, etc.

    The locations parameter is updated with information from the tasks
    parameter and task_runs parameter and then returned at the very end of
    the function.

    The actual use case is calling the function multiple times, once with data
    from each application, in order to reconstruct each task's history.

    :param locations:
    :type locations: dict
    :param tasks:
    :type tasks: list
    :param task_runs:
    :type task_runs: list
    :param comp_loc: application being processed
    :type comp_loc: str
    :param comp_key: used to reference task attributes for specific applications
    :type comp_key: str
    :param sample: sub-sample size
    :type sample: int

    :return:
    :rtype:
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


#/* ======================================================================= */#
#/*     Define is_location_complete() function
#/* ======================================================================= */#

def is_location_complete(location, tasks, task_runs):

    """
    Figure out if a given location was fully completed in a given task/task_run set

    Determined by sifting through the tasks to find the location's redundancy
    and then sifting through the task_runs to see if there are enough task runs
    to say the task has been completed.

    :param location: the location primary key (lat + long + year)
    :type location: str
    :param tasks: tasks from json.load(open('task.json'))
    :type tasks: list
    :param task_runs: task runs from json.load(open('task_run.json'))
    :type task_runs: list

    :return: True if complete and False if not
    :rtype: bool
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

    global VERBOSE

    #/* ======================================================================= */#
    #/*     Defaults
    #/* ======================================================================= */#

    overwrite_outfiles = False
    sample_size = None
    validate_tasks = False

    #/* ======================================================================= */#
    #/*     Containers
    #/* ======================================================================= */#

    compiled_output_csv_file = None
    compiled_output_json_file = None
    scrubbed_output_csv_file = None
    public_tasks_file = None
    public_task_runs_file = None
    first_internal_tasks_file = None
    first_internal_task_runs_file = None
    final_internal_tasks_file = None
    final_internal_task_runs_file = None
    sweeper_tasks_file = None
    sweeper_task_runs_file = None
    missing_tasks_file = None
    missing_task_runs_file = None

    #/* ======================================================================= */#
    #/*     Parse Arguments
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

    #/* ======================================================================= */#
    #/*     Validate Input/Output Files and Configurations
    #/* ======================================================================= */#

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

    #/* ======================================================================= */#
    #/*     Load Data
    #/* ======================================================================= */#

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

    #/* ======================================================================= */#
    #/*     Get Locations to Analyze
    #/* ======================================================================= */#

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

    #/* ======================================================================= */#
    #/*     Get Task Runs to Analyze
    #/* ======================================================================= */#

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

        #/* ======================================================================= */#
        #/*     Extra location/task run check
        #/* ======================================================================= */#

        # This was used to work out some inherent weirdness in the data so another
        # part of the utility could be developed

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

    #/* ======================================================================= */#
    #/*     Build Master Location Container
    #/* ======================================================================= */#

    # The container constructed below will be used to reconstruct a given task's full history

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

    #/* ======================================================================= */#
    #/*     Analyze Tasks
    #/* ======================================================================= */#

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

    #/* ======================================================================= */#
    #/*     Write Compiled Output JSON
    #/* ======================================================================= */#

    print("Writing compiled JSON output...")
    with open(compiled_output_json_file, 'w') as f:
        json.dump(locations, f)

    #/* ======================================================================= */#
    #/*     Write Scrubbed Output CSV
    #/* ======================================================================= */#

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

    #/* ======================================================================= */#
    #/*     Write Compiled Output CSV
    #/* ======================================================================= */#

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

    #/* ======================================================================= */#
    #/*     Cleanup
    #/* ======================================================================= */#

    # Update user
    if VERBOSE:
        print("Total errors: %s" % str(ERROR_COUNT))
    print("Done.")

    # Success
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
