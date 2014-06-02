#!/usr/bin/env python


# This document is part of CrowdTools
# https://github.com/SkyTruth/CrowdTools


# =================================================================================== #
#
# New BSD License
#
# Copyright (c) 2014, SkyTruth, Kevin D. Wurster
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * The names of its contributors may not be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# =================================================================================== #


"""
Combine the contents of PyBossa's exported task.json and task_run.json
"""


import os
import sys
import json
from os.path import *


__docname__ = basename(__file__)
__all__ = ['print_usage', 'print_help', 'print_license', 'print_help_info', 'print_version', 'get_task',
           'adjust_fields', 'main']


# Build information
__author__ = 'Kevin Wurster'
__release__ = '2014-06-02'
__version__ = '0.1-dev'
__license__ = '''
New BSD License

Copyright (c) 2014, Kevin D. Wurster
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* The names of its contributors may not be used to endorse or promote products
  derived from this software without specific prior written permission.

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
'''


#/* ======================================================================= */#
#/*     Define print_usage()
#/* ======================================================================= */#
def print_usage():

    """
    Print commandline usage
    """

    print("")
    print("Usage: %s [options] task.json task_run.json outfile.json" % __docname__)
    print("")
    print("Options:")
    print("  --overwrite  -> Overwrite output file")
    print("  --prefix=str -> Prefix for all task fields - defaults to '_t_'")
    print("")

    return 1


#/* ======================================================================= */#
#/*     Define print_help()
#/* ======================================================================= */#
def print_help():

    """
    Print more detailed help information
    """

    print("")
    print("Detailed Help: %s" % __docname__)
    print("---------------" + "-" * len(__docname__))
    print("Loops through all task runs and appends the matching task's fields to the task")
    print("run.  A string is prepended to all task fields in order to prevent overwriting")
    print("fields that exist in both the task and task run - this prefix can be set by the")
    print("user via the '--prefix=str' option.")
    print("")

    return 1


#/* ======================================================================= */#
#/*     Define print_license()
#/* ======================================================================= */#
def print_license():

    """
    Print licensing information
    """

    print(__license__)

    return 1


#/* ======================================================================= */#
#/*     Define print_help_info()
#/* ======================================================================= */#
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
    print("")

    return 1


#/* ======================================================================= */#
#/*     Define print_version()
#/* ======================================================================= */#
def print_version():

    """
    Print the module version information
    """

    print("")
    print("%s version %s - released %s" % (__docname__, __version__, __release__))
    print("")

    return 1


#/* ======================================================================= */#
#/*     Define get_task()
#/* ======================================================================= */#
def get_task(task_id, tasks_object):

    """
    Find the matching task.json for a given task_run.json 's task_id
    """

    task = None
    for t in tasks_object:
        if t['id'] == task_id:
            task = t
            break

    return task


#/* ======================================================================= */#
#/*     Define adjust_fields()
#/* ======================================================================= */#
def adjust_fields(prefix, task):

    """
    Prepend the prefix to a task's fields
    """

    output_task = {}
    for field, content in task.items():
        output_task[prefix + field] = content

    return output_task.copy()  # Make sure we don't return a pointer


