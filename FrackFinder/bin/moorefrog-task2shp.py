#!/usr/bin/env python


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


import os
import sys
import json
import inspect
from os.path import basename


# Build information
__author__ = 'Kevin Wurster'
__copyright__ = 'Copyright (c) 2014, SkyTruth'
__version__ = '0.1'
__release__ = '2014/04/23'
__docname__ = basename(inspect.getfile(inspect.currentframe()))


def print_usage():

    """
    Command line usage information
    """

    print("")
    print("Usage: %s [options] task.json task_run.json output/directory" % __docname__)
    print("")
    print("Options:")
    print("  --help-info  -> Print out a list of help related flags")
    print("  --prefix=str -> Output filename prefix")
    print("  --wellpad-file-name=str -> Defaults to 'wellpad.shp")
    print("  --bbox-file-name=str -> Defaults to 'bbox.shp")
    print("  --clicks-file-name=str -> Defaults to 'clicks.shp")
    print("")
    print("OGR Options:")
    print("  --of=driver  -> Output driver name/file type - default='ESRI Shapefile'")
    print("  --epsg=int   -> EPSG code for coordinates in task.json - default=4326")
    print("")

    return 1


def print_license():

    """
    Print out license information
    """

    print(__license__)

    return 1


def print_help():

    """
    Detailed help information
    """

    print("")
    print("%s Detailed Help" % __docname__)
    print("--------------" + "-" * len(__docname__))
    print("Input is task.json and task_run.json from MooreFrog")
    print("Output is a set of bounding boxes, well pad points, ")
    print("and pond clicks.")
    print("")

    return 1


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
    print("  ")

    return 1


def print_version():

    """
    Print script version information
    """

    print("")
    print('%s version %s - released %s' % (__docname__, __version__, __release__))
    print(__copyright__)
    print("")

    return 1


def main(args):

    # Containers
    task_file_path = None
    task_run_file_path = None
    output_directory = None
    output_prefix = ''

    # Defaults
    bbox_file_name = 'bbox.shp'
    well_pad_file_name = 'wellpads.shp'
    clicks_file_name = 'clicks.shp'

    # Parse arguments
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
        elif '--prefix=' in arg:
            output_prefix = arg.split('=', 1)[1]
        elif '--bbox-file-name=' in arg:
            bbox_file_name = arg.split('=', 1)[1]
        elif '--wellpad-file-name=' in arg or '--well-pad-file-name=' in arg:
            well_pad_file_name = arg.split('=', 1)[1]
        elif '--clicks-file-name=' in arg:
            clicks_file_name = arg.split('=', 1)[1]

        # Ignore empty arguments
        elif arg == '':
            pass

        # Positional arguments
        else:

            # Get task.json file
            if task_file_path is None:
                task_file_path = arg

            # Get task_run.json file
            elif task_run_file_path is None:
                task_run_file_path = arg

            # Get output directory
            elif output_directory is None:
                output_directory = arg

            # Argument is unrecognized - throw an error
            else:
                print("ERROR: Invalid argument: %s" % str(arg))
                arg_error = True

    # Validate
    bail = False
    if arg_error:
        print("ERROR: Did not successfully parse arguments")
        bail = True
    if output_directory is None or not os.access(output_directory, os.W_OK):
        print("ERROR: Can't access output directory: %s" % output_directory)
        bail = True
    if task_file_path is None or not os.access(task_file_path, os.R_OK):
        print("ERROR: Can't access task file: %s" % task_file_path)
        bail = True
    if task_run_file_path is None or not os.access(task_run_file_path, os.R_OK):
        print("ERROR: Can't access task run file: %s" % task_run_file_path)
        bail = True
    if bail:
        return 1

    # Update user
    print("Task file: %s" % task_file_path)
    print("Task run file: %s" % task_run_file_path)
    print("Output directory: %s" % output_directory)

    # Convert files to json
    print("Extracting JSON...")
    with open(task_file_path, 'r') as f:
        task_json = json.load(f)
    with open(task_run_file_path, 'r') as f:
        task_run_json = json.load(f)
    print("  Num tasks: %s" % str(len(task_json)))
    print("  Num task runs: %s" % str(len(task_run_json)))

    # Create

    from pprint import pprint
    print("")
    pprint(task_json[0])
    print("")

    # Cleanup OGR datasources



    # Success
    return 0


if __name__ == '__main__':
    if len(sys.argv) is 1:
        sys.exit(print_usage())
    else:
        sys.exit(main(sys.argv[1:]))
