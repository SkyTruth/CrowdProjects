#!/usr/bin/env python


# See global __license__ variable for license information


"""
Get stats about a matching set of task.json and task_runs.json
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
__release__ = '2014/04/08'
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
    Print list of help flags

    :rtype: int
    """

    print("")
    print("Help flags:")
    print("  --help    -> A more detailed description of this utility")
    print("  --usage   -> Arguments, parameters, flags, options, etc.")
    print("  --version -> Version and ownership information")
    print("  --license -> License information")
    print("  --short-version -> Only print version number")
    print("  --help-info -> This list")
    print("")

    return 1


def print_help():

    """
    Print a more detailed description of the utility

    :rtype int
    """

    print("%s Detailed Help" % __docname__)
    print("--------------" + "-" * len(__docname__))
    print("Print out a bunch of stats")
    print("")

    return 1


def print_usage():

    """
    Print out the commandline usage information

    :rtype: int
    """

    print("")
    print("Usage: %s [options] task.json task_run.json" % __docname__)
    print("")
    print("Options:")
    print("  --help-info -> Print out a list of help related flags")
    print("  --redundancy=int -> Set the minimum completion redundancy value")
    print("")

    return 1


def print_version():

    """
    Print version and ownership information
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


def task_run_count(task, task_runs):

    """
    Figure out if a given task is complete by checking all the task runs

    :param task: single task object from task.json file
    :type task: dict
    :param task_runs: task_run.json loaded into a JSON
    :type task_runs: list
    :rtype: str
    """

    count = 0
    task_id = task['id']
    for task_run in task_runs:
        tr_id = task_run['task_id']
        if task_id == tr_id:
            count += 1

    return count


def main(args):

    # == Set Defaults and Containers == #

    # Define containers
    task_file = None
    task_run_file = None

    # Set defaults
    redundancy = 10

    # == Parse Arguments == #

    arg_error = False
    i = 0
    try:
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

            # Additional options
            elif '--redundancy=' in arg:
                i += 1
                redundancy = arg.split('=', 1)[1]

            # Ignore empty arguments
            elif arg == '':
                i += 1

            # Assign positional arguments and catch errors
            else:

                # Assign task.json file if it has not yet been assigned
                if task_file is None:
                    i += 1
                    task_file = arg

                # Assign task_run.json file if it has not yet been assigned
                elif task_run_file is None:
                    i += 1
                    task_run_file = arg

                # Catch invalid arguments
                else:
                    i += 1
                    print("ERROR: Invalid argument: %s" % arg)
                    arg_error = True

    # Problem parsing arguments
    except ValueError:

        # User probably forgot to include a parameter with an argument
        print("ERROR: An argument has invalid parameters")
        arg_error = True

    # == Validate Arguments and Settings == #

    # Make sure input files exist
    bail = False
    if arg_error:
        print("ERROR: Did not successfully parse arguments")
        bail = True
    if task_file is None or not isfile(task_file) or not os.access(task_file, os.R_OK):
        print("ERROR: Can't access task file: %s" % task_file)
        bail = True
    if task_run_file is None or not isfile(task_run_file) or not os.access(task_run_file, os.R_OK):
        print("ERROR: Can't access task run file: %s" % task_run_file)
        bail = True
    try:
        redundancy = int(redundancy)
        if redundancy < 0:
            print("ERROR: Invalid redundancy - must be > 0: %s" % str(redundancy))
            bail = True
    except ValueError:
        print("ERROR: Invalid redundancy - must be an integer: %s" % str(redundancy))
        bail = True
    if bail:
        return 1

    # == Cache JSON Content == #

    # Convert task.json file to a JSON object
    with open(task_file, 'r') as f:
        task_json = json.load(f)

    # Convert task_run.json file to a JSON object
    with open(task_run_file, 'r') as f:
        task_run_json = json.load(f)

    # Update user
    print("Found %s tasks in: %s" % (str(len(task_json)), task_file))
    print("Found %s task runs in: %s" % (str(len(task_run_json)), task_run_file))

    # Check to see if all the tasks have been completed
    num_completed_tasks = 0
    num_incomplete_tasks = 0
    print("Checking to see if all tasks have been completed...")
    for task in task_json:
        num_task_runs = task_run_count(task, task_run_json)
        if num_task_runs >= redundancy:
            num_completed_tasks += 1
        else:
            num_incomplete_tasks += 1

    # Update user
    print("Found %s completed tasks" % str(num_completed_tasks))
    print("Found %s incomplete tasks" % str(num_incomplete_tasks))

    # Success
    return 0


if __name__ == '__main__':
    if len(sys.argv) is 1:
        sys.exit(print_usage())
    else:
        sys.exit(main(sys.argv[1:]))
