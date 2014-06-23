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
Join two JSON files together
"""


import os
import sys
import json
from os.path import *


__docname__ = basename(__file__)
__all__ = ['print_usage', 'print_help', 'print_license', 'print_help_info', 'print_version', 'main']


#/* ======================================================================= */#
#/*     Build information
#/* ======================================================================= */#

__version__ = '0.1-dev'
__release__ = '2014-06-02'
__copyright__ = 'Copyright 2014, SkyTruth'
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


#/* ======================================================================= */#
#/*     Define print_usage() function
#/* ======================================================================= */#

def print_usage():

    """
    Commandline usage

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    print("""
Usage:
    {0} --help-info
    {0} [options] infile1.json infile2.json [infile3.json ...] outfile.json

Options:
    --overwrite     Overwrite output file if it already exists
""".format(__docname__))

    return 1


#/* ======================================================================= */#
#/*     Define print_help() function
#/* ======================================================================= */#

def print_help():

    """
    Detailed help information

    :return: 1 for exit code purposes
    :rtype: int
    """

    print("""
Help: %s
------%s

Combine two or more JSON encoded files into a single output file.  Files are
processed in the order they are supplied, which means the first input file
will be at the beginning of the output file and the last input file will be
at the end of the output file.  Input JSON objects that are structured as a
list will simply be appended but dictionaries are first wrapped in a list
in order to be aggregated.


Combining Dictionaries
======================

Infile 1
--------
{'key1': {'subkey1': 'subval1'},
 'key2': 'val2',
 'key3': ['li1', 'li2', 'li3']}


Infile 2
--------
{'key4': {'subkey2': 'subval2'},
 'key5': 'val5',
 'key6': ['li4', 'li5', 'li6']}

Outfile
-------
[{'key1': {'subkey1': 'subval1'},
  'key2': 'val2',
  'key3': ['li1', 'li2', 'li3']},
 {'key4': {'subkey2': 'subval2'},
  'key5': 'val5',
  'key6': ['li4', 'li5', 'li6']}]


Combining Lists
===============

Infile 1
--------
[{'key1': {'subkey1': 'subval1'},
  'key2': 'val2',
  'key3': ['li1', 'li2', 'li3']},
 {'key4': {'subkey2': 'subval2'},
  'key5': 'val5',
  'key6': ['li4', 'li5', 'li6']}]

Infile 2
--------
[{'key7': {'subkey1': 'subval1'},
  'key8': 'val2',
  'key9': ['li1', 'li2', 'li3']},
 {'key10': {'subkey2': 'subval2'},
  'key11': 'val5',
  'key12': ['li4', 'li5', 'li6']}]

Outfile
-------
[{'key1': {'subkey1': 'subval1'},
  'key2': 'val2',
  'key3': ['li1', 'li2', 'li3']},
 {'key4': {'subkey2': 'subval2'},
  'key5': 'val5',
  'key6': ['li4', 'li5', 'li6']},
 {'key7': {'subkey1': 'subval1'},
  'key8': 'val2',
  'key9': ['li1', 'li2', 'li3']},
 {'key10': {'subkey2': 'subval2'},
  'key11': 'val5',
  'key12': ['li4', 'li5', 'li6']}]
    """ % (__docname__, '-' * len(__docname__)))

    return 1


#/* ======================================================================= */#
#/*     Define print_license() function
#/* ======================================================================= */#

def print_license():

    """
    Print out license information

    :return: 1 for exit code purposes
    :rtype: int
    """

    print(__license__)

    return 1


#/* ======================================================================= */#
#/*     Define print_help_info() function
#/* ======================================================================= */#

def print_help_info():

    """
    Print a list of help related flags

    :return: 1 for exit code purposes
    :rtype: int
    """

    print("""
Help flags:
    --help-info     This printout
    --help          More detailed description of this utility
    --usage         Arguments, parameters, flags, options, etc.
    --version       Version and ownership information
    --license       License information
    """)

    return 1


#/* ======================================================================= */#
#/*     Define print_version() function
#/* ======================================================================= */#

def print_version():

    """
    Print script version information

    :return: 1 for exit code purposes
    :rtype: int
    """

    print("""
%s version %s - released %s

%s
    """ % (__docname__, __version__, __release__, __copyright__))

    return 1


#/* ======================================================================= */#
#/*     Define main() function
#/* ======================================================================= */#

def main(args):

    """
    Commandline logic

    :param args: commandline arguments
    :type args: list|tuple
    :return: success returns 0 and failure returns 1
    :rtype: int
    """

    #/* ======================================================================= */#
    #/*     Defaults
    #/* ======================================================================= */#

    # I/O settings
    overwrite_output_file = False

    #/* ======================================================================= */#
    #/*     Containers
    #/* ======================================================================= */#

    # Input/output files
    input_files = []
    output_file = None

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

            # Output options
            elif arg == '--overwrite':
                i += 1
                overwrite_output_file = True

            # Positional arguments and errors
            else:

                # Catch input files - NOTE: The output file will be stripped off before validating
                i += 1
                input_files.append(arg)

        # An argument with parameters likely didn't iterate 'i' properly
        except IndexError:
            i += 1
            arg_error = True
            print("ERROR: An argument has invalid parameters")

    # Get the output file
    if input_files is []:
        arg_error = True
        print("ERROR: Can't get output file out of arguments")
    else:
        output_file = abspath(input_files.pop(-1))

    # Force input files to use absolute paths
    input_files = [abspath(i) for i in input_files]

    #/* ======================================================================= */#
    #/*     Validate
    #/* ======================================================================= */#

    bail = False

    # Check arguments
    if arg_error:
        bail = True
        print("ERROR: Did not successfully parse arguments")

    # Input files
    if len(input_files) < 2:
        bail = True
        print("ERROR: Need at least 2 input files - received %s" % str(len(input_files)))
    else:
        for ifile in input_files:
            if not isfile(ifile):
                bail = True
                print("ERROR: Can't find input file: %s" % ifile)
            elif not os.access(ifile, os.R_OK):
                bail = True
                print("ERROR: Need read permission: %s" % ifile)

    # Output file
    if output_file is None:
        bail = True
        print("ERROR: Need an output file")
    if output_file is not None and isfile(output_file) and not overwrite_output_file:
        bail = True
        print("ERROR: Output file exists and overwrite=%s: %s" % (str(overwrite_output_file), output_file))
    elif not os.access(dirname(output_file), os.W_OK):
        bail = True
        print("ERROR: Need write permission: %s" % dirname(output_file))

    if bail:
        return 1

    #/* ======================================================================= */#
    #/*     Process files
    #/* ======================================================================= */#

    # Loop through input files and aggregate content
    print("Processing %s files ..." % str(len(input_files)))
    output_json = []
    for ifile in input_files:
        with open(ifile, 'r') as f:

            content = json.load(f)

            # Input is a dictionary - wrap it in a list in to allow concatenation
            if isinstance(content, dict):
                content = [content]

            output_json += content

    # Write output file
    print("Writing output file ...")
    with open(output_file, 'w') as f:
        json.dump(output_json, f)

    #/* ======================================================================= */#
    #/*     Cleanup
    #/* ======================================================================= */#

    # Success
    print("Done.")
    return 0


#/* ======================================================================= */#
#/*     Command Line Execution
#/* ======================================================================= */#

if __name__ == '__main__':

    # Didn't get enough arguments - print usage
    if len(sys.argv) is 1:
        sys.exit(print_usage())

    # Got enough arguments - drop the first argument since its the script name and give the rest to main()
    else:
        sys.exit(main(sys.argv[1:]))
