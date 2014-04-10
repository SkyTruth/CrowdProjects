#!/usr/bin/env python

# !!! THIS IS A TEMPORARY SCRIPT !!! #
# !!! THIS IS A TEMPORARY SCRIPT !!! #
# !!! THIS IS A TEMPORARY SCRIPT !!! #
# !!! THIS IS A TEMPORARY SCRIPT !!! #
# !!! THIS IS A TEMPORARY SCRIPT !!! #

import sys
import json
from os.path import isfile

__author__ = 'Kevin Wurster'


def get_location(task):
    lat = str(task['info']['latitude'])
    lng = str(task['info']['longitude'])
    year = str(task['info']['year'])
    return lat + lng + '---' + year


def is_task_complete(task, task_runs, redundancy):
    count = 0
    task_id = int(task['id'])
    for tr in task_runs:
        tr_id = int(tr['task_id'])
        if task_id == tr_id:
            count += 1
            if count >= redundancy:
                return True
    return False


def main(args):

    # JSON files of note
    public_tasks = '../DartFrog/QAQC/complete-tasks/export/public/task.json'
    public_task_runs = '../DartFrog/QAQC/complete-tasks/export/public/task_run.json'
    internal_tasks = '../DartFrog/QAQC/complete-tasks/export/first-internal/task.json'
    internal_task_runs = '../DartFrog/QAQC/complete-tasks/export/first-internal/task_run.json'
    outfile = 'OVERLAPPING_TASKS.json'

    # Make sure the files exist
    for filepath in (public_tasks, public_task_runs, internal_tasks, internal_task_runs):
        if not isfile(filepath):
            print("ERROR: Can't find: %s" % filepath)
            return 1

    # Open all files and cache as JSON
    print("Parsing input files...")
    json_content = {'public_tasks': public_tasks,
                    'public_task_runs': public_task_runs,
                    'internal_tasks': internal_tasks,
                    'internal_task_runs': internal_task_runs}
    for name, path in json_content.iteritems():
        with open(path, 'r') as f:
            json_content[name] = json.load(f)

    # Update user
    for name, content in json_content.iteritems():
        print('  ' + name + ' = ' + str(len(content)))

    # Get all completed tasks
    print("Getting completed tasks...")
    completed_public_tasks = []
    completed_internal_tasks = []
    for task in json_content['public_tasks']:
        if is_task_complete(task, json_content['public_task_runs'], 10):
            completed_public_tasks.append(task)
    print("  public_tasks = %s" % str(len(completed_public_tasks)))
    for task in json_content['internal_tasks']:
        if is_task_complete(task, json_content['internal_task_runs'], 3):
            completed_internal_tasks.append(task)
    print("  internal_tasks = %s" % str(len(completed_internal_tasks)))

    # Compare completed tasks to find overlapping tasks
    print("Finding overlapping tasks...")
    overlapping_tasks = []
    for p_task in completed_public_tasks:
        if p_task not in overlapping_tasks:
            p_task_location = get_location(p_task)
            for i_task in completed_internal_tasks:
                i_task_location = get_location(i_task)
                if p_task_location == i_task_location:
                    overlapping_tasks.append(p_task)
    print("  overlapping_tasks = %s" % len(overlapping_tasks))

    # Write to file
    print("Writing overlapping tasks...")
    with open(outfile, 'w') as f:
        json.dump(overlapping_tasks, f)
    print("Done.")

    # Successful
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))