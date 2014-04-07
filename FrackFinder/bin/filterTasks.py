#!/usr/bin env python


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
    print("  --include|-i files -> Only include tasks in file")
    print("  --exclude|-e files -> Exclude tasks in file")
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
    print('%s version %s - released %s' % (__docname__, __version__, __release__))
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

    print('\n' + __license__ + '\n')
    return 1


def get_unique_tasks(*task_groups):

    """
    Compare input JSON objects containing tasks and return a unique set

    :param json_objects: lists of task objects
    :type json_objects: list
    :rtype: list
    """

    # Combine all sub-json objects into a single group
    unique_tasks = []
    for task_set in task_groups:
        for task in task_set:
            if task not in unique_tasks:
                unique_tasks.append(task)

    # Trash potentially giant input object to save memory
    task_groups = None

    return unique_tasks


def get_overlapping_tasks(*task_groups):

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

            # Figure out how many groups we need to check the task against and iterate through their indexes
            for i in range(0, len(task_groups) - 1):

                # Don't check the group we're working with in the outer loop - compare the indexes for a quick check
                if group_index is not i:

                    # Got a group we can check - see if the task exists in it
                    if task in task_groups[group_index]:

                        # Hey, it exists!  Append to the output container.
                        overlapping_tasks.append(task)

        # Iterate the group index in preparation for processing the next group
        group_index += 1

    # Trash potentially giant input object to save memory
    task_groups = None

    return overlapping_tasks


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
                return print_help_info()
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
            elif ('--mode=', '-mode=') in arg:
                i += 1
                comparison = arg.split('=', 1)[1]

            # Set positional arguments
            else:

                # Grab *.json files
                while i < len(args) and arg[0] != '-':
                    compare_files.append(arg)
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

    # Make sure the comparison mode is allowed
    if comparison not in comparison_modes:
        print("ERROR: Invalid comparison mode: %s" % comparison)
        print("       Valid modes: %s" % str(comparison_modes))
        bail = True

    # Make sure all input files exist
    if compare_files is []:
        print("ERROR: Need files to compare")
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
    print("Opening files to compare...")
    json_content = {}
    for item in compare_files:
        print("  Parsing: %s")
        with open(item, 'r') as f:
            json_content[item] = json.load(f)

    #







    # Success
    return 0


if __name__ == '__main__':
    if len(sys.argv) is 1:
        sys.exit(print_usage())
    else:
        sys.exit(main(sys.argv[1:]))
