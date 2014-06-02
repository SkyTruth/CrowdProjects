#!/usr/bin/env python


# This document is part of CrowdTools
# https://github.com/SkyTruth/CrowdTools


# =================================================================================== #
#
# New BSD License
#
# Copyright (c) 2014, Kevin D. Wurster, SkyTruth
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


import sys
from os.path import *


__author__ = 'Kevin Wurster'
__release__ = '2014-06-02'
__version__ = '0.1-dev'

__docname__ = basename(__file__)
__all__ = ['print_usage', 'print_help', 'print_license', 'print_help_info', 'print_version', 'main']

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
    print("Usage: %s task.json task_run.json outfile.json" % __docname__)
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
    print("%s Detailed Help" % __docname__)
    print("--------------" + "-" * len(__docname__))
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

    #/* ======================================================================= */#
    #/*     Defaults
    #/* ======================================================================= */#

    # Input/output files
    task_file = None
    task_run_file = None
    output_file = None

    #/* ======================================================================= */#
    #/*     Containers
    #/* ======================================================================= */#

    # JSON objects
    tasks = None
    task_runs = None

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
                    arg_error = True
                    print("ERROR: Invalid argument: %s" % str(arg))

        except IndexError:
            arg_error = True
            print("ERROR: An argument has invalid parameters")

    #/* ======================================================================= */#
    #/*     Validate configuration
    #/* ======================================================================= */#

    bail = False
    if arg_error:
        bail = True
        print("ERROR: Did not successfully parse arguments")
    if bail:
        return 1

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
