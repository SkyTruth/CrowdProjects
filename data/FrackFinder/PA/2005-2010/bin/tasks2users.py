#!/usr/bin/env python


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


import sys
import json
from os.path import *
from os import linesep
from datetime import datetime


# Build information
__author__ = 'Kevin Wurster'
__copyright__ = 'Copyright (c) 2014, SkyTruth'
__version__ = '0.1-dev'
__release__ = '2014/05/06'
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
"""


def print_usage():

    """
    Print commandline usage information
    """

    print("")
    print("Usage: %s task_run.json output.csv" % basename(__file__))
    print("")

    return 1


def print_help():

    """
    Print a more detailed help description
    """

    print("")
    print("DETAILED HELP GOES HERE")
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


def print_version():

    """
    Print the module version information
    """

    print("")
    print("%s version %s - released %s" % (basename(__file__), __version__, __release__))
    print("")

    return 1


def print_license():

    """
    Print licensing information
    """

    print(__license__)

    return 1


def row_formatter(row, qualifier='"'):

    """
    Format a row in a consistent way
    """

    output_row = []
    for item in row:
        if item is None:
            item = '""'
        elif str(item)[0] is '2' and 'T' in str(item):
            item = qualifier + datetime.strptime(item, "%Y-%m-%dT%H:%M:%S.%f").strftime("%m/%d/%Y %H:%M:%S") + qualifier
        else:
            item = qualifier + str(item) + qualifier
        output_row.append(item)

    return output_row


def main(args):

    """
    Convert a set of task_run.json to user attributes with 1 row per task
    """

    # Containers
    input_task_runs_file = None
    output_csv_file = None

    # Defaults
    overwrite_output = False

    # Parse arguments
    arg_error = False
    for arg in args:

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

        # Additional options
        elif arg in ('-overwrite', '--overwrite'):
            overwrite_output = True

        # Other arguments are positional
        else:
            if input_task_runs_file is None:
                input_task_runs_file = arg
            elif output_csv_file is None:
                output_csv_file = arg
            else:
                print("ERROR: Invalid argument: %s" % arg)
                arg_error = True

    # -+== Validate ==+- #

    # Make sure all requirements are met before proceeding
    bail = False
    if arg_error:
        print("ERROR: Did not successfully parse arguments")
        bail = True
    if not isfile(input_task_runs_file):
        print("ERROR: Can't find input task runs: %s" % input_task_runs_file)
        bail = True
    if output_csv_file is None:
        print("ERROR: Need an output file")
        bail = True
    if isfile(output_csv_file) and not overwrite_output:
        print("ERROR: Outfile exists: %s" % output_csv_file)
        bail = True
    if bail:
        return 1

    # -+== Analyze JSON ==+- #

    print("Analyzing: %s" % input_task_runs_file)

    # Define header structure and containers
    header = ['user_id', 'user_ip', 'task_id', 'created', 'finish_time']
    output_rows = [header]

    # Open the input file for processing
    with open(input_task_runs_file, 'r') as f:

        # Convert file to a JSON object
        task_runs = json.load(f)

        # Loop through all task runs
        for tr in task_runs:

            # Stick items into the proper place, according to the header, convert data types, and add text qualifiers
            row = ['' for i in header]
            for item in header:
                row[header.index(item)] = tr[item]
            output_rows.append(row)

    # Write the output file
    print("Writing: %s" % output_csv_file)
    with open(output_csv_file, 'w') as f:
        for row in output_rows:
            f.write(','.join(row_formatter(row)) + linesep)

    # Success
    return 0


if __name__ == '__main__':
    if len(sys.argv) is 1:
        sys.exit(print_usage())
    else:
        sys.exit(main(sys.argv[1:]))
