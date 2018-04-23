import argparse
import json

import pandas as pd


def read_shape_data(store):
    print('Reading shape data...')
    shapes = store.shapes
    shape_points = dict((
        shapes
            .sort_values(['shape_id', 'shape_pt_sequence'])
            .groupby('shape_id')
            .apply(lambda pts: pts[['shape_pt_lon', 'shape_pt_lat']].values.tolist())
    ))
    lon = shapes['shape_pt_lon']
    lat = shapes['shape_pt_lat']
    bbox = ((lon.min(), lat.min()), (lon.max(), lat.max()))
    return bbox, shape_points


def generate_geojson(routes, shape_points):
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
    return geojson_objs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--hdf5-input', '-i', required=True)
    ap.add_argument('--output', '-o', required=True)
    args = ap.parse_args()
    store = pd.HDFStore(args.hdf5_input)
    print('Reading trip and route data...')
    routes = store.trips.join(store.routes.set_index('route_id'), on='route_id', rsuffix='_r')

    bbox, shape_points = read_shape_data(store)
    print('Bounding box:', bbox)

    print('Generating GeoJSON...')
    geojson_objs = generate_geojson(routes, shape_points)

    print('Writing...')
    with open(args.output, 'w') as outf:
        json.dump({
            'type': 'FeatureCollection',
            'features': geojson_objs,
        }, outf)


if __name__ == '__main__':
    main()
