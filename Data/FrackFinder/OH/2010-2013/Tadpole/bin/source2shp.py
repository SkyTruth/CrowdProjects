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
Convert FrackFinder Ohio source data to a spatial format
"""


from __future__ import print_function

import os
import csv
import sys
from os.path import *
from datetime import datetime
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

__author__ = 'Kevin Wurster'
__version__ = '0.1-dev'
__release__ = '2014-06-23'
__copyright__ = 'Copyright (c) 2014, SkyTruth '
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
    Commandline usage

    :return: returns 1 for for exit code purposes
    :rtype: int
    """

    print("""
Usage:
    {0} --help-info
    {0} [options] input.csv output.shp

Options:
    --overwrite     Overwrite the output file
    --of=driver     Set output OGR driver
                    [default: 'ESRI Shapefile']
    --epsg=int      Set EPSG code for input data
                    [default: 4326]
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
This utility converts an input CSV matching the format listed below to an
OGR compatible vector layer with properly typecast fields.  The values
used for the point coordinates are "Surface Lat" and "Surface Long".

Permit Issued,County,Township,API #,Status,Operator,Well Name & Number,Surface Lat,Surface Long,Endpoint Lat,Endpoint Long
11/02/11,ASHLAND,CLEAR CREEK,34005241600100,Drilled,DEVON ENERGY PRODUCTION CO,EICHELBERGER DAVID 1H,40.9466508,-82.4034777,40.9466509,-82.4036587
06/07/13,ASHTABULA,WAYNE,34007245510100,Permitted,BEUSA ENERGY LLC,MAGYAR 9 1H,41.5204837,-80.6934257,41.5005237,-80.6788228
04/09/12,BELMONT,MEAD,34013206530000,Producing,XTO ENERGY INC.,KALDOR 2H,39.9773526,-80.8380489,39.969831,-80.819645
04/09/12,BELMONT,MEAD,34013206540100,Producing,XTO ENERGY INC.,KALDOR 1H,39.9760339,-80.8381875,39.9667858,-80.8196294
06/15/12,BELMONT,KIRKWOOD,34013206570100,Producing,GULFPORT ENERGY CORPORATION,SHUGERT 1-1H,40.0431192,-81.1231952,40.0574876,-81.1320239
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
%s version %s - released %s

%s
    """ % (__docname__, __version__, __release__, __copyright__))

    return 1


#/* ======================================================================= */#
#/*     Define man() function
#/* ======================================================================= */#

def date_formatter(input_datestring):

    """
    Convert an input date string to an OGR compatible date string

    :param input_datestring: input date string from input CSV
    :type input_datestring: str

    :return: OGR compatible date string
    :rtype: str
    """

    return datetime.strptime(input_datestring, '%m/%d/%y').strftime('%Y-%m-%d')


