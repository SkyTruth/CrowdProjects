# ========================================================================== #
#
#    Copyright (c) 2014, SkyTruth
#    All rights reserved.
#
#    Redistribution and use in source and binary forms, with or without
#    modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice, this
#      list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
#    * Neither the name of the {organization} nor the names of its
#      contributors may be used to endorse or promote products derived from
#      this software without specific prior written permission.
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#    FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#    DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#    SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#    CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#    OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# ========================================================================== #


import os
import json
from os.path import isfile


def load_json(infile):

    """
    Wrapper to quickly convert a file to a JSON object

    :param infile: input file path
    :type infile: str
    :rtype: dict|list|False
    """

    # Validate input
    if not isfile(infile) or not os.access(infile, os.R_OK):
        print("ERROR: Can't access: %s" % str(infile))
        return False

    # Perform conversion to JSON
    with open(infile, 'r') as f:
        output = json.load(f)

    return output


def get_task_runs(task, task_run_json, unique=True):

    """
    Search through items from task_run.json to find matching objects for input task

    :param task: input task object
    :type task: dict
    :param task_run_json: task_run.json converted to a JSON object via json.load() or common.load_json()
    :type task_run_json: list
    :param unique: specifies whether output list will contain unique values or not
    :type unique: bool
    :rtype: list
    """

    # Perform comparison
    output = []
    task_id = task['id']
    for task_run in task_run_json:
        if task_id == task_run['task_id']:
            output.append(task)
    if unique:
        return set(output)
    else:
        return output


def get_overlapping_tasks(compare_id=False, *task_groups):

    """
    Compare lists of input tasks and return the tasks that appear in all sets

    :param compare_id: toggle whether or not the id tag should be used in the comparison
    :type compare_id: bool
    :param task_groups: lists of tasks from json.load(open('infile.json')) OR load_json()
    :type task_groups: list
    :rtype: bool|list
    """

    # Validate input
    if len(task_groups) <= 1:
        return False

    # Get a task from a group and make sure it exists in the other groups
    # group_index is used to speed up the loop that searches for overlapping tasks
    # No need to search the current group since that is where we got the task
    overlapping_tasks = []
    group_index = 0

    # Get a group of tasks
    for group in task_groups:

        # Loop through all tasks in the group
        for task in group:

            # Cache the task since we may be removing the id key in order to get a better comparison
            task_cache = task
            if not compare_id:
                del task['id']

            # Check to make sure the task isn't already in the output overlapping_tasks list - speeds things up
            if task not in overlapping_tasks:

                # Figure out how many groups we need to check the task against and iterate through their indexes
                for check_index in range(0, len(task_groups)):

                    # Don't check the group we're working with in the outer loop - compare the indexes for a quick check
                    if group_index is not check_index:

                        # Check if the task exists in the current check_group - let python do all the work if compare_id
                        if compare_id:
                            if task in task_groups[check_index]:
                                overlapping_tasks.append(task_cache)
                        else:

                            # We have to compare the id field, so loop through tasks individually
                            for check_task in task_groups[check_index]:

                                # Remove the id key if necessary
                                if not compare_id:
                                    del check_task['id']

                                # Get location and compare
                                if task == check_task:

                                    # Hey, it exists - Append to the output container
                                    overlapping_tasks.append(task_cache)

        # Iterate the group index in preparation for processing the next group
        group_index += 1

    # Trash potentially giant input object to save memory
    task_groups = None

    return overlapping_tasks


def get_non_overlapping_tasks():
    pass


def is_task_finished():
    pass


def get_unique_tasks(compare_id=False, *task_groups):

    """
    Compare lists of tasks and get a unique set in return.
    False is returned if an error is encountered

    :param compare_id: toggle whether or not the id field is included in the comparison
    :type compare_id: bool
    :param task_groups: input lists of tasks from json.load(open('file.json')) or load_json()
    :type task_groups: list
    :rtype: bool|list
    """

    # Validate input
    if len(task_groups) <= 1:
        return False

    # Get a task from a group and make sure it exists in the other groups
    # group_index is used to speed up the loop that searches for overlapping tasks
    # No need to search the current group since that is where we got the task
    unique_tasks = []
    group_index = 0

    # Get a group of tasks
    for group in task_groups:

        # Loop through all tasks in the group
        for task in group:

            # Cache the task since we may be removing the id key in order to get a better comparison
            task_cache = task
            if not compare_id:
                del task['id']

            # Check to make sure the task isn't already in the output overlapping_tasks list - speeds things up
            if task not in unique_tasks:

                # Figure out how many groups we need to check the task against and iterate through their indexes
                for check_index in range(0, len(task_groups)):

                    # Don't check the group we're working with in the outer loop - compare the indexes for a quick check
                    if group_index is not check_index:

                        # Check if the task exists in the current check_group - let python do all the work if compare_id
                        if compare_id:
                            is_unique
                            if task in task_groups[check_index]:
                                unique_tasks.append(task_cache)
                        else:

                            # We have to compare the id field, so loop through tasks individually
                            for check_task in task_groups[check_index]:

                                # Remove the id key if necessary
                                if not compare_id:
                                    del check_task['id']

                                # Get location and compare
                                if task == check_task:

                                    # Hey, it exists - Append to the output container
                                    overlapping_tasks.append(task_cache)

        # Iterate the group index in preparation for processing the next group
        group_index += 1

    # Trash potentially giant input object to save memory
    task_groups = None

    return overlapping_tasks
