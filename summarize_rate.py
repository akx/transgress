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

    args = ap.parse_args()

    with open(args, 'r') as jf:
        j_data = json.load(jf)

    sum_data = [(', '.join(j[0]['routes']), j[0]['shape_id'], j[1]) for j in j_data]
    sum_data_uniq = list(uniq(sum_data, itemgetter(0)))
    print(tabulate.tabulate(sum_data_uniq[:args.limit]))
    print('"shape_id" in (%s)' % ', '.join("'%s'" % j[0]['shape_id'] for j in j_data[:args.expr_limit]))


if __name__ == '__main__':
    main()
