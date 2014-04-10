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


def get_num_task_runs(task, task_runs):
    count = 0
    task_id = str(task['id'])
    for tr in task_runs:
        tr_id = tr['task_id']
        if task_id == tr_id:
            count += 1
    return count


def main(args):

    # JSON files of note
    public_tasks = '../DartFrog/QAQC/complete-tasks/export/public/task.json'
    public_task_runs = '../DartFrog/QAQC/complete-tasks/export/public/task_run.json'
    internal_tasks = '../DartFrog/QAQC/complete-tasks/export/first-internal/task.json'
    internal_task_runs = '../DartFrog/QAQC/complete-tasks/export/first-internal/task_run.json'

    # Make sure the files exist
    for filepath in (public_tasks, public_task_runs, internal_tasks, internal_task_runs):
        if not isfile(filepath):
            print("ERROR: Can't find: %s" % filepath)
            return 1

    # Open all files and cache as JSON
    json_content = {'public_tasks': public_tasks,
                    'public_task_runs': public_task_runs,
                    'internal_tasks': internal_tasks,
                    'internal_task_runs': internal_task_runs}
    for name, path in json_content.iteritems():
        with open(path, 'r') as f:
            json_content[name] = json.load(f)

    # Update user
    for name, content in json_content.iteritems():
        print(name + ' = ' + str(len(content))

    # Get all completed tasks
    completed_tasks = {'public_tasks': [],
                       'internal_tasks': []}
    for task in json_content['public_tasks']:
        if get_num_task_runs(task, json_content['public_task_runs']) >= 10:
            completed_tasks['public_tasks'].append(task)
    for task in json_content['internal_tasks']:
        if get_num_task_runs(task, json_content['internal_task_runs']) >= 3:
            completed_tasks['internal_tasks'].append(task)

    # Update user
    for name, content in completed_tasks.iteritems():
        print(name + ' = ' + str(len(content)))

    # Successful
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))