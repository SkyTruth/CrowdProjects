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
Add/delete fields
"""


import os
import sys
import json
from os.path import *


__docname__ = basename(__file__)
__all__ = ['print_usage', 'print_help', 'print_license', 'print_help_info', 'print_version', 'main']


# Build information
__author__ = 'Kevin Wurster'
__release__ = '2014-06-03'
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
    print("Usage: %s --help-info [options] input.json output.json" % __docname__)
    print("")
    print("Options:")
    print("  -e field=val -> Edit a field and set it equal to value")
    print("  -r field=new -> Rename a field")
    print("  -d fields    -> Delete field")
    print("  --overwrite  -> Overwrite output file")
    print("  --edit-add   -> Do not modify existing fields - only create")
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

    :param args: arguments from the commandline
    :type args: list|tuple

    :return: return 0 on success and 1 on error
    :rtype: int
    """

    #/* ======================================================================= */#
    #/*     Defaults
    #/* ======================================================================= */#

    overwrite_outfile = False
    edit_command_adds = False

    #/* ======================================================================= */#
    #/*     Containers
    #/* ======================================================================= */#

    # Input/output files
    infile = None
    outfile = None

    # Retain the processing argument order so processing order can be specified by the user
    processing_chain = []

    #/* ======================================================================= */#
    #/*     Parse Arguments
    #/* ======================================================================= */#

    i = 0
    arg_error = False
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

            # Processing flags
            elif arg in ('-e', '-d', '-r'):
                processing_chain.append(arg)
                i += 1
                while i < len(args) and args[i][0] != '-':
                    processing_chain.append(args[i])
                    i += 1

            # Additional processing options
            elif arg in ('--edit-add', '-edit-add'):
                i += 1
                edit_command_adds = True

        except IndexError:
            arg_error = True
            print("ERROR: An argument has invalid parameters")


    #/* ======================================================================= */#
    #/*     Validate
    #/* ======================================================================= */#

    bail = True

    # Check arguments
    if arg_error:
        bail = True
        print("ERROR: Did not successfully parse arguments")

    # Check input file
    if infile is None:
        bail = True
        print("ERROR: Need an input file")
    elif not isfile(infile):
        bail = True
        print("ERROR: Can't find input file: %s" % infile)
    elif not os.access(infile, os.R_OK):
        bail = True
        print("ERROR: Need read access: %s" % infile)

    # Check output file
    if outfile is None:
        bail = True
        print("ERROR: Need an output file: %s" % outfile)
    elif isfile(outfile) and not overwrite_outfile:
        bail = True
        print("ERROR: Output file exists and overwrite=%s: %s" % (str(overwrite_outfile), outfile))
    elif isfile(outfile) and overwrite_outfile and not os.access(outfile, os.W_OK):
        bail = True
        print("ERROR: Need write access for output file: %s" % outfile)
    elif not isfile(outfile) and not os.access(dirname(outfile), os.W_OK):
        bail = True
        print("ERROR: Need write access for output directory: %s" % dirname(outfile))

    # Make sure there's something to process
    if processing_chain is []:
        bail = True
        print("ERROR: No processing flags supplied - nothing to do")

    if bail:
        return 1

    #/* ======================================================================= */#
    #/*     Process Fields
    #/* ======================================================================= */#

    # Open input JSON
    print("Parsing infile: %s" % infile)
    with open(infile, 'r') as f:
        infile_content = json.load(f)
    print("  Found %s records" % len(infile_content))

    # Process fields
    print("Processing fields...")
    i = 0
    content_count = len(infile_content)
    while i < len(processing_chain):

        try:
            command = processing_chain[i]

            # Edit fields
            if command == '-e':
                i += 1
                while i < len(processing_chain) and processing_chain[i][0] != '-':

                    # Get the parameters
                    field, value = processing_chain[i].split('=', 1)

                    # Update user
                    print("  Editing: %s -> %s with edit_add=%s" % (field, value, str(edit_command_adds)))

                    # Make edits
                    loop_count = 0
                    for item in infile_content:
                        if edit_command_adds and field not in item:
                            item[field] = value
                        else:
                            item[field] = value

                        # Print progress
                        loop_count += 1
                        sys.stdout.write("\r\x1b[K" + "  %s/%s" % (str(loop_count), str(content_count)))
                        sys.stdout.flush()

                    # Loop iteration
                    i += 1

            # Rename fields
            elif command == '-r':
                i += 1
                while i < len(processing_chain) and processing_chain[i][0] != '-':

                    # Get the parameters
                    old_name, new_name = processing_chain[i].split('=', 1)

                    # Update user
                    print("  Renaming: %s -> %s" % (old_name, new_name))

                    # Do renaming
                    loop_count = 0
                    for item in infile_content:
                        if old_name in item:
                            value = item[old_name]
                            item[new_name] = value
                            del old_name

                        # Print progress
                        loop_count += 1
                        sys.stdout.write("\r\x1b[K" + "  %s/%s" % (str(loop_count), str(content_count)))
                        sys.stdout.flush()

                    # Loop iteration
                    i += 1

            # Delete fields
            elif command == '-d':
                i += 1
                while i < len(processing_chain) and processing_chain[i][0] != '-':

                    # Get the parameters
                    delete_field = processing_chain[i]

                    # Do deleting
                    loop_count = 0
                    for item in infile_content:
                        if delete_field in item:
                            del item[delete_field]

                        # Print progress
                        loop_count += 1
                        sys.stdout.write("\r\x1b[K" + "  %s/%s" % (str(loop_count), str(content_count)))
                        sys.stdout.flush()

                    # Loop iteration
                    i += 1

            # Catch errors
            else:
                i += 1
                print("ERROR: Something has gone wrong while processing - no data changed")
                print("       Received command: %s" % command)
                return 1

        except IndexError:
            i += 1
            print("ERROR: A processing command has invalid parameters - no data changed")

    #/* ======================================================================= */#
    #/*     Write Output
    #/* ======================================================================= */#

    # Blindly write output file since we already checked for --overwrite in the validation stage
    with open(outfile, 'w') as f:
        json.dump(infile_content, f)

    #/* ======================================================================= */#
    #/*     Cleanup
    #/* ======================================================================= */#

    # Success
    return 0


#/* ======================================================================= */#
#/*     Command line execution
#/* ======================================================================= */#

if __name__ == '__main__':
    if len(sys.argv) > 1:
        sys.exit(main(sys.argv[1:]))
    else:
        sys.exit(print_usage())
