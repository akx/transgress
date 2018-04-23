import argparse
import json
from functools import partial

import pyproj
from shapely.geometry import shape
from shapely.ops import transform
from shapely.prepared import prep
from tqdm import tqdm


def dump_json(routes_and_points, filename):
    with open(filename, 'w') as outf:
        j_data = [
            (
                route.properties,
                len(matching_points),
                [dict(p['point'].properties, distance=p['distance']) for p in matching_points],
            )
            for (route, matching_points)
            in routes_and_points
        ]
        j_data.sort(key=lambda r: r[1], reverse=True)
        json.dump(j_data, outf, indent=1, sort_keys=True)


def calculate_best(distance_threshold, points, routes):
    routes_and_points = []
    with tqdm(routes, desc='Calculating') as routes_iter:
        for route in routes_iter:
            point_distance_buffered_route = prep(route.buffer(
                distance=distance_threshold,
            ))
            matching_points = [
                {
                    'point': point,
                    'distance': route.distance(point),
                }
                for point in points
                if point_distance_buffered_route.contains(point)
            ]
            routes_and_points.append((route, matching_points))
            routes_iter.set_postfix_str('Best: %d' % max(len(rp[1]) for rp in routes_and_points))
    return routes_and_points


def read_routes(routes_geojson, project_to_meters):
    with open(routes_geojson, 'r') as rf:
        routes_json = json.load(rf)
        routes = []
        for route_info in tqdm(routes_json['features'], desc='Routes'):
            route = transform(project_to_meters, shape(route_info['geometry']))
            route.properties = route_info['properties']
            routes.append(route)
    return routes


def read_points(points_geojson, project_to_meters):
    with open(points_geojson, 'r') as pf:
        points_json = json.load(pf)
        points = []
        for point_info in tqdm(points_json['features'], desc='Points'):
            point = transform(project_to_meters, shape(point_info['geometry']))
            point.properties = point_info['properties']
            point.properties['coords'] = point_info['geometry']['coordinates']
            points.append(point)
    return points


def cli():
    ap = argparse.ArgumentParser()
    ap.add_argument('--points-geojson', '-p', required=True)
    ap.add_argument('--routes-geojson', '-r', required=True)
    ap.add_argument('--output-json', '-o', default='route-rate.json')
    ap.add_argument('--distance-threshold', '-d', type=float, default=40)
    ap.add_argument('--source-proj', default='EPSG:4326')  # WGS 84
    ap.add_argument('--measurement-proj', default='EPSG:3067')  # ETRS-TM35FIN (only for Finland)
    # Also try "EPSG:32634" ( UTM zone 34 N (http://www.dmap.co.uk/utmworld.htm)) for measurement
    args = ap.parse_args()
    project_to_meters = partial(
        pyproj.transform,
        pyproj.Proj(init=args.source_proj),
        pyproj.Proj(init=args.measurement_proj),
    )

    points = read_points(args.points_geojson, project_to_meters)
    routes = read_routes(args.routes_geojson, project_to_meters)
    routes_and_points = calculate_best(args.distance_threshold, points, routes)
    dump_json(routes_and_points, filename=args.output_json)


if __name__ == '__main__':
    cli()
