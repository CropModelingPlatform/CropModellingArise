#!/usr/bin/env python

import os
import xarray as xr
import sqlite3
from glob import glob
import numpy as np
import argparse
import sys
import traceback


def main():
    try:
        print("soil_to_db.py")
        # work_dir = os.getcwd()
        work_dir = '/work'
        parser = argparse.ArgumentParser(description='load soil data into database')
        parser.add_argument('-i', '--index', help="Specify the index of the sub virtual experience")
        args = parser.parse_args()
        i = args.index
        EXPS_DIR = os.path.join(work_dir, 'EXPS')
        EXP_DIR = os.path.join(EXPS_DIR, 'exp_' + str(i))
        DB_MI = os.path.join(EXP_DIR, 'MasterInput.db')

        ds_mask = xr.open_dataset(os.path.join(work_dir, 'data', 'land', 'GFSAD1KCM_senegal_5km_fin.nc'))
        ds_mask = ds_mask.reindex({'lat': sorted(ds_mask.lat)})
        df_mask = ds_mask.to_dataframe().dropna(axis=0, how="any")
        df_mask = df_mask.reset_index()
        df_mask = df_mask.astype(np.float64).round(4)
        df_mask.columns = ['lat', 'lon', 'mask']
        df_mask = df_mask.set_index(['lat', 'lon'])

        SOIL_DIR = os.path.join(work_dir, 'data', 'soil', '5km')
        ncs = glob(os.path.join(SOIL_DIR, '*_fin.nc'))
        ds = xr.open_mfdataset(ncs, cache=False)
        ds = ds.reindex({'lat': sorted(ds.lat)})
        ds.coords['mask'] = (('lat', 'lon'), ds_mask.mask.to_masked_array(copy=True))
        # ds = ds.where(ds.mask == 1)
        df = ds.to_dataframe().dropna(axis=0, how="any")
        df = df.reset_index()
        df = df.astype(np.float64).round(4)
        df = df.round({'OrganicNStock': 3, 'pH': 1, 'OrganicC':2, 'cf':1})

        with sqlite3.connect(DB_MI) as conn:
            df.to_sql('SoilTemp', conn, if_exists='replace', index=False)

        sql_as_string = ''
        with open(os.path.join(work_dir, 'scripts', 'db', 'init_soil.sql')) as f:
            sql_as_string = f.read()
        # print(sql_as_string)

        with sqlite3.connect(DB_MI) as conn:
            cur = conn.cursor()
            cur.executescript(sql_as_string)
            conn.commit()
            cur.executescript("DROP TABLE SoilTemp;")
            conn.commit()
    except:
        print("Unexpected error have been catched:", sys.exc_info()[0])
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
