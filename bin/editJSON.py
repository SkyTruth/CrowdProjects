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
Add/delete fields from a JSON file
"""


from __future__ import print_function

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
    print("  --overwrite  -> Overwrite output file")
    print("  -a field=val -> Only add a field if it doesn't exist and set it equal to a value")
    print("  -e field=val -> Edit/add a field and set it equal to a value")
    print("  -r field=new -> Rename a field")
    print("  -d fields    -> Delete field")
    print("")
    print("Additional Options:")
    print("  Types: str|float|int|None")
    print("  -a=type field=val -> Add a field, and set it equal to ")
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
    print("Explanation: %s" % __docname__)
    print("---------------" + "-" * len(__docname__))
    print("""Add, edit, rename, delete, and change the type of fields in a JSON file
in a user defined order, which allows for on the fly field mapping and copying.
Processing flags are processed in the order they are discovered, which allows
the user to do things like rename a field by creating a new field, copying a
different field's value into it, and then deleting the old field.

NOTE: Currently only top level fields are accessed.  Nested fields are not
      supported.


Edit Field Example
------------------

If the 'county' field does not already exist in a given JSON object, it
will be added and set equal to 'Jefferson'.  If it does exist, the value
will be overwritten as 'Jefferson'.

{0} -e county=Jefferson input.json output.json

Alternatively, this command does the same thing but sets the value equal
to the string '123'

{0} -e county=123 input.json output.json

Alternatively, this command does the same thing but sets the value equal
to the integer 123

{0} -e=int county=123 input.json output.json

This command does the same thing but sets the value equal to the None type

{0} -e=None county=None input.json output.json


Add Field Example
-----------------

This command is similar to the edit shown above but ONLY adds the field if
it does not already exist

{0} -a county=Jefferson input.json output.json

{0} -a county=123 input.json output.json

{0} -a=int county=123 input.json output.json

{0} -a=None county=None input.json output.json


Rename Field Example
--------------------

If the field exists, it is renamed and if it doesn't exist, nothing happens.

{0} -r county=County input.json output.json


Delete Field Example
--------------------

If the field exists, it is deleted and if it doesn't exist, nothing happens.

{0} -d county input.json output.json


Copying a Field Value
---------------------

Field values can be copied into a new field via the edit command and by placing
a '%' character in front of the value and using a field name for the value

{0} -e NEW_FIELD=%county input.json output.json


Copy a Field and Change Type

Same command as above but add a field type to the -e flag

{0} -e=int NEW_FIELD=%county input.json output.json


Change a Field's Type
---------------------

A field's type can be changed with a combination of the above two commands

{0} -e=int field=%field input.json output.json