#/* ======================================================================= */#
#/*     Define main()
#/* ======================================================================= */#
def main(args):

    """
    Commandline logic
    """

    #/* ======================================================================= */#
    #/*     Defaults
    #/* ======================================================================= */#

    # I/O configuration
    overwrite_outfile = False
    field_prefix = '_t_'

    #/* ======================================================================= */#
    #/*     Containers
    #/* ======================================================================= */#

    # Input/output files
    task_file = None
    task_run_file = None
    output_file = None

    # JSON objects
    tasks = None
    task_runs = None
    output_json = None

    #/* ======================================================================= */#
    #/*     Parse Arguments
    #/* ======================================================================= */#

    arg_error = False
    i = 0
    while i < len(args):

        try:
            arg = args[i]

            # Help arguments
            if arg in ('--help-info', '-help-info', '--helpinfo', '-help-info'):
                return print_help_info()
            elif arg in ('--help', '-help', '--h', '-h'):
                return print_help()
            elif arg in ('--usage', '-usage'):
                return print_usage()
            elif arg in ('--version', '-version'):
                return print_version()
            elif arg in ('--license', '-usage'):
                return print_license()

            # I/O options
            elif arg in ('--overwrite', '-overwrite'):
                i += 1
                overwrite_outfile = True

            # Processing options
            elif '-prefix=' in arg:
                i += 1
                field_prefix = arg.split('=', 1)[1]

            # Positional arguments and errors
            else:

                # Catch task.json
                if task_file is None:
                    i += 1
                    task_file = arg

                # Catch task_run.json
                elif task_run_file is None:
                    i += 1
                    task_run_file = arg

                # Catch output.json
                elif output_file is None:
                    i += 1
                    output_file = arg

                # Catch errors
                else:
                    i += 1
                    arg_error = True
                    print("ERROR: Invalid argument: %s" % str(arg))

        except IndexError:
            arg_error = True
            print("ERROR: An argument has invalid parameters")

    #/* ======================================================================= */#
    #/*     Validate configuration
    #/* ======================================================================= */#

    bail = False

    # Check arguments
    if arg_error:
        bail = True
        print("ERROR: Did not successfully parse arguments")

    # Check task.json file
    if task_file is None:
        bail = True
        print("ERROR: Need a task.json file")
    if task_file is not None and not isfile(task_file):
        bail = True
        print("ERROR: Can't find task.json file: %s" % task_file)
    elif not os.access(task_run_file, os.R_OK):
        bail = True
        print("ERROR: Need read permission: %s" % task_file)

    # Check task_run.json file
    if task_run_file is None:
        bail = True
        print("ERROR: Need a task_run.json file")
    if task_run_file is not None and not isfile(task_run_file):
        bail = True
        print("ERROR: Can't find task_run.json file: %s" % task_run_file)
    elif not os.access(task_run_file, os.R_OK):
        bail = True
        print("ERROR: Need read permission: %s" % task_run_file)

    # Check output file
    if output_file is None:
        bail = True
        print("ERROR: Need an output file")
    if output_file is not None and isfile(output_file) and not overwrite_outfile:
        bail = True
        print("ERROR: Output file exists and overwrite=%s: %s" % (str(overwrite_outfile), output_file))
    elif not os.access(dirname(output_file), os.W_OK):
        bail = True
        print("ERROR: Need write permission: %s" % dirname(output_file))

    # Processing options
    if field_prefix == '':
        bail = True
        print("ERROR: Field prefix cannot be an empty string - this will cause data to be overwritten")

    # Exit if necessary
    if bail:
        return 1

    #/* ======================================================================= */#
    #/*     Load data
    #/* ======================================================================= */#

    print("Loading data...")

    # Load task.json
    with open(task_file, 'r') as f:
        tasks = json.load(f)
    print("  Found %s tasks" % str(len(tasks)))

    # Load task_run.json
    with open(task_run_file, 'r') as f:
        task_runs = json.load(f)
    print("  Found %s task runs" % str(len(task_runs)))

    #/* ======================================================================= */#
    #/*     Process Data
    #/* ======================================================================= */#

    print("Processing data...")

    output_json = []
    i = 0
    tot_tasks = len(task_runs)
    for tr in task_runs:

        # Update user
        i += 1
        sys.stdout.write("\r\x1b[K" + "  %s/%s" % (str(i), str(tot_tasks)))
        sys.stdout.flush()

        # Get task and update task run
        task = get_task(tr['task_id'], tasks)
        if task is None:
            print("  - SKIPPED: Did not find task for task run: %s" % tr['task_id'])
        else:
            task = adjust_fields(field_prefix, task)
            for field, content in task.items():
                tr[field] = content
            output_json.append(tr)

    #/* ======================================================================= */#
    #/*     Write Output
    #/* ======================================================================= */#

    print("")
    print("Writing output...")

    with open(output_file, 'w') as f:
        json.dump(output_json, f)

    #/* ======================================================================= */#
    #/*     Cleanup
    #/* ======================================================================= */#

    # Success
    print("Done.")
    return 0


#/* ======================================================================= */#
#/*     Command line execution
#/* ======================================================================= */#
if __name__ == '__main__':
    if len(sys.argv) > 1:
        sys.exit(main(sys.argv[1:]))
    else:
        sys.exit(print_usage())
