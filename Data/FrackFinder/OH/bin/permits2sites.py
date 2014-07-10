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
Convert FrackFinder Ohio permit data to clustered sites
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
import math
import os
from os.path import *
import sys
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
__release__ = '2014-07-03'
__copyright__ = 'Copyright (c) 2014, SkyTruth '


#/* ======================================================================= */#
#/*     Document Level Information
#/* ======================================================================= */#

__docname__ = basename(__file__)
__all__ = ['print_usage', 'print_help', 'print_help_info', 'print_version', 'print_license',
           'get_epsg_code', 'main']


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
#/*     Define get_epsg_code() function
#/* ======================================================================= */#

def get_epsg_code(lat, lng):

    """
    Get a UTM EPSG code from the latitude and longitude

    :param lat: point's degree of latitude
    :type lat: float
    :param lng: point's degree longitude
    :type lng: float

    :return: EPSG code
    :rtype: int
    """

    zone = int(math.floor((lng + 180) / 6.0) + 1)

    epsg = 32600 + zone

    if lat < 0:
        epsg += 100

    return epsg


#/* ======================================================================= */#
#/*     Define generate_guid() function
#/* ======================================================================= */#

def generate_guid(*args):

    """
    Generate a GUID for a given clustered site
    """

    return sum(args)


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

    cluster_distance_m = 100
    overwrite_mode = False
    input_data_epsg = 4326

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

            # OGR options
            elif arg in ('-ie', '--input-epsg'):
                i += 2
                input_data_epsg = args[i - 1]

            # Additional options
            elif arg in ('--overwrite', '-overwrite'):
                i += 1
                overwrite_mode = True

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

    # Check input EPSG
    try:
        input_data_epsg = int(input_data_epsg)
    except ValueError:
        bail = True
        print("ERROR: Invalid input EPSG: %s" % str(input_data_epsg))

    if bail:
        return 1

    #/* ======================================================================= */#
    #/*     Build an in-memory OGR layer for use during processing
    #/* ======================================================================= */#

    # Figure out how many permits we're processing and make sure all the API's are unique
    num_permits = 0
    with open(input_file, 'r') as f:

        reader = csv.DictReader(f)

        # Cache all the API's for the non-unique check
        apis = [row['API #'] for row in reader]
        num_permits = len(apis)

        # Check for non-unique
        if num_permits != len(set(apis)):
            print("ERROR: The following API's are non-unique:")
            temp = []
            for api in apis:
                if api not in temp:
                    temp.append(api)
                else:
                    print(api)
            return 1

    print("Found %s records in input file: %s" % (str(num_permits), input_file))

    # Create an in memory OGR datasource for use during processing
    try:
        mem_srs = osr.SpatialReference()
        mem_srs.ImportFromEPSG(input_data_epsg)
        mem_driver = ogr.GetDriverByName('Memory')
        mem_ds = mem_driver.CreateDataSource('temp_ogr_ds')
        mem_layer_name = 'temp_ogr_layer'
        mem_layer = mem_ds.CreateLayer(mem_layer_name, mem_srs, ogr.wkbPoint)
        field_definitions = (('api', 254, ogr.OFTString),
                             ('epsg', 10, ogr.OFTInteger),
                             ('perm_date', 254, ogr.OFTString),
                             ('county', 254, ogr.OFTString),
                             ('status', 254, ogr.OFTString),
                             ('operator', 254, ogr.OFTString),
                             ('well_name', 254, ogr.OFTString),
                             ('end_lat', 254, ogr.OFTString),
                             ('end_long', 254, ogr.OFTString))
        for f_name, f_width, f_type in field_definitions:
            f_obj = ogr.FieldDefn(f_name, f_type)
            f_obj.SetWidth(f_width)
            mem_layer.CreateField(f_obj)
    except RuntimeError, e:
        print(e)
        return 1

    # Process input CSV
    with open(input_file, 'r') as f:

        print("Initial processing...")
        reader = csv.DictReader(f)

        # Add API's to temporary OGR datasource
        for row in reader:

            # Cache attributes
            api_num = str(row['API #'])
            lat = float(row['Surface Lat'])
            lng = float(row['Surface Long'])
            epsg_code = get_epsg_code(lat, lng)

            # Create and add feature
            geometry = ogr.Geometry(ogr.wkbPoint)
            geometry.AddPoint(lng, lat)
            feature = ogr.Feature(mem_layer.GetLayerDefn())
            feature.SetGeometry(geometry)
            feature.SetField('api', api_num)
            feature.SetField('epsg', epsg_code)
            feature.SetField('perm_date', row['Permit Issued'])
            feature.SetField('county', row['County'])
            feature.SetField('status', row['Status'])
            feature.SetField('operator', row['Operator'])
            feature.SetField('well_name', row['Well Name & Number'])
            feature.SetField('end_lat', row['Endpoint Lat'])
            feature.SetField('end_long', row['Endpoint Long'])


            mem_layer.CreateFeature(feature)

        # Cleanup
        geometry = None
        feature = None

    #/* ======================================================================= */#
    #/*     Cluster Data
    #/* ======================================================================= */#

    # TODO: This is pretty ugly ...

    print("Clustering data ...")
    mem_layer.ResetReading()
    with open(output_file, 'w') as f:

        # Create a CSV writer and immediately write the header row
        fieldnames = ['lat', 'long', 'api', 'guid', 'perm_date',
                      'county', 'perm_date', 'status', 'operator',
                      'well_name', 'end_lat', 'end_long']
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()

        # Create a copy of the in memory layer for distance calculations
        iter_layer = mem_ds.CopyLayer(mem_layer, 'ITER_' + mem_layer_name)

        # Keep track of which API's in the input dataset have been clustered to avoid generating multiple clusters
        processed_input_apis = []

        # Process all features in the memory layer
        mem_layer.ResetReading()
        i = 0
        for feature in mem_layer:

            # Update user
            i += 1
            sys.stdout.write("\r\x1b[K" + "  %s/%s" % (str(i), str(num_permits)))
            sys.stdout.flush()

            # Cache attributes
            feature_geometry = feature.GetGeometryRef().Clone()
            f_lat = feature_geometry.GetY()
            f_lng = feature_geometry.GetX()
            f_api = feature.GetField('api')
            f_epsg = feature.GetField('epsg')
            guid = generate_guid(*[f_lat, f_lng, int(f_api), f_epsg])

            # Only process the feature if its API number has not already been clustered
            if f_api not in processed_input_apis:

                # Reproject the input feature's geometry in order to do distance calculations in UTM
                f_s_srs = feature_geometry.GetSpatialReference()
                f_t_srs = osr.SpatialReference()
                f_t_srs.ImportFromEPSG(f_epsg)
                f_coord_transform = osr.CoordinateTransformation(f_s_srs, f_t_srs)
                reprojected_feature_geometry = feature_geometry.Clone()
                reprojected_feature_geometry.Transform(f_coord_transform)

                #/* ======================================================================= */#
                #/*     Cluster Data
                #/* ======================================================================= */#

                # Create a multi-point geometry to be used as the actual cluster
                # Set the SRS to the input feature's UTM zone since that's where all the distance
                # calculations will be performed
                cluster = ogr.Geometry(ogr.wkbMultiPoint)
                c_srs = osr.SpatialReference()
                c_srs.ImportFromEPSG(f_epsg)
                cluster.AssignSpatialReference(c_srs)

                # The current feature must always be part of the cluster, so add it
                cluster.AddGeometry(reprojected_feature_geometry)
                processed_input_apis.append(f_api)

                # Record which API numbers belong to this cluster
                cluster_apis = [f_api]

                # Keep performing distance calculations until no mo
                nearest_feature = ''  # Get past initial loop
                while nearest_feature is not None:

                    nearest_feature = None
                    nearest_distance = None
                    iter_layer.ResetReading()
                    for i_feature in iter_layer:

                        # Figure out if this feature is closer than the previous
                        distance = feature.GetGeometryRef().Distance(i_feature.GetGeometryRef())
                        if nearest_distance is None or distance < nearest_distance:
                            nearest_distance = distance
                            nearest_feature = i_feature.Clone()

                    # Add the nearest feature to the cluster
                    # If no nearest_feature is still None then that means the entire layer has been processed
                    # and we're done clustering the input feature
                    if nearest_feature is not None:

                        # Reproject the nearest feature to UTM and calculate distance
                        reprojected_i_geometry = nearest_feature.GetGeometryRef()
                        reprojected_i_geometry.Transform(f_coord_transform)
                        distance = cluster.Distance(reprojected_i_geometry)

                        # Nearest feature is not within the cluster distance - done with this feature
                        # All other features in the layer are outside the cluster distance as well
                        if distance > cluster_distance_m:
                            nearest_feature = None

                        # Add nearest point to the cluster if its still within the cluster distance
                        else:
                            processed_input_apis.append(nearest_feature.GetField('api'))
                            point = ogr.Geometry(ogr.wkbPoint)
                            point.AddPoint(reprojected_i_geometry.GetX(), reprojected_i_geometry.GetY())
                            cluster.AddGeometry(point)
                            cluster_apis.append(nearest_feature.GetField('api'))
                            iter_layer.DeleteFeature(nearest_feature.GetFID())

                # Compute a cluster centroid and send it back to the input layer's SRS
                centroid = cluster.Centroid()
                centroid_srs = cluster.GetSpatialReference()
                centroid_transform = osr.CoordinateTransformation(centroid_srs, f_s_srs)
                centroid.Transform(centroid_transform)

                # Write data
                writer.writerow({'lat': centroid.GetY(),
                                 'long': centroid.GetX(),
                                 'api': json.dumps(cluster_apis),
                                 'guid': guid,
                                 'perm_date': feature.GetField('perm_date'),
                                 'county': feature.GetField('county'),
                                 'status': feature.GetField('status'),
                                 'operator': feature.GetField('operator'),
                                 'well_name': feature.GetField('well_name'),
                                 'end_lat': feature.GetField('end_lat'),
                                 'end_long': feature.GetField('end_long')})

        # Done processing input file
        print(" - Done")

        # Cleanup
        reprojected_i_geometry = None
        nearest_feature = None
        i_feature = None
        point = None
        coord_transform = None
        reprojected_c_feature = None
        feature = None
        cluster = None
        mem_layer = None
        mem_ds = None
        iter_layer = None

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
