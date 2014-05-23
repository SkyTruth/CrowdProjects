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


"""
./userAnalyzer.py ../FrackFinder/Global_QAQC/dartfrog/transform/public/tasks/task_run.json TEST.csv
"""


from __future__ import division

import sys
import json
from os import linesep
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
    print("Usage: %s --help-info [options] task_run.json outfile.csv" % basename(__file__))
    print("")
    print("Options:")
    print("  --classify-skiplines=int  ->  Skip n lines if classifying from an input file")
    print("  --classify-ids id=class   ->  Normalized user ID and user defined classification str")
    print("  --overwrite  ->  Overwrite the outfile.csv")
    print("  --inverse-classify-ids id=class  ->  Normalized user ID and user defined classification str")
    print("")

    return 1


def print_help():

    """
    Detailed help information
    """

    print("")
    print("%s Detailed Help" % basename(__file__))
    print("--------------" + "-" * len(basename(__file__)))
    print("Transforms a task_run.json file into a CSV with one line per user and a set of attributes.")
    print("Attributes are as follows:")
    print("  n_uid    = Normalized user ID taken from user_id when populated and user_ip otherwise")
    print("  user_id  = Taken from user_id if available - null otherwise")
    print("  user_ip  = Taken from user_ip if available - null otherwise")
    print("  uid_type = Specifies whether n_uid came from user_id or user_ip")
    print("  start_date = The date the user completed their first task run")
    print("  end_date   = The most recent date a user completed a task run")
    print("Running without any arguments counts everything in the current directory")
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

    This comes from the task_run.json file: task_run['created / finish_time']
    """

    return datetime.strptime(input_datetime_stamp, "%Y-%m-%dT%H:%M:%S.%f")


def datetime_formatter(input_datetime_object, strfmt='%Y-%m-%d %H:%M:%S.%f'):

    """
    Convert a datetime object to a single normalized time format readable by Excel
    """
    if input_datetime_object is None:
        return None
    else:
        return input_datetime_object.strftime(strfmt)


def row_formatter(row, qualifier='"'):

    """
    Format a row in a consistent way
    """

    output_row = []
    for item in row:
        if item is None:
            item = '""'
        else:
            item = qualifier + str(item) + qualifier
        output_row.append(item)

    return output_row


def id_classification_processor(id_classification, skip_lines):

    """
    Convert commandline --classify-id ids=class parameter to a dictionary
    """

    # Transform ID's
    o_dict = {}
    for ids, classification in id_classification.items():
        if isfile(ids):
            try:
                with open(ids, 'r') as f:
                    for line in f.readlines()[skip_lines:]:
                        o_dict[line.replace(linesep, '').strip()] = classification
            except OSError:
                print("ERROR: ID classifier is a file that cannot be opened: %s" % ids)
                return 1
        elif ',' in ids:
            for i in ids.split(','):
                o_dict[i] = classification

    # Success
    return o_dict.copy()


def inverse_id_classification_processor(inverse_id_classification, skip_lines):

    """
    Convert commandline --inverse-classify-id ids=class parameter to a dictionary
    """

    # Transform ID's
    output = []
    for ids, classification in inverse_id_classification.items():
        if isfile(ids):
            try:
                with open(ids, 'r') as f:
                    id_set = []
                    for line in f.readlines()[skip_lines:]:
                        id_set.append(line.replace(linesep, '').strip())
                    output.append((id_set, classification))
            except OSError:
                print("ERROR: ID classifier is a file that cannot be opened: %s" % ids)
                return 1
        elif ',' in ids:
            id_set = []
            for i in ids.split(','):
                id_set.append(i)
            output.append((id_set, classification))

    # Success
    return output


def main(args):

    """
    Main command line logic
    """

    #/* ======================================================================= */#
    #/*     Set Defaults
    #/* ======================================================================= */#

    # Input/output files
    input_task_runs_file = None
    output_csv = None

    # Parameters/configuration
    sample_size = None
    overwrite_outfile = False
    id_classification = {}
    inverse_id_classification = {}
    classify_skipline = 0

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

            # User ID classification
            elif arg in ('--classify-ids', '--classify-id'):
                i += 1
                while i < len(args) and args[i][0] != '-':
                    ids, classification = args[i].split('=', 1)
                    id_classification[ids] = classification
                    i += 1
            elif '--classify-skiplines=' in arg or '--classify-skipline=' in arg:
                i += 1
                try:
                    classify_skipline = int(arg.split('=', 1)[1])
                except ValueError:
                    arg_error = True
                    print("ERROR: Invalid classify skiplines - must be an int: %s" % arg)
            elif arg in ('--inverse-classify-ids', '--inverse-classify-id'):
                i += 1
                while i < len(args) and args[i][0] != '-':
                    ids, classification = args[i].split('=', 1)
                    inverse_id_classification[ids] = classification
                    i += 1

            # Additional parameters
            elif '--overwrite' in arg:
                i += 1
                overwrite_outfile = True

            elif '--sample=' in arg:
                i += 1
                try:
                    sample_size = int(arg.split('=', 1)[1])
                except ValueError:
                    arg_error = True
                    print("ERROR: Invalid sample value - must be an int: %s" % arg)

            # Positional arguments and errors
            else:

                # Catch input file
                if input_task_runs_file is None:
                    i += 1
                    input_task_runs_file = arg
                elif output_csv is None:
                    i += 1
                    output_csv = arg
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
    if output_csv is None:
        print("ERROR: Need an output file")
        bail = True
    if output_csv is not None and isfile(output_csv) and not overwrite_outfile:
        print("ERROR: Outfile exists and overwrite=%s: %s" % (str(overwrite_outfile), output_csv))
        bail = True
    if input_task_runs_file is None or not isfile(input_task_runs_file):
        print("ERROR: Can't find file: %s" % str(input_task_runs_file))
        bail = True
    if sample_size is not None and sample_size <= 0:
        print("ERROR: Invalid sample size - must be > 0: %s" % str(sample_size))
        bail = True
    if bail:
        return 1

    #/* ======================================================================= */#
    #/*     Transform ID classification stuff - files and arguments
    #/* ======================================================================= */#

    # Transform ID's
    if id_classification != {}:
        id_classification = id_classification_processor(id_classification, classify_skipline)
    if inverse_id_classification != {}:
        inverse_id_classification = inverse_id_classification_processor(inverse_id_classification, classify_skipline)

    #/* ======================================================================= */#
    #/*     Aggregate Task Runs and Users
    #/* ======================================================================= */#

    # Update user
    print("Analyzing task runs ...")

    # Load input file
    task_runs = None
    with open(input_task_runs_file) as f:
        task_runs = json.load(f)

    # If we're doing a sample, grab it
    if sample_size is not None:
        if sample_size > len(task_runs):
            sample_size = len(task_runs)
            print("WARNING: Sample size larger than input - adjusted to: %s" % str(sample_size))
        task_runs = task_runs[:sample_size]

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

        # Collect IDs and add to the stats container
        if nuid not in stats:
            stats[nuid] = {'uid_type': utype,
                           'user_id': uid,
                           'user_ip': uip,
                           'n_uid': nuid,
                           'tr': [],
                           'num_tasks_completed': 0,
                           'start_date': None,
                           'end_date': None,
                           'avg_task_time_seconds': [],
                           'engaged_days': None}
        if id_classification != {} or inverse_id_classification != {}:
            stats[nuid]['classification'] = None

        # Classify ID
        if inverse_id_classification is not {}:
            for t in inverse_id_classification:
                id_set, classification = t
                if str(nuid) not in id_set:
                    stats[nuid]['classification'] = classification
        if id_classification is not {}:
            if str(nuid) in id_classification:
                stats[nuid]['classification'] = id_classification[str(nuid)]

        # Add to task runs and update count
        stats[nuid]['tr'].append(tr)
        stats[nuid]['num_tasks_completed'] += 1

#/* ======================================================================= */#
#/*     Analyze Task Runs
#/* ======================================================================= */#

    # Loop through all collected user's and compute metrics
    for nuid in stats.keys():

        # Time metrics for collected task runs
        start_date = None
        end_date = None
        for c_tr in stats[nuid]['tr']:

            # Get the collected task_run's start/end date and start/end time
            # Sometimes stuff isn't populated for whatever reason so we have to try/except each set
            try:
                task_time_seconds = round(c_tr['info']['timings']['presentTask'] / 1000, 2)
                stats[nuid]['avg_task_time_seconds'].append(task_time_seconds)
            except KeyError:
                pass
            try:
                c_start_date = date2datetime(c_tr['created'])
                c_end_date = date2datetime(c_tr['finish_time'])
            except KeyError:
                c_start_date = None
                c_end_date = None

            # Handle start/end date
            if start_date is None or c_start_date < start_date:
                start_date = c_start_date
            if end_date is None or c_end_date > end_date:
                end_date = c_end_date

        # Dump start date, end date, and average task completion time into stats object
        engaged_days = (end_date - start_date).days
        if engaged_days is 0 and stats[nuid]['num_tasks_completed'] > 0:
            engaged_days = 1
        stats[nuid]['engaged_days'] = engaged_days
        stats[nuid]['start_date'] = datetime_formatter(start_date)
        stats[nuid]['end_date'] = datetime_formatter(end_date)
        avg_task_time = sum(stats[nuid]['avg_task_time_seconds']) / len(stats[nuid]['avg_task_time_seconds'])
        stats[nuid]['avg_task_time_seconds'] = avg_task_time

    # Done analyzing task runs - update user
    print("  - Done")

#/* ======================================================================= */#
#/*     Write Output CSV
#/* ======================================================================= */#

    # Write output csv
    print("Processing CSV rows ...")

    # Define header structure and containers
    header = ['n_uid', 'user_id', 'user_ip', 'uid_type', 'start_date', 'end_date', 'engaged_days',
              'num_tasks_completed', 'avg_task_time_seconds']
    if id_classification != {} or inverse_id_classification != {}:
        header.insert(8, 'classification')
    output_rows = [header]

    # Convert the stats container to CSV rows
    ri = 0
    for uid, attributes in stats.items():

        ri += 1
        sys.stdout.write("\r\x1b[K" + "  %s/%s" % (str(ri), str(len(stats.keys()))))
        sys.stdout.flush()

        # Stick items into the proper place, according to the header, convert data types, and add text qualifiers
        row = ['' for i in header]
        for item in header:
            row[header.index(item)] = attributes[item]
        output_rows.append(row)
    print("  - Done")

    # Write the file
    print("Writing output file: %s" % output_csv)
    with open(output_csv, 'w') as f:
        for row in output_rows:
            f.write(','.join(row_formatter(row)) + linesep)

    # Success
    return 0


#/* ======================================================================= */#
#/*     Executing from Commandline
#/* ======================================================================= */#

if __name__ == '__main__':
    if len(sys.argv) > 1:
        sys.exit(main(sys.argv[1:]))
    else:
        sys.exit(print_usage())
