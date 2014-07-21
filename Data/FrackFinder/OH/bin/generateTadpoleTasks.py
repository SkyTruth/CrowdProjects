#!/usr/bin/env python


# This document is part of CrowdProjects
# https://github.com/skytruth/CrowdProjects


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


"""
Convert output from permits2sites.py to PyBossa tasks
"""


from __future__ import print_function

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

import csv
import json
import os
from os.path import *
import sys


#/* ======================================================================= */#
#/*     Build Information
#/* ======================================================================= */#

__author__ = 'Kevin Wurster'
__version__ = '0.1-dev'
__release__ = '2014-07-10'
__copyright__ = 'Copyright (c) 2014, SkyTruth'


#/* ======================================================================= */#
#/*     Document Level Information
#/* ======================================================================= */#

__docname__ = basename(__file__)
__all__ = ['print_usage', 'print_help', 'print_help_info', 'print_version', 'print_license', 'main']


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
    {0} [--help-info] input.csv output.csv
""".format(__docname__))

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
#/*     Define print_help() function
#/* ======================================================================= */#

def print_help():

    """
    Detailed help information

    :return: 1 for exit code purposes
    :rtype: int
    """

    print("""
Help: {0}
------{1}
    """.format(__docname__, '-' * len(__docname__)))

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
%s v%s - released %s

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

    # Processing options
    overwrite_mode = False
    process_subsample = None

    # Input data field names
    i_lat_field = 'lat'
    i_long_field = 'long'
    i_guid_field = 'guid'
    i_api_field = 'api'
    i_county_field = 'county'

    # WMS info
    wms_data = {'map': 'https://mapsengine.google.com/06136759344167181854-11845109403981099587-4/wms/',
                'version': '1.3.0',
                'years': {'2010': '06136759344167181854-04770958895915995837-4',
                          '2011': '06136759344167181854-08224624193234342065-4',
                          '2013': '06136759344167181854-11275828430006462017-4'}}

    # Additional task attributes
    task_state = 'OH'
    task_size = 200

    #/* ======================================================================= */#
    #/*     Containers
    #/* ======================================================================= */#

    input_file = None
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
            if arg in ('--help', '-help'):
                return print_help()
            elif arg in ('--help-info', '-help-info', '--helpinfo', '--helpinfo'):
                return print_help_info()
            elif arg in ('--license', '-license'):
                return print_license()
            elif arg in ('--version', '-version'):
                return print_version()
            elif arg in ('--usage', '-usage'):
                return print_usage()

            # Infile options
            elif '-i-lat-field' in arg:
                i += 2
                i_lat_field = args[i - 1]
            elif '-i-long-field' in arg:
                i += 2
                i_long_field = args[i - 1]
            elif '-i-guid-field' in arg:
                i += 2
                i_guid_field = args[i - 1]
            elif '-i-api-field' in arg:
                i += 2
                i_api_field = args[i - 1]

            # Additional task options
            elif arg in ('-size', '--size'):
                i += 2
                task_size = args[i - 1]
            elif arg in ('-state', '--state'):
                i += 2
                task_state = args[i - 1]

            # Additional options
            elif arg in ('--overwrite', '-overwrite'):
                i += 1
                overwrite_mode = True
            elif arg in ('-s', '--subsample'):
                i += 2
                process_subsample = args[i - 1]

            # Positional arguments and errors
            else:

                # Catch input file
                if input_file is None:
                    i += 1
                    input_file = abspath(arg)

                # Catch output file
                elif output_file is None:
                    i += 1
                    output_file = abspath(arg)

                # Catch unrecognized arguments
                else:
                    i += 1
                    arg_error = True
                    print("ERROR: Unrecognized argument: %s" % arg)

        # An argument with parameters likely didn't iterate 'i' properly
        except IndexError:
            arg_error = True
            i += 1
            print("ERROR: An argument has invalid parameters")

    #/* ======================================================================= */#
    #/*     Validate
    #/* ======================================================================= */#

    bail = False

    # Check arguments
    if arg_error:
        bail = True
        print("ERROR: Did not successfully parse arguments")

    # Check input file
    if input_file is None:
        bail = True
        print("ERROR: Need an input file")
    elif not os.access(input_file, os.R_OK):
        bail = True
        print("ERROR: Can't access input CSV: %s" % input_file)

    # Check output file
    if output_file is None:
        bail = True
        print("ERROR: Need an output file")
    elif not os.access(dirname(output_file), os.W_OK):
        bail = True
        print("ERROR: Need write access: %s" % dirname(output_file))
    elif not overwrite_mode and isfile(output_file):
        bail = True
        print("ERROR: Overwrite=%s and output file exists: %s" % (str(overwrite_mode), output_file))

    # If processing a subsample, validate
    if process_subsample is not None:
        try:
            process_subsample = int(process_subsample)
            if process_subsample < 0:
                bail = True
                print("ERROR: Invalid subsample - must be > 0: %s" % str(process_subsample))
        except ValueError:
            bail = True
            print("ERROR: Invalid subsample - must be an int: %s" % str(process_subsample))

    # Additional task attributes
    try:
        task_size = int(task_size)
        if task_size < 0:
            bail = True
            print("ERROR: Invalid task size - must be > 0: %s" % str(task_size))
    except ValueError:
        bail = True
        print("ERROR: Invalid task size - must be an int: %s" % str(task_size))

    # Exit on validation error
    if bail:
        return 1

    #/* ======================================================================= */#
    #/*     Convert input file to tasks
    #/* ======================================================================= */#

    # Figure out how many rows are in the input CSV
    num_input_rows = None
    with open(input_file, 'r') as i_f:
        reader = csv.DictReader(i_f)
        num_input_rows = len([i for i in reader])

    # Process input file
    print("Processing input file: %s" % input_file)
    with open(input_file, 'r') as i_f:

        reader = csv.DictReader(i_f)
        output_content = []

        i = 0
        for row in reader:

            # Update user
            i += 1
            sys.stdout.write("\r\x1b[K" + "  %s/%s" % (str(i), str(num_input_rows)))
            sys.stdout.flush()

            # Create one task for every imagery year
            years = wms_data['years'].keys()
            years.sort()
            for year in years:

                output_content.append({'info': {'latitude': float(row[i_lat_field]),
                                                'longitude': float(row[i_long_field]),
                                                'options': {'layers': wms_data['years'][year],
                                                            'version': wms_data['version']},
                                                'county': row[i_county_field],
                                                'siteID': row[i_guid_field],
                                                'size': task_size,
                                                'state': task_state,
                                                'url': wms_data['map'],
                                                'year': year,
                                                'apis': row[i_api_field]}})
        # Update user
        print(" - Done")

        #/* ======================================================================= */#
        #/*     Convert input file to tasks
        #/* ======================================================================= */#

        print("Writing output file ...")
        with open(output_file, 'w') as o_f:
            json.dump(output_content, o_f)

        print("Done")

    #/* ======================================================================= */#
    #/*     Cleanup
    #/* ======================================================================= */#

    # Success
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
