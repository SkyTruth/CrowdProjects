#!/usr/bin/env python


# =================================================================================== #
#
# New BSD License
#
# Copyright (c) 2014, Kevin D. Wurster
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


import sys
import json
from datetime import datetime
from pprint import pprint
from os.path import isfile
from os.path import basename


# Build information
__version__ = '0.1-dev'
__release__ = '05/19/14'
__author__ = 'Kevin Wurster'
__license__ = '''
New BSD License

Copyright (c) 2014, SkyTruth
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


def print_usage():

    """
    Print commandline usage information
    """

    print("")
    print("Usage: %s --help-info [options]" % basename(__file__))
    print("")

    return 1


def print_help():

    """
    Detailed help information
    """

    print("")
    print("HELP DESCRIPTION")
    print("")

    return 1


def print_version():

    """
    Print the module version information
    """

    print("")
    print("%s version %s - released %s" % (basename(__file__), __version__, __release__))
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
    print("")

    return 1


def print_license():

    """
    Print licensing information
    """

    print(__license__)

    return 1


def get_task_runs(nuid, utype, task_runs):

    """
    Return a list of all tasks completed by a given user
    """

    task_run_list = []
    for tr in task_runs:
        if utype == 'id':
            if str(tr['user_id']) == nuid:
                task_run_list.append(tr)
        elif utype == 'ip':
            if str(tr['user_ip']) == nuid:
                task_run_list.append(tr)
        else:
            raise ValueError("Invalid nuid=%s" % str(nuid))

    return task_run_list


def date2datetime(input_datetime_stamp):

    """
    Convert PyBossa's XML formatted datetime to a Python datetime object

    Note that microseconds are dropped completely
    """

    return datetime.strptime(input_datetime_stamp, "%Y-%m-%dT%H:%M:%S.%f").replace(microsecond=0)


def main(args):

    #/* ======================================================================= */#
    #/*     Set Defaults
    #/* ======================================================================= */#

    # Input/output files
    input_task_runs_file = None

    #/* ======================================================================= */#
    #/*     Parse Arguments
    #/* ======================================================================= */#
    arg_error = False
    i = 0
    while i < len(args):

        try:
            arg = args[i]

            # Help arguments
            if arg in ('--help-info', '-helpinfo', '-help-info', '--helpinfo'):
                return print_help_info()
            elif arg in ('--help', '-help', '-h'):
                return print_help()
            elif arg in ('--usage', '-usage'):
                return print_usage()
            elif arg in ('--version', '-version'):
                return print_version()
            elif arg in ('--license', '-license'):
                return print_license()

            # Positional arguments and errors
            else:

                # Catch input file
                if input_task_runs_file is None:
                    i += 1
                    input_task_runs_file = arg
                else:
                    i += 1
                    print("ERROR: Invalid argument: %s" % str(arg))
                    arg_error = True

        except IndexError:
            i += 1
            print("ERROR: An argument has invalid parameters")
            arg_error = True

    #/* ======================================================================= */#
    #/*     Validate Parameters/Settings/Arguments
    #/* ======================================================================= */#

    bail = False
    if arg_error:
        print("ERROR: Did not successfully parse arguments")
        bail = True
    if input_task_runs_file is None or not isfile(input_task_runs_file):
        print("ERROR: Can't find file: %s" % str(input_task_runs_file))
        bail = True
    if bail:
        return 1

    #/* ======================================================================= */#
    #/*     Analyze Task Runs
    #/* ======================================================================= */#

    # Load input file
    task_runs = None
    with open(input_task_runs_file) as f:
        task_runs = json.load(f)

    # Define containers
    stats = {}
    i = 0
    tot_task_runs = len(task_runs)
    for tr in task_runs:

        # Update user
        i += 1
        sys.stdout.write("\r\x1b[K" + "  %s/%s" % (str(i), str(tot_task_runs)))
        sys.stdout.flush()

        # Get user identification
        uid = tr['user_id']
        utype = 'id'
        uip = tr['user_ip']
        nuid = str(uid)
        if uip is not None and uip.replace('.', '').isdigit():
            utype = 'ip'
            nuid = uip

        # Collect user ID stats
        stats[nuid] = {'uid_type': utype,
                       'user_id': uid,
                       'user_ip': uip,
                       'n_uid': nuid}

        # Get all task runs the user completed
        completed_task_runs = get_task_runs(nuid, utype, task_runs)
        stats[nuid]['tr'] = completed_task_runs
        stats[nuid]['num_completed'] = len(completed_task_runs)

        # Compute metrics for completed task runs
        start_date = None
        end_date = None
        avg_completion_time = None
        for c_tr in completed_task_runs:

            c_sd = date2datetime(c_tr['created'])
            c_ed = date2datetime(c_tr['finish_time'])

            # Compute average completion time per task run
            if avg_completion_time is None:
                avg_completion_time = c_ed - c_sd
            else:
                avg_completion_time = (avg_completion_time + c_ed - c_sd) / 2

            # Figure out if the date of the very first task the user completed and the very last task
            if start_date is None or c_sd < start_date:
                start_date = c_sd
            if end_date is None or c_ed > end_date:
                end_date = c_ed

            # Dump collected information into stats
            stats[nuid]['first_date'] = start_date.strftime("%m/%d/%Y %H:%M:%S")
            stats[nuid]['end_date'] = end_date.strftime("%m/%d/%Y %H:%M:%S")
            stats[nuid]['avg_time'] = str(avg_completion_time)



            ####### FIX AVG TIME CALCULATOR #######
            stats[nuid]['tr'] = None
            pprint(stats[nuid])
            return 1


    # Success
    return 0


if __name__ == '__main__':
    if len(sys.argv) > 1:
        sys.exit(main(sys.argv[1:]))
    else:
        sys.exit(print_usage())
