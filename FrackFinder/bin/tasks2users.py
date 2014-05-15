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


def main(args):

    """
    Convert a set of task_run.json to user attributes with 1 row per task
    """

    # Containers
    input_task_runs_file = None
    output_csv_file = None

    # Parse arguments
    arg_error = True
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

        # Other arguments are positional
        else:
            if input_task_runs_file is None:
                input_task_runs_file.append(arg)
            else:
                print("ERROR: Invalid argument: %s" % arg)
                arg_error = True

    # -+== Validate ==+- #

    # Make sure all requirements are met before proceeding
    bail = False
    if arg_error:
        print("ERROR: Did not successfully parse arguments")
        bail = True
    for infile in input_task_runs_file:
        if not isfile(infile):
            print("ERROR: Can't find input task runs: %s" % infile)
            bail = True
    if bail:
        return 1

    # -+== Analyze JSON ==+- #

    with open(input_task_runs_file, 'r') as f:
        task_runs = json.load(f)





if __name__ == '__main__':
    if len(sys.argv) is 1:
        sys.exit(print_usage())
    else:
        sys.exit(main(sys.argv[1:]))
