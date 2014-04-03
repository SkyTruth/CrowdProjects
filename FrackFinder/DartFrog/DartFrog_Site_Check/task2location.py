#!/usr/bin/env python


# Build information
__author__ = 'Kevin Wurster'
__version__ = '0.1'
__copyright__ = 'Copyright SkyTruth 2014'
__license__ = 'New BSD (See LICENSE.txt)'


import os
import sys
import json
from os.path import isfile


def print_usage():
    print("")
    print("Usage: task.json task_run.json outfile.txt [options]")
    print("")
    print("Options:")
    print("    --tr=file   -> Task runs file for use with --count")
    print("    --count     -> Include number of task runs for each location")
    print("    --delim=str -> Output text file delimiter for --count")
    print("    --qual=str  -> Output text qualifier for strings for --count")
    print("    --print     -> Print lines as they are written to the outfile")
    print("    --overwrite -> Overwrite outfile if it already exists")
    print("")
    return 1


def get_location(task, return_dict=False, lat_long_sep='', long_year_sep='---'):
    try:
        lat = task['info']['latitude']
        lng = task['info']['longitude']
        year = task['info']['year']
    except KeyError:
        return None
    if return_dict:
        return {'latitude': lat,
                'longitude': lng,
                'year': year}
    else:
        return ''.join([str(lat), lat_long_sep, str(lng), long_year_sep, str(year)])


def count_task_runs(task, task_runs, input_task_field='id', task_run_field='task_id'):
    task_id = str(task[input_task_field])
    count = 0
    for task_run in task_runs:
        task_run_id = str(task_run[task_run_field])
        if task_id == task_run_id:
            count += 1
    return count


def main(args):

    # Defaults
    line_sep = os.linesep
    tasks_file = None
    task_runs_file = None
    output_file = None
    compute_num_task_runs = False
    delimiter = ','
    print_lines = False
    overwrite_outfile = False
    text_qualifier = '"'

    # == Parse Arguments == #
    for arg in args:

        # Additional parameters
        if arg == '--count':
            compute_num_task_runs = True
        elif '--delim=' in arg or '--delimiter=' in arg:
            delimiter = arg.split('=')[1]
        elif '--linesep=' in arg:
            line_sep = arg.split('=')[1]
        elif arg == '--print':
            print_lines = True
        elif arg == '--overwrite':
            overwrite_outfile = True
        elif '--qual=' in arg or '--qualifier=' in arg:
            text_qualifier = arg.split('=')[1]
        elif '--tr=' in arg or '--task-runs=' in arg:
            task_runs_file = arg.split('=')[1]

        # These arguments are positional
        else:

            # Define input and output files
            if tasks_file is None:
                tasks_file = arg
            elif output_file is None:
                output_file = arg

            # Catch unrecognized arguments
            else:
                print("ERROR: Invalid argument: %s" % arg)
                return 1

    # == Validate Parameters == #

    # Delete output file if it already exists and user has specified --overwrite
    if overwrite_outfile and isfile(output_file):
        print("Overwriting outfile")
        os.remove(output_file)

    # If there is no task run file, set the delimiter and qualifier to an empty string to make post-processing easier
    if task_runs_file is None:
        delimiter = ''
        text_qualifier = ''

    # Make sure files do/don't exist and parameters are sane
    bail = False
    if tasks_file is None or not isfile(tasks_file) or not os.access(tasks_file, os.R_OK):
        print("ERROR: Can't access task file: %s" % str(tasks_file))
        bail = True
    if task_runs_file is not None:
        if not isfile(task_runs_file) or not os.access(task_runs_file, os.R_OK):
            print("ERROR: Can't access task run file: %s" % str(tasks_file))
            bail = True
    if output_file is None or isfile(output_file):
        print("ERROR: Output file exists: %s" % str(output_file))
        bail = True
    if bail:
        return 1

    # == Perform Conversion == #

    # Convert tasks file to json
    print("Converting task file %s to a JSON object..." % tasks_file)
    tasks_json = None
    with open(tasks_file, 'r') as f:
        tasks_json = json.load(f)
    print("Found %s items" % str(len(tasks_json)))

    # Convert task runs file to json
    task_runs_json = None
    if compute_num_task_runs:
        print("Converting task run file %s to a JSON object..." % task_runs_file)
        with open(task_runs_file, 'r') as f:
            task_runs_json = json.load(f)
        print("Found %s items" % str(len(task_runs_json)))

    # Write data to the output file
    min_task_run_count = None
    max_task_run_count = None
    task_run_count_histogram = {}
    num_locations = 0
    print("Opening outfile %s" % output_file)
    with open(output_file, 'w') as o_file:

        # Loop through all tasks in a task.json file
        print("Looping through %s tasks..." % str(len(tasks_json)))
        for task in tasks_json:

            num_locations += 1

            # Define the unique task location key (lat + long + year)
            task_location = get_location(task)

            # Define the line content based on whether or not we need the number of matching items from task_run.json
            if compute_num_task_runs:
                num_task_runs = count_task_runs(task, task_runs_json)
                line = ''.join([text_qualifier, task_location, text_qualifier, delimiter, str(num_task_runs), line_sep])

                # Update min/max stats
                if min_task_run_count is None or num_task_runs < min_task_run_count:
                    min_task_run_count = num_task_runs
                if max_task_run_count is None or num_task_runs > max_task_run_count:
                    max_task_run_count = num_task_runs

                # Update histogram
                if num_task_runs in task_run_count_histogram:
                    new_count = task_run_count_histogram[num_task_runs] + 1
                    task_run_count_histogram[num_task_runs] = new_count
                else:
                    task_run_count_histogram[num_task_runs] = 1
            else:
                line = ''.join([text_qualifier, task_location, text_qualifier, line_sep])

            # Print line content if user requested it
            if print_lines:
                print(line.replace(line_sep, ''))

            # Write the line to the output file
            o_file.write(line)

    # Print stats
    print("")
    print("---== Stats ==---")
    if task_runs_file is None:
        print("Num locations = %s" % str(num_locations))
    else:
        print("Task run count histogram:")
        histo_keys = task_run_count_histogram.keys()
        histo_keys.sort()
        for key in histo_keys:
            print("  %s : %s" % (key, str(task_run_count_histogram[key])))
        print("Num locations = %s" % str(num_locations))
        print("Histogram sum = %s" % str(sum(task_run_count_histogram.itervalues())))
        print("Min task run count = %s" % str(min_task_run_count))
        print("Max task run count = %s" % str(max_task_run_count))
    print("")

    # Successful
    return 0


if __name__ == '__main__':
    if len(sys.argv) is 1:
        sys.exit(print_usage())
    else:
        sys.exit(main(sys.argv[1:]))