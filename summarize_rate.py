import argparse
import json
from operator import itemgetter

import tabulate


def uniq(arr, key=lambda v: v):
    seen = set()
    for value in arr:
        k = key(value)
        if k not in seen:
            seen.add(k)
            yield value


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file')
    ap.add_argument('--limit', type=int, default=50)
    ap.add_argument('--expr-limit', type=int, default=10)
    ap.add_argument('--sort-by-col', type=int, default=2)
    ap.add_argument('--sort-asc', dest='sort_reverse', action='store_false', default=True)
    ap.add_argument('--sort-desc', dest='sort_reverse', action='store_true')

    args = ap.parse_args()

    with open(args.file, 'r') as jf:
        j_data = json.load(jf)

    sum_data = [(
        ', '.join(j['route']['routes']),
        j['route']['shape_id'],
        j['n_points'],
        j['length'] / 1000,
        j['n_points'] / (j['length'] / 1000),
    ) for j in j_data]
    sum_data_uniq = list(uniq(sum_data, itemgetter(0)))
    sum_data_uniq.sort(key=itemgetter(args.sort_by_col), reverse=args.sort_reverse)

    print(tabulate.tabulate(
        sum_data_uniq[:args.limit],
        headers=('route', 'shape', 'points', 'length(km)', 'points-per-km'),
    ))
    print('"shape_id" in (%s)' % ', '.join("'%s'" % j['route']['shape_id'] for j in j_data[:args.expr_limit]))


if __name__ == '__main__':
    main()
