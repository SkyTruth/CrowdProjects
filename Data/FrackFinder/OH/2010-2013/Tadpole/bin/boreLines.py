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
EXPERIMENTAL: Produce lines between well borehole and endpoints
"""


import csv
import sys
from os.path import *
try:
    from osgeo import ogr
    from osgeo import osr
except ImportError:
    import ogr
    import osr
ogr.UseExceptions()
osr.UseExceptions()


#/* ======================================================================= */#
#/*     Build Information
#/* ======================================================================= */#

__version__ = '0.1-dev'
__release__ = '2014-06-23'
__copyright__ = 'Copyright 2014, SkyTruth'
__docname__ = basename(__file__)
__author__ = 'Kevin Wurster'
__license__ = '''
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
'''


#/* ======================================================================= */#
#/*     Define print_usage() function
#/* ======================================================================= */#

def print_usage():

    """
    Print commandline usage

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    print("""
Usage:
    {0} --help-info
    {0} [options] input.csv output.shp

Options:
    --overwrite     Enable overwrite mode
    """.format(__docname__))

    return 1


#/* ======================================================================= */#
#/*     Define print_help() function
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
HELP INFORMATION
    """.format(__docname__, '-' * len(__docname__)))

    return 1


#/* ======================================================================= */#
#/*     Define print_license() function
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
#/*     Define print_help_info() function
#/* ======================================================================= */#

def print_help_info():

    """
    Print a list of help related flags

    :return: 1 for exit code purposes
    :rtype: int
    """

    print("""
Help Flags:
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
    Print the module version information

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    print("""
%s version %s - released %s

%s
    """ % (__docname__, __version__, __release__, __copyright__))

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

    # Defaults
    overwrite_mode = False
    ogr_output_driver = 'ESRI Shapefile'
    ogr_input_epsg = 4326

    # Containers
    infile = None
    outfile = None

    # Parse arguments
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
        elif arg in ('--overwrite', '-overwrite'):
            overwrite_mode = True

        # Positional arguments and errors
        else:

            # Catch input file
            if infile is None:
                infile = arg

            # Catch output file
            elif outfile is None:
                outfile = arg

            # Catch errors
            else:
                print("ERROR: Unrecognized argument: %s" % arg)
                return 1

    # Open CSV for editing
    with open(infile, 'r') as f:
        reader = csv.DictReader(f)

        # Create OGR objects
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(ogr_input_epsg)
        driver = ogr.GetDriverByName(ogr_output_driver)
        if overwrite_mode and isfile(outfile):
            driver.DeleteDataSource(outfile)
        datasource = driver.CreateDataSource(outfile)
        layer = datasource.CreateLayer('borelines', srs, ogr.wkbLineString)
        field_object = ogr.FieldDefn('status', ogr.OFTString)
        field_object.SetWidth(254)
        layer.CreateField(field_object)

        # Process CSV file
        for line in reader:
            surface_lat = float(line['Surface Lat'])
            surface_lng = float(line['Surface Long'])
            endpoint_lat = float(line['Endpoint Lat'])
            endpoint_lng = float(line['Endpoint Long'])
            geometry = ogr.Geometry(ogr.wkbLineString)
            geometry.AddPoint(surface_lng, surface_lat)
            geometry.AddPoint(endpoint_lng, endpoint_lat)
            feature = ogr.Feature(layer.GetLayerDefn())
            feature.SetGeometry(geometry)
            feature.SetField('status', line['Status'])
            layer.CreateFeature(feature)

    # Cleanup
    feature = None
    line = None
    layer = None
    datasource = None
    driver = None
    srs = None

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
