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
Add WMS URL information to the Digitizer input tasks for
FrackFinder PA 2013
"""


import os
import sys
import json
from os import sep
from os.path import *
try:
    from osgeo import ogr
    from osgeo import osr
except ImportError:
    import ogr
    import osr


#/* ======================================================================= */#
#/*     Build Information
#/* ======================================================================= */#

__author__ = 'Kevin Wurster'
__version__ = '0.1-dev'
__release__ = '2014-07-21'
__docname__ = basename(__file__)
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


#/* ======================================================================= */#
#/*     Define print_usage() function
#/* ======================================================================= */#

def print_usage():

    """
    Command line usage information

    :return: 1 for exit code purposes
    :rtype: int
    """

    print("""
Usage:
    {0} [options] input_task.json output_task.json

Options:
    --overwrite         Overwrite the output file if it exists
    --url=str           GME base URL
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
Input is a structured task.json and output is a structured task.json but with
the appropriate WMS information required by the digitizer
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
  --help    -> More detailed description of this utility
  --usage   -> Arguments, parameters, flags, options, etc.
  --version -> Version and ownership information
  --license -> License information
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
    """ % (__docname__, __version__, __release__))

    return 1


#/* ======================================================================= */#
#/*     Define main() function
#/* ======================================================================= */#

def main(args):

    """
    Main routine

    :param args: arguments from the commandline (sys.argv[1:] in order to drop the script name)
    :type args: list

    :return: 0 on success and 1 on error
    :rtype: int
    """

    #/* ----------------------------------------------------------------------- */#
    #/*     Defaults
    #/* ----------------------------------------------------------------------- */#

    overwrite = False

    imagery_year = 2013
    imagery_state = 'PA'

    wms_version = '1.3.0'
    gme_base_url = 'https://mapsengine.google.com/06136759344167181854-11153668168998282611-4/wms/?version=1.3.0'
    county_urls = {'Allegheny': {'layers': '06136759344167181854-17097547970711210810-4',
                                 'version': '1.3.0'},
                   'Armstrong': {'layers': '06136759344167181854-06463706214196194266-4',
                                 'version': '1.3.0'},
                   'Beaver': {'layers': '06136759344167181854-03215559208756578552-4',
                              'version': '1.3.0'},
                   'Bedford': {'layers': '06136759344167181854-16526163889416123181-4',
                               'version': '1.3.0'},
                   'Blair': {'layers': '06136759344167181854-16306107710083036950-4',
                             'version': '1.3.0'},
                   'Bradford': {'layers': '06136759344167181854-11619381169245561436-4',
                                'version': '1.3.0'},
                   'Butler': {'layers': '06136759344167181854-00163352971033251325-4',
                              'version': '1.3.0'},
                   'Cambria': {'layers': '06136759344167181854-13868684653393383220-4',
                               'version': '1.3.0'},
                   'Cameron': {'layers': '06136759344167181854-16463396596362732263-4',
                               'version': '1.3.0'},
                   'Centre': {'layers': '06136759344167181854-10539758809169921438-4',
                              'version': '1.3.0'},
                   'Clarion': {'layers': '06136759344167181854-17634790329248222990-4',
                               'version': '1.3.0'},
                   'Clearfield': {'layers': '06136759344167181854-03814583937239315939-4',
                                  'version': '1.3.0'},
                   'Clinton': {'layers': '06136759344167181854-09339614925439096698-4',
                               'version': '1.3.0'},
                   'Columbia': {'layers': '06136759344167181854-10054736502800588783-4',
                                'version': '1.3.0'},
                   'Crawford': {'layers': '06136759344167181854-00803512395514163624-4',
                                'version': '1.3.0'},
                   'Elk': {'layers': '06136759344167181854-10654422879476935199-4',
                           'version': '1.3.0'},
                   'Fayette': {'layers': '06136759344167181854-08226320688614047434-4',
                               'version': '1.3.0'},
                   'Forest': {'layers': '06136759344167181854-04494763453322801357-4',
                              'version': '1.3.0'},
                   'Greene': {'layers': '06136759344167181854-04446242188479492519-4',
                              'version': '1.3.0'},
                   'Huntingdon': {'layers': '06136759344167181854-12953080324530945934-4',
                                  'version': '1.3.0'},
                   'Indiana': {'layers': '06136759344167181854-10430386465901337383-4',
                               'version': '1.3.0'},
                   'Jefferson': {'layers': '06136759344167181854-01017506003890167070-4',
                                 'version': '1.3.0'},
                   'Lackawanna': {'layers': '06136759344167181854-11146815151701635563-4',
                                  'version': '1.3.0'},
                   'Lawrence': {'layers': '06136759344167181854-17465323330420787243-4',
                                'version': '1.3.0'},
                   'Lycoming': {'layers': '06136759344167181854-13835316165504888097-4',
                                'version': '1.3.0'},
                   'McKean': {'layers': '06136759344167181854-02116311310577831038-4',
                              'version': '1.3.0'},
                   'Mckean': {'layers': '06136759344167181854-02116311310577831038-4',
                              'version': '1.3.0'},
                   'Mercer': {'layers': '06136759344167181854-16872361300740609449-4',
                              'version': '1.3.0'},
                   'Potter': {'layers': '06136759344167181854-05714603436863463689-4',
                              'version': '1.3.0'},
                   'Somerset': {'layers': '06136759344167181854-08330569884800709473-4',
                                'version': '1.3.0'},
                   'Sullivan': {'layers': '06136759344167181854-00051000293596002125-4',
                                'version': '1.3.0'},
                   'Susquehanna': {'layers': '06136759344167181854-14352042435009570491-4',
                                   'version': '1.3.0'},
                   'Tioga': {'layers': '06136759344167181854-14517973204373249050-4',
                             'version': '1.3.0'},
                   'Venango': {'layers': '06136759344167181854-05937934275891388982-4',
                               'version': '1.3.0'},
                   'Warren': {'layers': '06136759344167181854-15230985584827365932-4',
                              'version': '1.3.0'},
                   'Washington': {'layers': '06136759344167181854-14060481984627017886-4',
                                  'version': '1.3.0'},
                   'Wayne': {'layers': '06136759344167181854-00928672201559263810-4',
                             'version': '1.3.0'},
                   'Westmoreland': {'layers': '06136759344167181854-10111599715883825716-4',
                                    'version': '1.3.0'},
                   'Wyoming': {'layers': '06136759344167181854-04815378753287989307-4',
                               'version': '1.3.0'}}

    #/* ----------------------------------------------------------------------- */#
    #/*     Containers
    #/* ----------------------------------------------------------------------- */#

    input_task_file = None
    output_task_file = None

    #/* ----------------------------------------------------------------------- */#
    #/*     Parse arguments
    #/* ----------------------------------------------------------------------- */#

    arg_error = False
    for arg in args:

        # Help arguments
        if arg in ('--help', '-help'):
            return print_help()
        elif arg in ('--help-info', '-help-info', '--helpinfo', '--helpinfo'):
            return print_help_info()
        elif arg in ('--license', '-license'):
            return print_license()
        elif arg in ('--version', '-version'):
            return print_version()

        # Additional options
        elif arg == '--overwrite':
            overwrite = True

        # Positional arguments
        else:

            # Get task.json file
            if input_task_file is None:
                input_task_file = abspath(arg)

            # Get task_run.json file
            elif output_task_file is None:
                output_task_file = abspath(arg)

            # Argument is unrecognized - throw an error
            else:
                arg_error = True
                print("ERROR: Invalid argument: %s" % str(arg))

    #/* ----------------------------------------------------------------------- */#
    #/*     Validate configuration
    #/* ----------------------------------------------------------------------- */#

    bail = False

    # Arguments
    if arg_error:
        bail = True
        print("ERROR: Did not successfully parse arguments")

    # Input task.json file
    if input_task_file is None:
        bail = True
        print("ERROR: Need an input task file")
    elif not os.access(input_task_file, os.R_OK):
        bail = True
        print("ERROR: Can't access input task file: %s" % input_task_file)

    # Output task.json file
    if output_task_file is None:
        bail = True
        print("ERROR: Need an output task file")
    elif not overwrite and isfile(output_task_file):
        bail = True
        print("ERROR: Overwrite=%s and output exists: %s" % (str(overwrite), output_task_file))
    elif overwrite and not os.access(output_task_file, os.W_OK):
        bail = True
        print("ERROR: Need write access: %s" % output_task_file)
    elif not os.access(dirname(output_task_file), os.W_OK):
        bail = True
        print("ERROR: Need write access for directory: %s" % dirname(output_task_file))

    if bail:
        return 1

    #/* ----------------------------------------------------------------------- */#
    #/*     Process input file
    #/* ----------------------------------------------------------------------- */#

    output_json = []

    # Open input file for processing
    with open(input_task_file, 'r') as i_f:

        input_tasks = json.load(i_f)

        # Process all input tasks
        print("Processing %s tasks ..." % str(len(input_tasks)))
        for task in input_tasks:

            task_body = {'info': task.copy()}

            # Get the GME layer ID for the WMS URL
            county = task['county']
            try:
                layer_id = county_urls[county]
            except KeyError:
                print("ERROR: County '%s' not in WMS URL dictionary" % county)
                return 1

            # Populate task
            task_body['info']['state'] = imagery_state
            task_body['info']['year'] = imagery_year
            task_body['info']['url'] = gme_base_url
            task_body['info']['options'] = {'layers': layer_id,
                                            'version': wms_version}

            output_json.append(task_body)

        # Write output file
        print("Writing output file ...")
        with open(output_task_file, 'w') as o_f:
            json.dump(output_json, o_f)

    #/* ----------------------------------------------------------------------- */#
    #/*     Cleanup and return
    #/* ----------------------------------------------------------------------- */#

    print("Done.")

    return 0


#/* ======================================================================= */#
#/*     Commandline Execution
#/* ======================================================================= */#

if __name__ == '__main__':

    # Not enough arguments - print usage
    if len(sys.argv) is 1:
        sys.exit(print_usage())

    # Got enough arguments - give all but the first to the main() function
    else:
        sys.exit(main(sys.argv[1:]))
