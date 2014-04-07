#!/usr/bin env python


# See global __license__ variable for license information


"""
Compare two task.json files from PyBossa and keep/remove
unique/non-unique tasks.
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
    """
    print("")
    print("Usage: %s [options] *.json outfile.json" % __docname__)
    print("")
    print("Options:")
    print("  --help-info -> Print out a list of help related flags")
    print("  --unique    -> Write tasks that are unique in *.json files")
    print("  --overlap   -> Write tasks that exist in *.json files")
    print("  --include|-i file -> Only include tasks in file")
    print("  --exclude|-e file -> Exclude tasks in file")
    print("")
    print("Utility defaults to --overlap mode")
    print("When using -i/-e the -i filtering happens before -e")
    print("")
    return 1


def print_version():
    """
    Print version and ownership information
    """
    print("")
    print('%s version %s - released %s' % (__docname__, __version__, __release__))
    print("")
    return 1


def print_short_version():
    """
    Just print the version number for commandline comparison purposes
    """
    print(__version__)
    return 1


def print_license():
    """
    Print licensing information
    """
    print('\n' + __license__ + '\n')
    return 1


def main(args):

    # Set defaults
    outfile = None
    compare_files = []
    comparison = 'overlap'
    exclusion_files = []
    inclusion_files = []

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
                mode = 'unique'
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

    # Make sure files exist, arguments were populated, ranges check out, etc



    # Success
    return 0


if __name__ == '__main__':
    if len(sys.argv) is 1:
        sys.exit(print_usage())
    else:
        sys.exit(main(sys.argv[1:]))
