#!/usr/bin/env python


import sys
import json
from pprint import pprint


PRECISION = 8


def load_json(input_file):

    """
    Convert a JSON file to a json.load(open(input_file)) object
    """

    return json.load(open(input_file))


def get_location(task, precision=PRECISION):

    """
    Get a task's location
    """

    lat = task['info']['latitude']
    lng = task['info']['longitude']
    year = task['info']['year']
    if precision is not None:
        lat = round(lat, precision)
        lng = round(lng, precision)

    return str(lat) + str(lng) + '---' + str(year)


def does_task_have_task_runs(task, task_runs):

    """
    Figure out if at least one task run exists for a given task

    Faster than get_task_runs()
    """

    task_id = task['id']
    for tr in task_runs:
        if task_id == tr['task_id']:
            return True
    else:
        return False


def get_task_runs(task, task_runs_object):

    """
    Return a list of all associated task runs for a task
    """

    output_list = []
    task_id = task['id']
    for tr in task_runs_object:
        if task_id == tr['task_id']:
            output_list.append(tr)
    return output_list


def location2task(location, tasks, precision=PRECISION):

    """
    Take a location and search through a set of tasks for a matching location - return that task
    """

    for task in tasks:
        if location == get_location(task, precision=precision):
            return task
    else:
        return None


def find_missing_task_runs(missing_locations=None,
                           first_internal_tasks=None,
                           first_internal_task_runs=None,
                           final_internal_tasks=None,
                           final_internal_task_runs=None,
                           sweeper_tasks=None,
                           sweeper_task_runs=None,
                           missing_tasks=None,
                           missing_task_runs=None):

    # Validate
    if missing_locations is None:
        raise ValueError("Need missing_locations")
    if first_internal_tasks is None:
        raise ValueError("Need first_internal_tasks")
    if first_internal_task_runs is None:
        raise ValueError("Need first_internal_task_runs")
    if final_internal_tasks is None:
        raise ValueError("Need final_internal_tasks")
    if final_internal_task_runs is None:
        raise ValueError("Need final_internal_task_runs")
    if sweeper_tasks is None:
        raise ValueError("Need sweeper_tasks")
    if sweeper_task_runs is None:
        raise ValueError("Need sweeper_task_runs")
    if missing_tasks is None:
        raise ValueError("Need missing_tasks")
    if missing_task_runs is None:
        raise ValueError("Need missing_task_runs")

    # Track where everything was found
    matched_first_internal_locations = []
    matched_final_internal_locations = []
    matched_sweeper_locations = []
    matched_missing_internal_locations = []
    found_public = []
    found_first_internal = []
    found_final_internal = []
    found_sweeper_internal = []
    found_missing_internal = []

    # Look in first internal for missing locations
    print("  Searching for missing task runs in first internal...")
    for missing_location in missing_locations:
        fi_task = location2task(missing_location, first_internal_tasks)
        if fi_task is not None:
            matched_first_internal_locations.append(missing_location)
            if len(get_task_runs(fi_task, first_internal_task_runs)) > 0:
                if missing_location not in found_first_internal:
                    found_first_internal.append(missing_location)
    print("    Matched locations: %s" % str(len(matched_first_internal_locations)))
    print("    Found %s in first internal" % str(len(found_first_internal)))

    # Look in final internal for missing locations
    print("  Searching for missing task runs in final internal...")
    for missing_location in missing_locations:
        fn_task = location2task(missing_location, final_internal_tasks)
        if fn_task is not None:
            matched_final_internal_locations.append(missing_location)
            if len(get_task_runs(fn_task, final_internal_task_runs)) > 0:
                if missing_location not in found_final_internal:
                    found_final_internal.append(missing_location)
    print("    Matched locations: %s" % str(len(matched_final_internal_locations)))
    print("    Found %s in final internal" % str(len(found_final_internal)))

    # Look in sweeper for missing locations
    print("  Searching for missing task runs in sweeper internal...")
    for missing_location in missing_locations:
        sw_task = location2task(missing_location, sweeper_tasks)
        if sw_task is not None:
            matched_sweeper_locations.append(missing_location)
            if len(get_task_runs(sw_task, sweeper_task_runs)) > 0:
                if missing_location not in found_sweeper_internal:
                    found_sweeper_internal.append(missing_location)
    print("    Matched locations: %s" % str(len(matched_sweeper_locations)))
    print("    Found %s in sweeper internal" % str(len(found_sweeper_internal)))

    # Look in missing for missing locations
    print("  Searching for missing task runs in missing internal...")
    for missing_location in missing_locations:
        mi_task = location2task(missing_location, missing_tasks)
        if mi_task is not None:
            matched_missing_internal_locations.append(missing_location)
            if len(get_task_runs(mi_task, missing_task_runs)) > 0:
                if missing_location not in found_missing_internal:
                    found_missing_internal.append(missing_location)
    print("    Matched locations: %s" % str(len(matched_missing_internal_locations)))
    print("    Found %s in missing internal" % str(len(found_missing_internal)))

    # Success
    return True