""".format(__docname__))

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

    # Processing options
    overwrite_outfile = False

    #/* ======================================================================= */#
    #/*     Containers
    #/* ======================================================================= */#

    # Input/output files
    infile = None
    outfile = None

    # Retain the processing argument order so processing order can be specified by the user
    processing_chain = []

    # Constrain value_types
    value_types = ('str', 'int', 'float', 'None', None)  # 'None' is default

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
            elif '-e=' in arg or '-a=' in arg or arg in ('-a', '-e', '-d', '-r'):
                processing_chain.append(arg)
                i += 2
                processing_chain.append(args[i - 1])

            # Additional options
            elif arg in ('--overwrite', '-overwrite'):
                i += 1
                overwrite_outfile = True

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

                # Catch errors
                else:
                    i += 1
                    arg_error = True
                    print("ERROR: Invalid argument: %s" % arg)

        except IndexError:
            i += 1
            arg_error = True
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
        print("ERROR: Need an output file")
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
    if not processing_chain:
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
    # TODO: Move each processing command into its own function
    print("Processing fields...")
    i = 0
    content_count = len(infile_content)
    while i < len(processing_chain):

        try:
            command = processing_chain[i]

            # Edit fields
            # TODO: Clean up logic for -e/-a
            if command[:2] in ('-a', '-e'):

                # Configure
                edit_command_only_adds = None
                if command[:2] == '-a':
                    edit_command_only_adds = True
                elif command[:2] == '-e':
                    edit_command_only_adds = False

                # Loop through edits|additions and process
                i += 1
                while i < len(processing_chain) and processing_chain[i][0] != '-':

                    # Get the parameters
                    field, value = processing_chain[i].split('=', 1)

                    # Check to see if we're forcing an edit type
                    value_type = 'None'
                    if '=' in command:
                        value_type = command.split('=', 1)[1]
                        if value_type not in value_types:
                            print("ERROR: Invalid value type: %s" % str(value_type))

                        # Only force the value's type upfront if its not being pulled from a field
                        if value[0] != '%':
                            if value_type == 'str':
                                value = str(value)
                            elif value_type == 'int':
                                try:
                                    value = int(value)
                                except ValueError:
                                    print("ERROR: Type '%s' is invalid for value '%s'" % str(value_type), value)
                                    return 1
                            elif value_type == 'float':
                                try:
                                    value = float(value)
                                except ValueError:
                                    print("ERROR: Type '%s' is invalid for value '%s'" % str(value_type), value)
                                    return 1
                            elif value_type == 'None':
                                value = None

                    # Save the original value for when %values are used
                    original_value = value

                    # Update user
                    if edit_command_only_adds:
                        print("  Adding: '%s'='%s'" % (field, str(value)))
                    else:
                        print("  Editing: '%s' -> '%s'" % (field, value))
                    if value_type != 'None':
                        print("           value_type=%s" % str(value_type))

                    # Make edits
                    loop_count = 0
                    for item in infile_content:

                        # Only create the field if
                        if edit_command_only_adds:
                            if field not in item:
                                item[field] = value
                        else:
                            if value[0] == '%' and value[1:] in item:
                                value = item[value[1:]]
                                if value_type != 'None':
                                    try:
                                        if value_type == 'str':
                                            value = str(value)
                                        elif value_type == 'int':
                                            value = int(value)
                                        elif value_type == 'float':
                                            value = float(value)
                                        elif value_type == 'none':
                                            value = None
                                    except ValueError:
                                        pass
                            item[field] = value

                        # Reset value to its original value since not all JSON objects are guaranteed to have the field
                        # This is necessary for %values
                        value = original_value

                        # Print progress
                        loop_count += 1
                        sys.stdout.write("\r\x1b[K" + "    %s/%s" % (str(loop_count), str(content_count)))
                        sys.stdout.flush()

                    # Loop iteration
                    i += 1

                # Formatting
                print(" - Done")

            # Rename fields
            elif command == '-r':
                i += 1
                while i < len(processing_chain) and processing_chain[i][0] != '-':

                    # Get the parameters
                    old_name, new_name = processing_chain[i].split('=', 1)

                    # Update user
                    print("  Renaming: '%s' -> '%s'" % (old_name, new_name))

                    # Do renaming
                    loop_count = 0
                    for item in infile_content:
                        if old_name in item:
                            value = item[old_name]
                            item[new_name] = value
                            del item[old_name]

                        # Print progress
                        loop_count += 1
                        sys.stdout.write("\r\x1b[K" + "    %s/%s" % (str(loop_count), str(content_count)))
                        sys.stdout.flush()

                    # Loop iteration
                    i += 1

                # Formatting
                print(" - Done")

            # Delete fields
            elif command == '-d':
                i += 1
                while i < len(processing_chain) and processing_chain[i][0] != '-':

                    # Get the parameters
                    delete_field = processing_chain[i]

                    # Update user
                    print("  Deleting: '%s'" % delete_field)

                    # Do deleting
                    loop_count = 0
                    for item in infile_content:
                        if delete_field in item:
                            del item[delete_field]

                        # Print progress
                        loop_count += 1
                        sys.stdout.write("\r\x1b[K" + "    %s/%s" % (str(loop_count), str(content_count)))
                        sys.stdout.flush()

                    # Loop iteration
                    i += 1

                # Formatting
                print(" - Done")

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
