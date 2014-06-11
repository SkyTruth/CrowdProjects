#!/usr/bin/env python


# See global __license__ variable for license information


"""
Compare two task.json files from PyBossa and keep/remove unique/non-unique tasks.
"""


import os
import sys
import json
import inspect
from os.path import isfile
from os.path import basename


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


def print_help_info():

    """
    Print help flags

    :rtype: int
    """

    print("")
    print("Help flags:")
    print("  --help    -> More detailed description of this utility")
    print("  --usage   -> Arguments, parameters, flags, options, etc.")
    print("  --version -> Version and ownership information")
    print("  --license -> License information")
    print("  --short-version -> Only print version number")
    return 1


def print_help():

    """
    Print a more detailed description of the utility

    :rtype: int
    """

    print("")
    print("%s Detailed Help" % __docname__)
    print("--------------" + "-" * len(__docname__))
    print("PyBossa exports an app's input tasks as task.json")
    print("This utility can compare multiple task.json output")
    print("files and extract unique or non-unique tasks.")
    print("Exclusion and inclusion files can also be used to")
    print("further customize output.")
    print("")
    return 1


def print_usage():

    """
    Print out the commandline usage information

    :rtype: int
    """

    print("")
    print("Usage: %s [options] *.json outfile.json" % __docname__)
    print("")
    print("Options:")
    print("  --help-info -> Print out a list of help related flags")
    print("  --unique    -> Write tasks that are unique in *.json files")
    print("  --overlap   -> Write tasks that exist in *.json files")
    print("  --include|-i files -> Only include tasks in any listed file")
    print("  --exclude|-e files -> Exclude tasks in any listed file")
    print("")
    print("Utility defaults to --overlap mode")
    print("When using -i/-e the -i filtering happens before -e")
    print("")
    return 1


def print_version():

    """
    Print version and ownership information

    :rtype: int
    """

    print("")
    print("%s version %s - released %s" % (__docname__, __version__, __release__))
    print(__copyright__)
    print("")
    return 1


def print_short_version():

    """
    Just print the version number for commandline comparison purposes

    :rtype: int
    """

    print(__version__)
    return 1


def print_license():

    """
    Print licensing information

    :rtype: int
    """

    print(__license__)
    return 1


def get_location(task, lat_long_sep='', long_year_sep='---'):

    """
    Parse a task and return its unique, lat, long, year location key

    :param task: task from task.json
    :type task: dict
    :param lat_long_sep: delimiter to be placed between lat/long in final output
    :type lat_long_sep: str
    :param long_year_sep: delimiter to be placed between long/year in final output
    :type long_year_sep: str
    :rtype: string
    """

    latitude = str(task['info']['latitude'])
    longitude = str(task['info']['longitude'])
    year = str(task['info']['year'])

    return latitude + lat_long_sep + longitude + long_year_sep + year


def get_unique_tasks(*task_groups):

    """
    Compare input JSON objects containing tasks and return a unique set

    :param json_objects: lists of task objects
    :type json_objects: list
    :rtype: list
    """

    # Combine all sub-json objects into a single group
    unique_tasks = []

    # Get a list of tasks from the list of groups
    for task_set in task_groups:

        # Get a single task from the group of tasks we're currently working with
        for task in task_set:

            # Append task to output if its not already in there
            if task not in unique_tasks:
                unique_tasks.append(task)

            # If task is already in the set of tasks that is supposed to be unique, its not unique - remove from output
            else:
                unique_tasks.remove(task)

    # Trash potentially giant input object to save memory
    task_groups = None

    return unique_tasks


