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
    print("Usage: %s [options] [input_files.json] output.json" % __docname__)
    print("")
    print("Options:")
    print("  --overwrite -> Overwrite output file if it already exists")
    print("")

    return 1


#/* ======================================================================= */#
#/*     Define print_help()
#/* ======================================================================= */#
def print_help():

    """
    Print more detailed help information
    """

    # TODO: Populate help

    print("")
    print("Detailed Help: %s" % __docname__)
    print("---------------" + "-" * len(__docname__))
    print("DETAILED HELP")
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
#/*     Define main()
#/* ======================================================================= */#
def main(args):

    """
    Commandline logic
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

            # Positional arguments and errors
            else:

                # Catch input files - NOTE: The output file will be stripped off before validating
                i += 1
                input_files.append(arg)

        except IndexError:
            arg_error = True
            print("ERROR: An argument has invalid parameters")

    # Get the output file
    if input_files is []:
        arg_error = True
        print("ERROR: Can't get output file out of arguments")
    else:
        output_file = input_files[-1]

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
        content = None
        with open(ifile, 'r') as f:
            content = json.load(f)
            output_json += content

    # Write output file
    print("Writing output file...")
    with open(output_file, 'w') as f:
        json.dump(output_json, f)

    #/* ======================================================================= */#
    #/*     Cleanup
    #/* ======================================================================= */#

    # Success
    print("Done.")
    return 0


#/* ======================================================================= */#
#/*     Commandline Execution
#/* ======================================================================= */#
if __name__ == '__main__':
    if len(sys.argv) > 1:
        sys.exit(main(sys.argv[1:]))
    else:
        sys.exit(print_usage())
