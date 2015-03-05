#!/usr/bin/env python


"""
Convert output from http://crowd.skytruth.org/app/frackfinder-ohio-wellpad-tracer/
to an OGR datasource.
"""


from collections import OrderedDict
import json
import sys

import click
import fiona


_t = {
    'app_id': 27,
    'calibration': 0,
    'created': '2015-02-02T20:21:35.943786',
    'id': 30293,
    'info': {
        'apis': '["34081205140000", "34081205200000", "34081205250000"]',
        'county': 'Jefferson',
        'imagery': [
            {
                'active': True,
                'options': {
                    'layers': '06136759344167181854-11275828430006462017-4'
                },
                'title': '2013',
                'type': 'WMS',
                'url': 'https://mapsengine.google.com/06136759344167181854-11845109403981099587-4/wms/'},
            {
                'options': {
                    'layers': '06136759344167181854-08224624193234342065-4'
                },
                'title': '2011',
                'type': 'WMS',
                'url': 'https://mapsengine.google.com/06136759344167181854-11845109403981099587-4/wms/'},
            {
                'options': {
                    'layers': '06136759344167181854-04770958895915995837-4'
                },
                'title': '2010',
                'type': 'WMS',
                'url': 'https://mapsengine.google.com/06136759344167181854-11845109403981099587-4/wms/'}],
        'latitude': 40.520639475001744,
        'longitude': -80.91696537501242,
        'n_answers': 10,
        'question': 'Please drag on the edges of the shape to make it fit the drill pad you see in the satellite image',
        'siteID': '93411b2a86894f569ff1ab722f2c1e18',
        'size': 200,
        'state': 'OH',
        'year': '2013'
    },
    'n_answers': 10,
    'priority_0': 0.0,
    'quorum': 0,
    'state': 'completed',
    'task_runs_nr': 12
}


_tr = {
    'app_id': 27,
    'calibration': None,
    'created': '2015-02-03T03:01:40.202908',
    'finish_time': '2015-02-03T03:01:40.202930',
    'id': 139096,
    'info': {
        'done': {
            'tasks': 1
        },
        'selection': 'done',
        'shapes': [
            {
                'coordinates': [
                    [
                        [-80.98388794448, 40.671508973115],
                        [-80.982774941605, 40.671033690807],
                        [-80.982155269735, 40.672261002085],
                        [-80.983147947974, 40.672609943526],
                        [-80.98388794448, 40.671508973115]
                    ]
                ],
                'type': 'Polygon'
            }
        ],
        'timings': {
            'presentTask': 6635,
            'reportAnswer': 6999
        }
    },
    'task_id': 30158,
    'timeout': None,
    'user_id': 350,
    'user_ip': None
}




@click.command()
@click.argument(
    'task_json', metavar='task.json', type=click.File(mode='r'), required=True)
@click.argument(
    'task_run_json', metavar='task_run.json', type=click.File(mode='r'), required=True)
@click.argument(
    'outfile', metavar='outfile', required=True
)
@click.option(
    '-f', '--format', '--driver', metavar='NAME', default='GeoJSON',
    help="Output driver."
)
def main(task_json, task_run_json, outfile, driver):

    """
    Convert task.json and task_run.json to a spatial format.
    """

    # Index the tasks on  and task_runs on task_id
    loaded_tasks = {t['id']: t for t in json.load(task_json)}
    loaded_task_runs = {}
    for tr in json.load(task_run_json):
        if tr['task_id'] in loaded_task_runs:
            loaded_task_runs[tr['task_id']].append(tr)
        else:
            loaded_task_runs[tr['task_id']] = [tr]

    # Update user
    click.echo("Found %s tasks" % len(loaded_tasks))
    click.echo("Found %s matching task run ID's" % len(loaded_task_runs))

    # Output vector schema
    meta = {
        'schema': {
            'geometry': 'MultiPolygon',
            'properties': OrderedDict({
                'app_id': 'int',
                'id': 'int',
                'n_answers': 'str',
                'n_responses': 'int',
                'selection': 'str',
                'task': 'str:255',
                'task_run': 'str:255',
                'task_id': 'int'
            })
        },
        'crs': 'EPSG:4326',
        'driver': driver,
    }

    with fiona.open(outfile, 'w', **meta) as dst:

        with click.progressbar(loaded_tasks) as progress_bar:
            num_task_run_with_no_geometry = 0

            # Loop over every unique input task
            for task_id in progress_bar:
                task = loaded_tasks[task_id]

                # Loop over every associated task run
                for tr in loaded_task_runs[task_id]:

                    # Only write features where the user actually drew a shape
                    if 'shapes' not in tr['info']:
                        num_task_run_with_no_geometry += 1
                    else:
                        dst.write(
                            {
                                'type': 'Feature',
                                'geometry': {
                                    'type': dst.meta['schema']['geometry'],
                                    'coordinates': [shape['coordinates'] for shape in tr['info']['shapes']]
                                },
                                'properties': {
                                    'app_id': task['app_id'],
                                    'id': task['id'],
                                    'n_answers': task['n_answers'],
                                    'n_responses': task['task_runs_nr'],
                                    'selection': tr['info']['selection'],
                                    'task': json.dumps(task),
                                    'task_run': json.dumps(tr),
                                    'task_id': tr['task_id']
                                }
                            }
                        )

    click.echo("Skipped %s task runs because they had no geometry" % num_task_run_with_no_geometry)
    click.echo("Done.")
    sys.exit(0)

if __name__ == '__main__':
    main()
