import argparse
import json

import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--gtfs-dir', '-d', required=True)
    ap.add_argument('--output', '-o', required=True)
    args = ap.parse_args()
    print('Reading data...')
    routes = pd.read_csv('%s/routes.txt' % args.gtfs_dir)
    routes = pd.read_csv('%s/trips.txt' % args.gtfs_dir).join(routes, on='route_id', rsuffix='_r')
    shapes = pd.read_csv('%s/shapes.txt' % args.gtfs_dir)
    shape_points = shapes.groupby('shape_id').apply(lambda pts: pts[['shape_pt_lon', 'shape_pt_lat']].values.tolist())

    lon = shapes['shape_pt_lon']
    lat = shapes['shape_pt_lat']
    bbox = ((lon.min(), lat.min()), (lon.max(), lat.max()))
    print('Bounding box:', bbox)

    print('Generating GeoJSON...')
    geojson_objs = []
    for shape_id, routes in routes.groupby('shape_id'):
        routes = routes.to_dict('records')
        route_descs = set(
            '%s - %s' % (r['route_short_name'], r['route_long_name'])
                for r
                in routes
        )
        geojson_objs.append(
            {
                'type': 'Feature',
                'properties': {
                    'routes': sorted(route_descs),
                    'shape_id': shape_id,
                },
                'geometry': {
                    'type': 'LineString',
                    'coordinates': shape_points[shape_id],
                }
            })

    print('Writing...')
    with open(args.output, 'w') as outf:
        json.dump({
            'type': 'FeatureCollection',
            'features': geojson_objs,
        }, outf)


if __name__ == '__main__':
    main()