#/* ======================================================================= */#
#/*     Define man() function
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

    overwrite_mode = False
    ogr_input_epsg = 4326
    ogr_output_driver = 'ESRI Shapefile'

    #/* ======================================================================= */#
    #/*     Containers
    #/* ======================================================================= */#

    infile = None
    outfile = None

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

            # OGR options
            elif '--of=' in arg or '-of=' in arg:
                i += 1
                ogr_output_driver = arg.split('=', 1)[1]
            elif '--epsg=' in arg or '-epsg=' in arg:
                i += 1
                ogr_input_epsg = arg.split('=', 1)[1]

            # Additional options
            elif arg in ('--overwrite', '-overwrite'):
                i += 1
                overwrite_mode = True

            # Positional arguments and errors
            else:

                # Catch input file
                if infile is None:
                    i += 1
                    infile = abspath(arg)

                # Catch output file
                elif outfile is None:
                    i += 1
                    outfile = abspath(arg)

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
    if infile is None:
        bail = True
        print("ERROR: Need an input CSV")
    elif not os.access(infile, os.R_OK):
        bail = True
        print("ERROR: Can't access input CSV: %s" % infile)

    # Check output file
    if outfile is None:
        bail = True
        print("ERROR: Need an output file")
    elif not os.access(dirname(outfile), os.W_OK):
        bail = True
        print("ERROR: Need write access: %s" % dirname(outfile))
    elif not overwrite_mode and isfile(outfile):
        bail = True
        print("ERROR: Overwrite=%s and output file exists: %s" % (str(overwrite_mode), outfile))

    # Check OGR options
    try:
        ogr_input_epsg = int(ogr_input_epsg)
        if ogr_input_epsg <= 0:
            bail = True
            print("ERROR: Invalid EPSG code: %s" % str(ogr_input_epsg))
    except ValueError:
        bail = True
        print("ERROR: Invalid input file EPSG code - must be an int: %s" % str(ogr_input_epsg))
    if ogr_output_driver not in [ogr.GetDriver(i).GetName() for i in range(ogr.GetDriverCount())]:
        bail = True
        print("ERROR: Invalid output OGR driver: %s" % ogr_output_driver)

    if bail:
        return 1

    #/* ======================================================================= */#
    #/*     Open Input Files and Construct Output Files
    #/* ======================================================================= */#

    # Open input CSV and prepare a DictReader() instance
    with open(infile, 'r') as f:

        reader = csv.DictReader(f)

        # Build OGR objects
        driver = ogr.GetDriverByName(ogr_output_driver)
        if overwrite_mode and isfile(outfile):
            driver.DeleteDataSource(outfile)
        elif not overwrite_mode and isfile(outfile):
            print("ERROR: Problem with overwrite flag")
            driver = None
            return 1
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(ogr_input_epsg)
        datasource = driver.CreateDataSource(outfile)
        layer_name = basename(outfile).split('.')[1]
        layer = datasource.CreateLayer(layer_name, srs, ogr.wkbPoint)

        # Create fields
        field_definitions = (('perm_date', 40, ogr.OFTDate, None),
                             ('county', 254, ogr.OFTString, None),
                             ('township', 254, ogr.OFTString, None),
                             ('api', 254, ogr.OFTString, None),
                             ('status', 254, ogr.OFTString, None),
                             ('operator', 254, ogr.OFTString, None),
                             ('wellnameid', 254, ogr.OFTString, None),
                             ('surf_lat', 10, ogr.OFTReal, 8),
                             ('surf_long', 10, ogr.OFTReal, 8),
                             ('end_lat', 10, ogr.OFTReal, 8),
                             ('end_long', 10, ogr.OFTReal, 8))
        for f_name, f_width, f_type, f_precision in field_definitions:
            f_obj = ogr.FieldDefn(f_name, f_type)
            f_obj.SetWidth(f_width)
            if f_precision is not None:
                f_obj.SetPrecision(f_precision)
            layer.CreateField(f_obj)

        # Map input file fields to output file fields
        # TODO: Why are some perm_dates not populating?  Might have to run through datetime to normalize
        ifield2map = (('Permit Issued', 'perm_date', date_formatter),
                      ('County', 'county', str),
                      ('Township', 'township', str),
                      ('API #', 'api', str),
                      ('Status', 'status', str),
                      ('Operator', 'operator', str),
                      ('Well Name & Number', 'wellnameid', str),
                      ('Surface Lat', 'surf_lat', float),
                      ('Surface Long', 'surf_long', float),
                      ('Endpoint Lat', 'end_lat', float),
                      ('Endpoint Long', 'end_long', float))

        #/* ======================================================================= */#
        #/*     Process Input CSV
        #/* ======================================================================= */#

        i = 0
        for line in reader:

            # Update user
            i += 1
            sys.stdout.write("\r\x1b[K" + "Processed %s lines" % str(i))

            # Instantiate feature and create/set geometry
            feature = ogr.Feature(layer.GetLayerDefn())
            geometry = ogr.Geometry(ogr.wkbPoint)  # TODO: Shouldn't 'ogr.wkbPoint' come from feature.GetFeatureDefn()? Method doesn't actually
            geometry.AddPoint(float(line['Surface Long']), float(line['Surface Lat']))
            feature.SetGeometry(geometry)

            # Populate fields
            for ifield, ofield, caster in ifield2map:
                feature.SetField(ofield, caster(line[ifield]))

            # Create feature
            layer.CreateFeature(feature)

        # Required formatting due to progress printout
        print("")

    #/* ======================================================================= */#
    #/*     Cleanup
    #/* ======================================================================= */#

    # Close OGR objects
    geometry = None
    feature = None
    layer = None
    datasource = None
    driver = None
    srs = None

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
