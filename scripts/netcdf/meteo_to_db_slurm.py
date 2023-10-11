#!/usr/bin/env python

import os
import xarray as xr
import sqlite3
from glob import glob
import numpy as np
import argparse
import sys
import traceback

METEO_COLS = ['idPoint', 'w_date', 'year', 'DOY', 'Nmonth', 'NdayM', 'srad', 'tmax', 'tmin', 'tmoy', 'rain',
              'wind', 'rhum', 'Etppm', 'Tdewmin', 'Tdewmax', 'Surfpress']


def format_df_meteo(df):
    df['year'] = df.time.apply(lambda l: l.year)
    df['Nmonth'] = df.apply(lambda l: l.time.month, axis=1)
    df['NdayM'] = df.apply(lambda l: l.time.day, axis=1)
    df['DOY'] = df.apply(lambda l: l.time.dayofyear, axis=1)
    df['w_date'] = df.apply(lambda l: l.time.strftime('%Y-%m-%d'), axis=1)
    df['idPoint'] = df.apply(lambda l: str(
        round(l.lat, 4)) + '_' + str(round(l.lon, 4)), axis=1)
    df['rhum'] = None
    df['Etppm'] = None
    df = df.reset_index()
    df = df[METEO_COLS]
    return df


def main():
    try:
        print("meteo_to_db.py")
        # work_dir = os.getcwd()
        work_dir = '/work'
        parser = argparse.ArgumentParser(
            description='load soil data into database')
        parser.add_argument(
            '-i', '--index', help="Specify the index of the sub virtual experience")
        args = parser.parse_args()
        i = args.index
        EXPS_DIR = os.path.join(work_dir, 'EXPS')
        EXP_DIR = os.path.join(EXPS_DIR, 'exp_' + str(i))
        DB_MI = os.path.join(EXP_DIR, 'MasterInput.db')

        ds_mask = xr.open_dataset(os.path.join(
            work_dir, 'data', 'land', 'GFSAD1KCM_senegal_5km_fin.nc'))
        ds_mask = ds_mask.reindex({'lat': sorted(ds_mask.lat)})
        df_mask_full = ds_mask.to_dataframe()
        df_mask = df_mask_full.dropna(axis=0, how="any")
    
        df_mask = df_mask.reset_index()
        df_mask.columns = ['lat', 'lon', 'mask']
        df_mask = df_mask.set_index(['lat', 'lon'])

        STEP_N = int(os.environ.get("SLURM_ARRAY_TASK_COUNT"))
        #STEP_N = 87
        STEP_IDX = int(i)
        DF_LEN = len(df_mask)
        STEP_SIZE = int(DF_LEN/STEP_N)
        STEP_START = STEP_IDX * STEP_SIZE
        if STEP_IDX == STEP_N:
            STEP_END = DF_LEN
        else:
            STEP_END = (STEP_IDX + 1) * STEP_SIZE

        print("STEP_START : " + str(STEP_START))
        print("STEP_END : " + str(STEP_END))
        print("END - START : " + str(STEP_END - STEP_START))
       
        df_mask.iloc[0:STEP_START, :] = None
        df_mask.iloc[STEP_END:, :] = None

        df_mask = df_mask.dropna(axis=0, how="any")
        da_mask_full = df_mask_full.where(
            df_mask_full.isin(df_mask)).to_xarray()
        ds_mask = ds_mask.where(da_mask_full.mask == 1)

        METEO_DIR = os.path.join(work_dir, 'data', 'meteo', '5km')
        ncs = glob(os.path.join(METEO_DIR, '*_fin.nc'))
        ds_meteo = xr.open_mfdataset(ncs, cache=True, parallel=True)
        ds_meteo = ds_meteo.reindex({'lat': sorted(ds_meteo.lat)})
        ds_meteo.coords['mask'] = (
            ('lat', 'lon'), ds_mask.mask.to_masked_array(copy=False))
        df = ds_meteo.where(ds_meteo.mask == 1, drop=True).compute(
        ).to_dataframe().dropna(axis=0, how="any")

        df = df.reset_index()
        df.drop(['mask'], axis=1, inplace=True)
        df.loc[:,"lat": "lon"] = df.loc[:,"lat": "lon"].apply(lambda x: np.float64(x).round(4))
        df.loc[:,"Surfpress": "wind"] = df.loc[:,"Surfpress": "wind"].apply(lambda x: np.float64(x).round(1))
        df = format_df_meteo(df)
        print(df.head(5))
        print(DB_MI)
        with sqlite3.connect(DB_MI) as conn:
            cur = conn.cursor()
            cur.executescript("DROP TABLE RAclimateD;")
            conn.commit()
            df.to_sql('RAclimateD', conn, if_exists='replace', index=False)
    except:
        print("Unexpected error have been catched:", sys.exc_info()[0])
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