def get_overlapping_tasks(task_groups):

    """
    Compare input JSON objects containing tasks and return tasks that
    only exist in all sets.

    :param task_groups: lists of task objects
    :type task_groups: list
    :rtype: list
    """

    # Get a task from a group and make sure it exists in the other groups
    # group_index is used to speed up the loop that searches for overlapping tasks
    # No need to search the current group since that is where we got the task
    overlapping_tasks = []
    group_index = 0

    # Get a group of tasks
    for group in task_groups:

        # Loop through all tasks in the group
        for task in group:

            # Check to make sure the task isn't already in the output overlapping_tasks list - speeds things up
            if task not in overlapping_tasks:

                # Figure out how many groups we need to check the task against and iterate through their indexes
                for check_index in range(0, len(task_groups)):

                    # Don't check the group we're working with in the outer loop - compare the indexes for a quick check
                    if group_index is not check_index:

                        # Loop through tasks in a group and compare unique locations
                        task_location = get_location(task)
                        for check_task in task_groups[check_index]:

                            # Get location and compare
                            check_task_location = get_location(check_task)
                            if task_location == check_task_location:

                                # Hey, it exists - Append to the output container, but only if its not already in there
                                if task not in overlapping_tasks:
                                    overlapping_tasks.append(task)

        # Iterate the group index in preparation for processing the next group
        group_index += 1

    # Trash potentially giant input object to save memory
    task_groups = None

    return overlapping_tasks


def apply_task_inclusion_filter(tasks, inclusion_files):

    """
    Check a set of input tasks against a set of files.  Only keep
    the input tasks that DO appear in ANY of the inclusion_files

    :param tasks: list of input task objects
    :type tasks: list
    :param inclusion_files: list of JSON files to check against
    :type inclusion_files: list
    :rtype: list
    """

    # Open the inclusion files and cache as JSON object
    json_inclusion_files = []
    for item in inclusion_files:
        with open(item, 'r') as f:
            json_inclusion_files.append(json.load(f))

    # Loop through all tasks and see if they exist in ANY of the inclusion JSON objects
    inclusion_tasks = []

    # Get a task from the input set of tasks
    for task in tasks:

        # Get one file's worth of inclusion tasks
        for inclusion_tasks in json_inclusion_files:

            # See if the task from the outer loop exists in the current set of inclusion tasks
            if task in inclusion_tasks:

                # Hey, it's in there - Append to output list.
                inclusion_tasks.append(task)

    # Trash potentially giant input and cached objects
    json_inclusion_files = None
    tasks = None

    return inclusion_tasks


def apply_task_exclusion_filter(tasks, exclusion_files):

    """
    Check a set of input tasks against a set of files.  Only keep
    the input tasks that DO NOT appear in ANY of the exclusion_files

    :param tasks: list of input task objects
    :type tasks: list
    :param exclusion_files: list of JSON files to check against
    :type exclusion_files: list
    :rtype: list
    """

    # Open the exclusion files and cache as JSON object
    json_exclusion_files = []
    for item in exclusion_files:
        with open(item, 'r') as f:
            json_exclusion_files.append(json.load(f))

    # Loop through all tasks and see if they exist in ANY of the exclusion JSON objects
    exclusion_tasks = []

    # Get a task from the input set of tasks
    for task in tasks:

        # Get one file's worth of exclusion tasks
        for inclusion_tasks in json_exclusion_files:

            # See if the task from the outer loop exists in the current set of exclusion tasks
            if task not in inclusion_tasks:

                # Task passed the filter, so append to output container
                inclusion_tasks.append(task)

    # Trash potentially giant input and cached objects
    json_exclusion_files = None
    tasks = None

    return exclusion_tasks


