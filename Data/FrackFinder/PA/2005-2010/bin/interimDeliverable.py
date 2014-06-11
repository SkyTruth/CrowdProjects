#!/usr/bin/env python


import sys
import json
from os.path import isfile
from os.path import sep


def get_location(task):

    lat = str(task['info']['latitude'])
    lng = str(task['info']['longitude'])
    year = str(task['info']['year'])

    return lat + lng + '---' + year


def main():

    # JSON locations
    basedir = '../DartFrog/QAQC/complete-tasks/export/'
    public_tasks_file = sep.join([basedir, 'public', 'task.json'])
    public_task_runs_file = sep.join([basedir, 'public', 'task_run.json'])
    first_internal_tasks_file = sep.join([basedir, 'first-internal', 'task.json'])
    first_internal_task_runs_file = sep.join([basedir, 'first-internal', 'task_run.json'])
    final_internal_tasks_file = sep.join([basedir, 'final-internal', 'task.json'])
    final_internal_task_runs_file = sep.join([basedir, 'final-internal', 'task_run.json'])
    sweeper_tasks_file = sep.join([basedir, 'sweeper-internal', 'task.json'])
    sweeper_task_runs_file = sep.join([basedir, 'sweeper-internal', 'task_run.json'])

    # Make sure input files exist
    for item in [public_tasks_file, public_task_runs_file, first_internal_tasks_file, first_internal_task_runs_file,
                 final_internal_tasks_file, final_internal_task_runs_file, sweeper_tasks_file, sweeper_task_runs_file]:
        if not isfile(item):
            return 1

    # Get public JSON
    print("")
    print("Fetching public json...")
    with open(public_tasks_file, 'r') as f:
        public_tasks = json.load(f)
    with open(public_task_runs_file, 'r') as f:
        public_task_runs = json.load(f)
    print("  tasks = %s" % str(len(public_tasks)))
    print("  task runs = %s" % str(len(public_task_runs)))
    print("")

    # Get first internal JSON
    print("Fetching first internal json...")
    with open(first_internal_tasks_file, 'r') as f:
        first_internal_tasks = json.load(f)
    with open(first_internal_task_runs_file, 'r') as f:
        first_internal_task_runs = json.load(f)
    print("  tasks = %s" % str(len(first_internal_tasks)))
    print("  task runs = %s" % str(len(first_internal_task_runs)))
    print("")

    # Get final internal JSON
    print("Fetching final internal json...")
    with open(final_internal_tasks_file, 'r') as f:
        final_internal_tasks = json.load(f)
    with open(final_internal_task_runs_file, 'r') as f:
        final_internal_task_runs = json.load(f)
    print("  tasks = %s" % str(len(final_internal_tasks)))
    print("  task runs = %s" % str(len(final_internal_task_runs)))
    print("")

    # Get sweeper internal JSON
    print("Fetching sweeper internal json...")
    with open(sweeper_tasks_file, 'r') as f:
        sweeper_tasks = json.load(f)
    with open(sweeper_task_runs_file, 'r') as f:
        sweeper_task_runs = json.load(f)
    print("  tasks = %s" % str(len(sweeper_tasks)))
    print("  task runs = %s" % str(len(sweeper_task_runs)))
    print("")

    # Get a list of locations
    loc_val_template = {'latitude': None,
                        'longitude': None,
                        'year': None,
                        'public_selection': None,
                        'first_internal_selection': None,
                        'final_internal_selection': None,
                        'sweeper_selection': None,
                        'overall_selection': None,
                        'selection_location': None,
                        'site_id': None}

    print("Creating locations container...")
    locations = {}
    for i in public_tasks:
        locations[get_location(i)] = loc_val_template
    print("Found %s locations" % str(len(locations)))

if __name__ == '__main__':
    sys.exit(main())