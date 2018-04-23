import argparse
import io
import os
import zipfile

import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--gtfs-zip', '-z', required=True)
    ap.add_argument('--hdf5-output', '-o', required=True)
    args = ap.parse_args()
    with pd.HDFStore(args.hdf5_output) as store:
        with zipfile.ZipFile(args.gtfs_zip) as zf:
            for name in zf.namelist():
                if name.endswith('.txt'):
                    print('Reading %s...' % name)
                    store[os.path.splitext(name)[0]] = pd.read_csv(io.BytesIO(zf.read(name)))


if __name__ == '__main__':
    main()
