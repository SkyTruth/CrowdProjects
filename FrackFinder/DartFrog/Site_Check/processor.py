#!/usr/bin/env python


import sys
import json
from pprint import pprint


def get_location(record, return_dict=False):
    lat = record['info']['latitude']
    lng = record['info']['longitude']
    year = record['info']['year']
    if return_dict:
        return {'lat': lat,
                'lng': lng,
                'year': year}
    else:
        return str(lat) + str(lng) + '-' + str(year)


def main(args):

    # Define input files
    public_tasks = 'public/task.json'
    public_task_runs = 'public/task_run.json'
    public_combined = 'public/combined.json'
    internal_tasks = 'internal/task.json'
    internal_task_runs = 'internal/task_run.json'
    internal_combined = 'internal/combined.json'

    # == Load public files into a JSON object == #
    print("Parsing public files...")

    # Public tasks
    with open(public_tasks, 'r') as f:
        public_tasks_json = json.load(f)

    # Public task runs
    with open(public_task_runs, 'r') as f:
        public_task_runs_json = json.load(f)

    # Public combined
    with open(public_combined, 'r') as f:
        public_combined_json = json.load(f)

    # == Load internal files into a JSON object == #
    print("Parsing internal files...")

    # Internal tasks
    with open(internal_tasks, 'r') as f:
        internal_tasks_json = json.load(f)

    # Internal task runs
    with open(internal_task_runs, 'r') as f:
        internal_task_runs_json = json.load(f)

    # Internal combined
    with open(internal_combined, 'r') as f:
        internal_combined_json = json.load(f)

    # Give user some status
    print("Public received %s tasks" % str(len(public_tasks_json)))
    print("Public completed %s task runs" % str(len(public_task_runs_json)))
    print("Internal received %s tasks" % str(len(internal_tasks_json)))
    print("Internal completed %s task runs" % str(len(internal_task_runs_json)))

    # Check out ID structure works
    candidate_tasks = []
    print("Checking for matching IDS...")
    num_tasks = len(public_tasks_json)
    i = 0
    for task in public_tasks_json:
        task_id = int(task['id'])
        count = 0
        for task_run in public_task_runs_json:
            task_run_id = int(task_run['task_id'])
            if task_id == task_run_id:
                count += 1
        if count is not 0:
            if count < 10:
                candidate_tasks.append(task)
    print("Num candidate tasks: %s" % str(len(candidate_tasks)))

    # Brute force write candidate tasks
    print("Writing candidate tasks to a file...")
    with open('FORCE-Candidate_Tasks.txt', 'w') as f:
        f.write(str(candidate_tasks))
    with open('Candidate_Tasks.json', 'w') as f:
        json.dump(candidate_tasks, f)

    # Compare candidate tasks to internal tasks
    final_tasks = []
    print("Comparing candidate tasks to internal...")
    i = 0
    num_total_tasks = len(candidate_tasks)
    drop_count = 0
    for candidate in candidate_tasks:
        candidate_location = get_location(candidate)
        candidate_id = int(candidate['id'])
        keep_candidate = True
        for internal_task in internal_tasks_json:
            internal_task_location = get_location(internal_task)
            if candidate_location == internal_task_location:
                keep_candidate = False
                #internal_task_run_count = 0
                #for internal_task_run in internal_task_runs_json:
                #    internal_task_run_id = int(internal_task_run['task_id'])
                #    if int(candidate_id) == int(internal_task_run_id):
                #        internal_task_run_count += 1
                #        print("  Task run found: %s" % internal_task_run_count)
                #if internal_task_run_count >= 3:
                #    print("  Dropping candidate")
                #    keep_candidate = False
                #    drop_count += 1
        if keep_candidate:
            #print("Keeping candidate: %s" % candidate_location)
            final_tasks.append(candidate)
    print("Dropped %s tasks" % str(drop_count))
    print("Found %s final tasks" % str(len(final_tasks)))

    # Write final tasks
    print("Forcing final task write...")
    with open('FORCE-Final_Tasks.txt', 'w') as f:
        f.write(str(final_tasks))
    with open('Final_Tasks.json', 'w') as f:
        json.dump(final_tasks, f)

    # Write final tasks to file
    print("Writing final tasks to a file...")

    # Success
    print("Done.")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))