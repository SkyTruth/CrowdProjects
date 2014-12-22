#!/usr/bin/env python


"""
Create input tasks for 2010-2013 pad delineator
"""


import argparse
import json
import os
import time
from pprint import pprint
import sys


def get_classification(task_runs):

    """
    Determine task run's classification based on the crowd's response

    Returns
    -------
    str
        Classification
    """

    output = None
    responses = {}

    for tr in task_runs:
        selection = tr['info']['selection']
        if selection in responses:
            responses[selection] += 1
        else:
            responses[selection] = 1

    max_selection = max(responses.values())

    for resp, count in responses.items():

        # The output has not been set yet and the count for this response matches the maximum number of counts
        if output is None and count is max_selection:
            output = resp

        # The output has already been set, which means that there are at least two responses that tied for first place
        # Only one of these occurred in the Tadpole tasks so just return None
        elif output is not None and count is max_selection:
            return None

    return output


def main(args):

    # Parse arguments
    parser = argparse.ArgumentParser(description="Create input tasks for OH pad delineator 2010-2013")
    parser.add_argument(
        'input_tasks', metavar='task.json', help="Input task.json")
    parser.add_argument(
        'input_task_runs', metavar='Input task_run.json')
    parser.add_argument(
        'output_tasks', metavar='output-tasks.json', help="Output task file")
    parser.add_argument(
        '--overwrite', default=False, action='store_true')
    pargs = parser.parse_args(args=args)

    # Validate
    if not os.access(pargs.input_tasks, os.R_OK):
        print("ERROR: Can't find input tasks: {}".format(pargs.input_tasks))
        return 1
    elif not os.access(pargs.input_tasks, os.R_OK):
        print("ERROR: Can't find input task runs: {}".format(pargs.input_task_runs))
        return 1
    elif not pargs.overwrite and os.path.isfile(pargs.output_tasks):
        print("ERROR: Output file exists and overwrite={0}: {1}".format(pargs.overwrite, pargs.output_tasks))
        return 1

    # Cache files and index by ID
    with open(pargs.input_tasks) as f:
        tasks = json.load(f)
    with open(pargs.input_task_runs) as f:
        task_runs = json.load(f)

    # Index tasks by SiteID so that {site_id: [task1, t2, ...]}
    input_tasks = {}
    for task in tasks:
        tid = task['id']
        if tid in input_tasks:
            input_tasks[tid].append(task)
        else:
            input_tasks[tid] = [task]

    # Index task runs by ID so that {id: [task1, t2, ...]}
    input_task_runs = {}
    for tr in task_runs:
        tid = tr['task_id']
        if tid in input_task_runs:
            input_task_runs[tid].append(tr)
        else:
            input_task_runs[tid] = [tr]

    # Container for all output tasks
    output_tasks = []
    allowed_fields = ['info', 'apis', 'county', 'latitude', 'longitude', 'options', 'siteID', 'size', 'state', 'url', 'year']

    # Process all site ID's in the input_tasks (task.json)
    progress_total = len(input_tasks)
    progress_i = 0
    num_output_tasks = 0
    print("Processing site ID's ...")
    for tid, tasks in input_tasks.items():

        progress_i += 1
        sys.stdout.write("\r\x1b[K" + "    {0}/{1}".format(progress_i, progress_total))
        sys.stdout.flush()
        if progress_i >= progress_total:
            sys.stdout.write(os.linesep)

        # Sort the associated tasks in year order
        ordered_tasks = []
        _tasks = {int(t['info']['year']): t for t in tasks}
        for y in sorted(_tasks.keys()):
            ordered_tasks.append(_tasks[y])

        # Write each task in sorted order
        for task in sorted(ordered_tasks):

            classification = get_classification([tr for tr in input_task_runs[tid] if tr['task_id'] == tid])
            if classification is not None and classification.lower() == 'pad':

                num_output_tasks += 1

                # Strip off all the non-required fields
                otask = {key: val for key, val in task.copy().items() if key in allowed_fields}

                # The first two API's are duplicates - force a unique list
                otask['info']['apis'] = json.dumps(list(set(json.loads(task['info']['apis']))))

                output_tasks.append(task)

    # Done
    with open(pargs.output_tasks, 'w') as f:
        json.dump(output_tasks, f)
    print("Wrote {} output tasks".format(num_output_tasks))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
