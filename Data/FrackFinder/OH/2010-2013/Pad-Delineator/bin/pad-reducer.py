#!/usr/bin/env python


from __future__ import division

import copy
import math

import affine
import click
import fiona as fio
import numpy as np
import rasterio as rio
from rasterio.features import rasterize
from shapely.geometry import mapping
from rasterio.features import shapes as polygonize
from shapely.geometry import shape


def _cb_agreement(ctx, param, value):

    """
    Click callback to convert agreement to a float if necessary.
    Also does validation.
    """

    if value.lower() == 'mean':
        return 'mean'
    else:
        try:
            value = float(value)
            if 0 <= value <= 1:
                return value
            else:
                raise click.BadParameter("Float values must be >= 0 and <= 1.")
        except ValueError:
            raise click.BadParameter("Must be 'mean' or a float.")


def _cb_gt_zero(ctx, param, value):

    """
    Click callback to validate integers and floats that must be >= 0

    Parameters
    ----------
    ctx : click.Context
        Ignored.
    param : click.Param
        Ignored.
    value : float
        Must be positive.

    Returns
    -------
    float
    """

    if not value >= 0:
        raise click.BadParameter("must be >= 0, not `{0}'".format(value))
    return value


def bbox_from_stack(stack):

    """
    Compute the minimum bounding box from an iterable of geometries.

    Parameters
    ----------
    stack : iter
        An iterable producing one GeoJSON geometry per iteration.

    Returns
    -------
    tuple
        (x_min, y_min, x_max, y_max)
    """

    x_min = None
    y_min = None
    x_max = None
    y_max = None
    for geom in stack:
        g_x_min, g_y_min, g_x_max, g_y_max = shape(geom).bounds
        if x_min is None or g_x_min < x_min:
            x_min = g_x_min
        if y_min is None or g_y_min < y_min:
            y_min = g_y_min
        if x_max is None or g_x_max > x_max:
            x_max = g_x_max
        if y_max is None or g_y_max > y_max:
            y_max = g_y_max

    return x_min, y_min, x_max, y_max


def geometric_mean(stack, bbox, res, agreement, id):

    """
    Compute the geomtric mean from a stack of GeoJSON geometries.  The algorithm
    does the following:

        1. Rasterize each geometry against the same grid and extent.
        2. Compute the number of geometries that intersect any given pixel.
        3. Compute the mean number of intersections.
        4. Mark any value < the mean as 0.
        5. Mark any value >= the mean as 1.
        6. Polygonize the remaining pixels and return.

    Parameters
    ----------
    stack : iter
        An iterable producing one GeoJSON feature per iteration.
    bbox : tuple

    res : int or tuple

    Returns
    -------
    """

    x_min, y_min, x_max, y_max = bbox

    aff = affine.Affine(res, 0.0, x_min,
                        0.0, -abs(res), y_max)
    width = math.ceil((x_max - x_min) / res)
    height = math.ceil((y_max - y_min) / res)
    data = np.zeros((height, width), dtype=np.int16)
    for geom in stack:
        data += rasterize(
            shapes=[geom],
            out_shape=(height, width),
            fill=0,
            transform=aff,
            all_touched=False,
            default_value=1,
            dtype=data.dtype
        )
    data = np.ma.array(data, mask=data == 0)

    if agreement == 'mean':
        breakpoint = data.mean()
    else:
        breakpoint = agreement * data.max()

    data[data < breakpoint] = 0
    data[data >= breakpoint] = 1

    if id == 30116:
        h, w = data.shape
        _meta = {
            'count': 1,
            'height': h,
            'width': w,
            'driver': 'GTiff',
            'crs': 'EPSG:4326',
            'transform': aff,
            'dtype': data.dtype
        }
        with rio.open('30116.tif', 'w', **_meta) as dst:
            dst.write(data, indexes=1)

    for geom, _ in polygonize(image=data, mask=~(data == 0), transform=aff):
        yield geom


@click.command()
@click.argument('infile', type=click.Path(exists=True, dir_okay=False), required=True)
@click.argument('outfile', required=True)
@click.option(
    '--agreement', metavar="'MEAN' | FLOAT", default='mean', callback=_cb_agreement,
    help='Percent agreement of overlapping polygons. Can "mean" or a percent as a float. '
         '(default: mean)'
)
@click.option(
    '-f', '--format', '--driver', default='ESRI Shapefile',
    help='Output driver name. (default: ESRI Shapefile)'
)
@click.option(
    '-r', '--res', type=click.FLOAT, default=0.00001, callback=_cb_gt_zero,
    help='Resolution for rasterized geometries. (default: 0.00001)'
)
@click.option(
    '-t', '--tolerance', type=click.FLOAT, default=0.00001, callback=_cb_gt_zero,
    help='Simplify tolerance. (default: 0.00001)'
)
def main(infile, outfile, agreement, driver, res, tolerance):

    """
    Convert stacks of ponds to a single geometry.
    """

    with fio.open(infile) as src:
        meta = src.meta.copy()
        src_features = [f for f in src]
        second_features = copy.deepcopy(src_features)

    click.echo("Processing %s features ..." % len(src_features))

    processed_fids = set()
    meta['schema']['properties'] = {'task_id': 'int:10'}
    meta['driver'] = driver
    with fio.open(outfile, 'w', **meta) as dst, \
            click.progressbar(src_features) as input_features:
        for idx, feature in enumerate(input_features):
            if feature['id'] not in processed_fids:
                try:
                    geom = shape(feature['geometry'])
                except Exception as e:
                    geom = None
                    click.echo(e, err=True)
                if geom is not None:
                    bbox = geom.bounds
                    stack = [
                        f for f in second_features
                        if f['properties']['task_id'] == feature['properties']['task_id']
                        and f['id'] not in processed_fids]
                    assert len(stack) == len(set([f['id'] for f in stack]))
                    for f in stack:
                        processed_fids.add(f['id'])
                    for out_geom in geometric_mean(
                            [f['geometry'] for f in stack], bbox, res=res, agreement=agreement, id=stack[0]['properties']['task_id']):
                        dst.write({
                            'type': 'Feature',
                            'properties': {'task_id': feature['properties']['task_id']},
                            'geometry': mapping(
                                shape(out_geom).simplify(tolerance, preserve_topology=True))
                        })


if __name__ == '__main__':
    main()