def main(args):

    # File paths
    public_tasks_file = '../Global_QAQC/dartfrog/transform/public/tasks/task.json'
    public_task_runs_file = '../Global_QAQC/dartfrog/transform/public/tasks/task_run.json'
    first_internal_tasks_file = '../Global_QAQC/dartfrog/transform/first-internal/tasks/task.json'
    first_internal_task_runs_file = '../Global_QAQC/dartfrog/transform/first-internal/tasks/task_run.json'
    final_internal_tasks_file = '../Global_QAQC/dartfrog/transform/final-internal/tasks/task.json'
    final_internal_task_runs_file = '../Global_QAQC/dartfrog/transform/final-internal/tasks/task_run.json'
    sweeper_tasks_file = '../Global_QAQC/dartfrog/transform/sweeper-internal/tasks/task.json'
    sweeper_task_runs_file = '../Global_QAQC/dartfrog/transform/sweeper-internal/tasks/task_run.json'
    missing_tasks_file = '../Global_QAQC/dartfrog/transform/missing_tasks/tasks/task.json'
    missing_task_runs_file = '../Global_QAQC/dartfrog/transform/missing_tasks/tasks/task_run.json'

    # Load public task.json
    print("Loading public tasks...")
    public_tasks = load_json(public_tasks_file)
    print("  %s" % str(len(public_tasks)))

    # Load public task_run.json
    print("Loading public task runs...")
    public_task_runs = load_json(public_task_runs_file)
    print("  %s" % str(len(public_task_runs)))

    # Load first internal task.json
    print("Loading first internal tasks...")
    first_internal_tasks = load_json(first_internal_tasks_file)
    print("  %s" % str(len(first_internal_tasks)))

    # Load first internal task_run.json
    print("Loading first internal task runs...")
    first_internal_task_runs = load_json(first_internal_task_runs_file)
    print("  %s" % str(len(first_internal_task_runs)))

    # Load final internal task.json
    print("Loading final internal tasks...")
    final_internal_tasks = load_json(final_internal_tasks_file)
    print("  %s" % str(len(final_internal_tasks)))

    # Load final internal task_run.json
    print("Loading final internal task runs...")
    final_internal_task_runs = load_json(final_internal_task_runs_file)
    print("  %s" % str(len(final_internal_task_runs)))

    # Load sweeper internal task.json
    print("Loading sweeper internal tasks...")
    sweeper_tasks = load_json(sweeper_tasks_file)
    print("  %s" % str(len(sweeper_tasks)))

    # Load sweeper internal task_run.json
    print("Loading sweeper internal task runs...")
    sweeper_task_runs = load_json(sweeper_task_runs_file)
    print("  %s" % str(len(sweeper_task_runs)))

    # Load missing internal task.json
    print("Loading missing internal tasks...")
    missing_tasks = load_json(missing_tasks_file)
    print("  %s" % str(len(missing_tasks)))

    # Load missing internal task_run.json
    print("Loading missing internal task runs...")
    missing_task_runs = load_json(missing_task_runs_file)
    print("  %s" % str(len(missing_task_runs)))

    # == Check For Missing Task Runs == #

    # Check public
    missing_json = []
    print("")
    print("Checking public for missing task runs...")
    missing_public_locations = []
    for task in public_tasks:
        if not does_task_have_task_runs(task, public_task_runs):
            missing_public_locations.append(get_location(task))
    print("  Found %s" % str(len(missing_public_locations)))
    for location in missing_public_locations:
        missing_json.append(location2task(location, public_tasks))

    # If there are any missing public locations, figure out WTF they went
    if len(missing_public_locations) > 0:
        find_missing_task_runs(missing_locations=missing_public_locations,
                               first_internal_tasks=first_internal_tasks,
                               first_internal_task_runs=first_internal_task_runs,
                               final_internal_tasks=final_internal_tasks,
                               final_internal_task_runs=final_internal_task_runs,
                               sweeper_tasks=sweeper_tasks,
                               sweeper_task_runs=sweeper_task_runs,
                               missing_tasks=missing_tasks,
                               missing_task_runs=missing_task_runs)

    # Check first internal
    print("")
    print("Checking first internal for missing task runs...")
    missing_first_internal_locations = []
    for task in first_internal_tasks:
        if not does_task_have_task_runs(task, first_internal_task_runs):
            missing_first_internal_locations.append(get_location(task))
    print("  Found %s" % str(len(missing_first_internal_locations)))

    # If there are any missing public locations, figure out WTF they went
    if len(missing_first_internal_locations) > 0:
        find_missing_task_runs(missing_locations=missing_first_internal_locations,
                               first_internal_tasks=first_internal_tasks,
                               first_internal_task_runs=first_internal_task_runs,
                               final_internal_tasks=final_internal_tasks,
                               final_internal_task_runs=final_internal_task_runs,
                               sweeper_tasks=sweeper_tasks,
                               sweeper_task_runs=sweeper_task_runs,
                               missing_tasks=missing_tasks,
                               missing_task_runs=missing_task_runs)

    # check final internal
    print("")
    print("Checking final internal for missing task runs...")
    missing_final_internal_locations = []
    for task in final_internal_tasks:
        if not does_task_have_task_runs(task, final_internal_task_runs):
            missing_final_internal_locations.append(get_location(task))
    print("  Found %s" % str(len(missing_final_internal_locations)))

    # If there are any missing public locations, figure out WTF they went
    if len(missing_final_internal_locations) > 0:
        find_missing_task_runs(missing_locations=missing_final_internal_locations,
                               first_internal_tasks=first_internal_tasks,
                               first_internal_task_runs=first_internal_task_runs,
                               final_internal_tasks=final_internal_tasks,
                               final_internal_task_runs=final_internal_task_runs,
                               sweeper_tasks=sweeper_tasks,
                               sweeper_task_runs=sweeper_task_runs,
                               missing_tasks=missing_tasks,
                               missing_task_runs=missing_task_runs)

    # Check sweeper internal
    print("")
    print("Checking sweeper internal for missing task runs...")
    missing_sweeper_locations = []
    for task in sweeper_tasks:
        if not does_task_have_task_runs(task, sweeper_task_runs):
            missing_sweeper_locations.append(get_location(task))
    print("  Found %s" % str(len(missing_sweeper_locations)))

    # If there are any missing public locations, figure out WTF they went
    if len(missing_sweeper_locations) > 0:
        find_missing_task_runs(missing_locations=missing_sweeper_locations,
                               first_internal_tasks=first_internal_tasks,
                               first_internal_task_runs=first_internal_task_runs,
                               final_internal_tasks=final_internal_tasks,
                               final_internal_task_runs=final_internal_task_runs,
                               sweeper_tasks=sweeper_tasks,
                               sweeper_task_runs=sweeper_task_runs,
                               missing_tasks=missing_tasks,
                               missing_task_runs=missing_task_runs)

    # Check missing internal
    print("")
    print("Checking missing internal for missing task runs...")
    missing_sweeper_locations = []
    for task in missing_tasks:
        if not does_task_have_task_runs(task, missing_task_runs):
            missing_sweeper_locations.append(get_location(task))
    print("  Found %s" % str(len(missing_sweeper_locations)))

    # If there are any missing public locations, figure out WTF they went
    if len(missing_sweeper_locations) > 0:
        find_missing_task_runs(missing_locations=missing_sweeper_locations,
                               first_internal_tasks=first_internal_tasks,
                               first_internal_task_runs=first_internal_task_runs,
                               final_internal_tasks=final_internal_tasks,
                               final_internal_task_runs=final_internal_task_runs,
                               missing_tasks=missing_tasks,
                               missing_task_runs=missing_task_runs)

    # Success
    print("")
    print("Done.")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))