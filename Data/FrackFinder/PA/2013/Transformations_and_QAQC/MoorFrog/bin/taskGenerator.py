#!/usr/bin/env python


# This document is part of CrowdProjects
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
Generate MoorFrog input tasks from Tadpole output


Internal Query:
"p_crd_a" >= 66 AND "crowd_sel" = 'pad'


Public Query:
"p_crd_a" >= 70
"""


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


import os
import sys
import json
from os.path import *
try:
    from osgeo import ogr
except ImportError:
    import ogr


__docname__ = basename(__file__)
__all__ = ['print_usage', 'print_help', 'print_license', 'print_help_info', 'print_version', 'main']


# Build information
__author__ = 'Kevin Wurster'
__release__ = '2014-06-02'
__version__ = '0.1-dev'


#/* ======================================================================= */#
#/*     Define print_usage() Function
#/* ======================================================================= */#

def print_usage():

    """
    Print commandline usage

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    print("""
Usage: %s [options] [input_files.json] output.json

Options:
  --overwrite -> Overwrite output file if it already exists
    """ % __docname__)

    return 1


#/* ======================================================================= */#
#/*     Define print_help() Function
#/* ======================================================================= */#

def print_help():

    """
    Print more detailed help information

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    print("""
Help: {0}
------{1}
DETAILED HELP
    """.format(__docname__, '-' * len(__docname__)))

    return 1


#/* ======================================================================= */#
#/*     Define print_license() Function
#/* ======================================================================= */#

def print_license():

    """
    Print licensing information

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    print(__license__)

    return 1


#/* ======================================================================= */#
#/*     Define print_help_info() Function
#/* ======================================================================= */#

def print_help_info():

    """
    Print a list of help related flags

    :return: returns 1 for for exit code purposes
    :rtype: int
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
#/*     Define print_version() Function
#/* ======================================================================= */#

def print_version():

    """
    Print the module version information

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    print("""
%s version %s - released %s"
    """ % (__docname__, __version__, __release__))

    return 1


#/* ======================================================================= */#
#/*     Define main()
#/* ======================================================================= */#

def main(args):

    """
    Commandline logic

    :param args: commandline arguments from sys.argv[1:]
    :type args: list|tuple

    :return: 0 on success and 1 on failure
    :rtype: int
    """

    #/* ======================================================================= */#
    #/*     Defaults
    #/* ======================================================================= */#

    # Additional options
    overwrite_mode = False

    #/* ======================================================================= */#
    #/*     Containers
    #/* ======================================================================= */#

    infile = None
    outfile = None
    input_query = None

    #/* ======================================================================= */#
    #/*     Parse Arguments
    #/* ======================================================================= */#

    i = 0
    arg_error = False
    arg = None

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

            # Processing options
            elif arg in ('--query', '-query'):
                i += 2
                input_query = args[i - 1]

            # Additional options
            elif arg in ('--overwrite', '-overwrite'):
                i += 1
                overwrite_mode = True

            # Positional arguments and errors
            else:

                # Catch infile
                if infile is None:
                    i += 1
                    infile = arg

                # Catch outfile
                elif outfile is None:
                    i += 1
                    outfile = arg

                # Errors
                else:
                    i += 1
                    print("ERROR: Unrecognized argument: %s" % arg)

        # An argument with parameters likely didn't iterate 'i' properly
        except IndexError:
            i += 1
            arg_error = True
            print("ERROR: An argument has invalid parameters: %s" % arg)

    #/* ======================================================================= */#
    #/*     Validate
    #/* ======================================================================= */#ki

    bail = False

    # Check arguments
    if arg_error:
        bail = True
        print("ERROR: Did not successfully parse arguments")

    # Check input file
    if infile is None:
        bail = True
        print("ERROR: Need an input file")
    elif not isfile(infile) or not os.access(infile, os.R_OK):
        bail = True
        print("ERROR: Can't find input file or need write access: %s" % infile)

    # Check output file
    if outfile is None:
        bail = True
        print("ERROR: Need an outfile")
    elif overwrite_mode and isfile(outfile):
        bail = True
        print("ERROR: Overwrite=%s and outfile exists: %s" % (str(overwrite_mode), outfile))

    if bail:
        return 1

    #/* ======================================================================= */#
    #/*     Load Data
    #/* ======================================================================= */#

    # Load input OGR datasource
    datasource = ogr.Open(infile)
    layer = datasource.GetLayer()
    layer.SetAttributeFilter(input_query)

    #/* ======================================================================= */#
    #/*     Process OGR Datasource
    #/* ======================================================================= */#

    task_template = {}

    #/* ======================================================================= */#
    #/*     Cleanup
    #/* ======================================================================= */#

    # Success
    return 0


#/* ======================================================================= */#
#/*     Commandline Execution
#/* ======================================================================= */#

if __name__ == '__main__':

    # Didn't get enough arguments - print usage and exit
    if len(sys.argv) is 1:
        sys.exit(print_usage())

    # Got enough arguments - give sys.argv[1:] to main()
    else:
        sys.exit(main(sys.argv[1:]))