def main(args):

    """
    Main routine

    :param args: list of arguments from command line(sys.argv[1:])
    :type args: dict
    :rtype: int
    """

    # == Default Configuration and Containers == #

    # Set defaults
    outfile = None
    compare_files = []
    comparison = 'overlap'
    exclusion_files = []
    inclusion_files = []
    write_to_outfile = True

    # Set constraints
    comparison_modes = ('overlap', 'unique')

    # == Parse Arguments == #

    # Parse input arguments
    arg_error = False
    try:
        i = 0
        while i < len(args):

            # Get argument
            arg = args[i]

            # Help arguments
            if arg in ('--help-info', '-help-info', '--helpinfo', '-helpinfo', '-hi'):
                return print_help()
            elif arg in ('--help', '-help', '-h'):
                return print_help()
            elif arg in ('--usage', '-usage', '-u'):
                return print_usage()
            elif arg in ('--version', '-version'):
                return print_version()
            elif arg in ('--short-version', '-short-version', '--shortversion', '-shortversion'):
                return print_short_version()
            elif arg in ('--license', '-license'):
                return print_license()

            # Collection inclusion files
            elif arg in ('--include', '-include', '-i'):
                i += 1
                while i < len(args) and arg[0] != '-':
                    exclusion_files.append(arg)
                    i += 1
            elif arg in ('--exclude', '-exclude', '-e'):
                i += 1
                while i < len(args) and arg[0] != '-':
                    inclusion_files.append(arg)
                    i += 1

            # Additional options
            elif arg in ('--unique', '-unique'):
                i += 1
                comparison = 'unique'
            elif arg in ('--overlap', '-overlap'):
                i += 1
                comparison = 'overlap'
            elif arg in ('--unique', '-unique'):
                i += 1
                comparison = 'unique'
            elif '--mode=' in arg or '-mode=' in arg:
                i += 1
                comparison = arg.split('=', 1)[1]
            elif arg == '--no-write':
                i += 1
                write_to_outfile = False

            # Set positional arguments
            else:

                # Grab *.json files
                while i < len(args) and args[i][0] != '-':
                    compare_files.append(args[i])
                    i += 1

        # Done parsing arguments - grab the last compare_file and make it the output file
        outfile = compare_files.pop(-1)

    except IndexError:

        # User didn't provide all necessary keyword arguments
        print("ERROR: An argument has invalid parameters")
        arg_error = True

    # == Validate Arguments and Settings == #

    # Make sure an outfile was given and that it exists
    bail = False
    if outfile is None:
        print("ERROR: Need an outfile")
        bail = True
    elif isfile(outfile):
        print("ERROR: Outfile exists: %s" % outfile)
        bail = True
    elif outfile in exclusion_files:
        print("ERROR: Outfile can't be used as an exclusion file: %s" % outfile)
        bail = True
    elif outfile in inclusion_files:
        print("ERROR: Outfile can't be used as an inclusion file: %s" % outfile)
        bail = True

    # Make sure the comparison mode is allowed
    if comparison not in comparison_modes:
        print("ERROR: Invalid comparison mode: %s" % comparison)
        print("       Valid modes: %s" % str(comparison_modes))
        bail = True

    # Make sure all input files exist
    if compare_files is []:
        print("ERROR: Need files to compare")
        bail = True
    elif len(compare_files) is 1:
        print("ERROR: Need more than one file to compare")
        bail = True
    else:
        for item in compare_files:
            if not isfile(item):
                print("ERROR: Can't find input file: %s" % item)
                bail = True

    # Make sure inclusion files exist, if any were given
    if inclusion_files is not []:
        for inclusion in inclusion_files:
            if not os.access(inclusion, os.R_OK) or not isfile(inclusion):
                print("ERROR: Can't access inclusion file: %s" % inclusion)
                bail = True

    # Make sure exclusion files exist, if any were given
    if exclusion_files is not []:
        for exclusion in exclusion_files:
            if not os.access(exclusion, os.R_OK) or not isfile(exclusion):
                print("ERROR: Can't access exclusion file: %s" % exclusion)
                bail = True

    # Check for argument errors
    if arg_error:
        print("ERROR: Did not successfully parse arguments")
        bail = True

    # If validation failed, return an error code
    if bail:
        return 1

    # == Open JSON Files == #

    # Cache all JSON files
    print("Opening %s files for comparison..." % str(len(compare_files)))
    json_content = {}
    for file_path in compare_files:
        print("  Parsing: %s" % file_path)
        with open(file_path, 'r') as f:
            json_content[file_path] = json.load(f)
        print("  Found %s tasks" % str(len(json_content[file_path])))

    # == Compare Files == #

    # Update user
    num_total_tasks = 0
    for input_file, task_list in json_content.iteritems():
        task_count = len(task_list)
        num_total_tasks += task_count
    print("Found %s total tasks" % str(num_total_tasks))

    # Mode is set to overlap - find tasks that exist in all files
    if comparison == 'overlap':
        print("Finding overlapping tasks...")
        post_compare_tasks = get_overlapping_tasks(json_content.values())

    # Mode is set to unique - find tasks that only appear once across all files
    elif comparison == 'unique':
        print("Finding unique tasks...")
        post_compare_tasks = get_unique_tasks(json_content.values())

    # Invalid mode - error out
    else:
        print("ERROR: Can't compare files - invalid comparison mode: %s" % str(comparison))
        return 1

    # == Apply Filters == #

    # Cache containers to make some later logic a bit easier
    post_inclusion_filter_tasks = None
    post_exclusion_filter_tasks = None

    # Inclusion files supplied - filter tasks to those that only appear in any of the inclusion files
    if inclusion_files:
        print("Filtering %s tasks against %s inclusion files..." % (str(len(post_compare_tasks)), len(inclusion_files)))
        post_inclusion_filter_tasks = apply_task_inclusion_filter(post_compare_tasks, inclusion_files)

    # Exclusion files supplied - filter tasks to those that don't appear in any of the exclusion files
    if exclusion_files:
        # Adjust variables if the user didn't set an inclusion filter
        if post_inclusion_filter_tasks is None:
            post_inclusion_filter_tasks = post_compare_tasks
        print("Filtering %s tasks against against %s exclusion files..." % (str(len(post_inclusion_filter_tasks)),
                                                                            len(exclusion_files)))
        post_exclusion_filter_tasks = apply_task_exclusion_filter(post_inclusion_filter_tasks, exclusion_files)

    # == Adjust Variables Post Filtering == #

    # Since the exclusion filter happens after the inclusion filter, use its output for the post filter task set
    if post_exclusion_filter_tasks is not None:
        final_task_list = post_exclusion_filter_tasks

    # User didn't specify an exclusion filter but did specify an inclusion filter - use the inclusion tasks
    elif post_inclusion_filter_tasks is not None:
        final_task_list = post_inclusion_filter_tasks

    # User didn't specify any filters - use the post_compare tasks as the final task set
    else:
        final_task_list = post_compare_tasks

    # Store some information and trash potentially giant variables
    num_post_compare_tasks = len(post_compare_tasks)
    if inclusion_files:
        num_post_inclusion_filter_tasks = len(post_inclusion_filter_tasks)
    else:
        num_post_inclusion_filter_tasks = None
    if exclusion_files:
        num_post_exclusion_filter_tasks = len(post_exclusion_filter_tasks)
    else:
        num_post_exclusion_filter_tasks = None
    post_inclusion_filter_tasks = None
    post_exclusion_filter_tasks = None
    post_compare_tasks = None

    # == Update User and Print Stats == #

    # Update user
    print("Started with %s tasks from %s files" % (str(num_total_tasks), len(compare_files)))
    print("Used '%s' comparison to find %s tasks" % (comparison, str(num_post_compare_tasks)))
    if inclusion_files:
        print("Checked %s inclusion files - left with %s tasks" % (str(len(inclusion_files)),
                                                                   str(num_post_inclusion_filter_tasks)))
    if exclusion_files:
        print("Checked %s exclusion files - left with %s tasks" % (str(len(exclusion_files)),
                                                                   str(num_post_exclusion_filter_tasks)))
    print("Final number of tasks: %s" % str(len(final_task_list)))

    # Write final tasks to output file
    if not write_to_outfile:
        print("Skipping write to outfile: %s" % outfile)
    else:
        print("Writing to output file: %s" % outfile)
        try:
            with open(outfile, 'w') as f:
                json.dump(final_task_list, f)
        except IOError:
            print("ERROR: Could not write final tasks - check permissions: %s" % outfile)

    # Update user
    print("Done.")

    # Success
    return 0


if __name__ == '__main__':
    if len(sys.argv) is 1:
        sys.exit(print_usage())
    else:
        sys.exit(main(sys.argv[1:]))
