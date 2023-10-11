#
#!/usr/bin/env python

import os
import xarray as xr
import sqlite3
from glob import glob
import numpy as np
import argparse
import sys
import pandas as pd
import traceback
import dask.dataframe as dd
from dask import delayed


METEO_COLS = ['idPoint', 'w_date', 'year', 'DOY', 'Nmonth', 'NdayM', 'srad', 'tmax', 'tmin', 'tmoy', 'pr',
              'wind', 'rhum', 'Etppm', 'Tdewmin', 'Tdewmax', 'Tdewmean', 'Surfpress']


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

def apply_mask(ds_meteo, ds_mask):
    ds_meteo = ds_meteo.reindex({'lat': sorted(ds_meteo.lat)})
    ds_meteo.coords['mask'] = (
            ('lat', 'lon'), ds_mask.mask.to_masked_array(copy=False))
    df = ds_meteo.where(ds_meteo.mask == 1, drop=True).compute(
        ).to_dataframe().dropna(axis=0, how="any")
    df = df.reset_index()
    df.drop(['mask'], axis=1, inplace=True)
    return df

def process_ncfile(ncfile, ds_mask):
    print(f"Processing {ncfile}")
    df = xr.open_dataset(ncfile)
    df = apply_mask(df, ds_mask)
    return df


def main():
    #try:
    print("meteo_to_db.py")
    work_dir = '/work'
    data_dir = '/inputData'
    parser = argparse.ArgumentParser(
            description='load soil data into database')
    parser.add_argument(
            '-i', '--index', help="Specify the index of the sub virtual experience")
    args = parser.parse_args()
    i = args.index
    EXPS_DIR = os.path.join(work_dir, 'EXPS')
    EXP_DIR = os.path.join(EXPS_DIR, 'exp_' + str(i))
    DB_MI = os.path.join(EXP_DIR, 'MasterInput.db')

    ds_mask = xr.open_dataset(glob(os.path.join(data_dir,'land', '*.nc'))[0])
    ds_mask = ds_mask.reindex({'lat': sorted(ds_mask.lat)})
    df_mask_full = ds_mask.to_dataframe()

    df_mask_full = df_mask_full.reorder_levels(['lat', 'lon'])
    df_mask_full = df_mask_full.sort_index(level='lat')

    df_mask = df_mask_full.dropna(axis=0, how="any")
    df_mask = df_mask.reset_index()

    print(len(df_mask))

    #SLURM_ARRAY_TASK_COUNT = int(os.environ.get("SLURM_ARRAY_TASK_COUNT"))
    #STEP_N = SLURM_ARRAY_TASK_COUNT - 1
    STEP_N = 4000
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
       
    df_mask.loc[~df_mask.index.isin(range(STEP_START, STEP_END)), 'mask'] = None

    df_mask = df_mask.dropna(axis=0, how="any")
    df_mask = df_mask.set_index(['lat', 'lon'])

    da_mask_full = df_mask_full.where(
            df_mask_full.isin(df_mask)).to_xarray()
    ds_mask = ds_mask.where(da_mask_full.mask == 1)

    METEO_DIR = os.path.join(data_dir, 'meteo')
    #parameters = ["2m-dewpoint-temperature", "rainfall"]
    
    parameters = ["2m-dewpoint-temperature", "2m-dewpoint-temperature-max", "2m-dewpoint-temperature-min",\
                     "Rainfall", "Solar-Radiation-Flux", "surface-pressure", "Temperature-Air-2m-Max-24h", \
                     "Temperature-Air-2m-Min-24h", "Temperature-Air-2m-Mean-24h", "Wind-Speed-10m-Mean" ] 
 
    ds_meteo = dd.from_pandas(pd.DataFrame(columns=["lon", "lat", "time"]), npartitions=24)
    print(ds_meteo)
    for parameter in parameters:
        print(parameter)
        param_path = os.path.join(METEO_DIR, parameter)
        ncfiles = glob(os.path.join(param_path, '*.nc'))

            # Process each NetCDF file in parallel
        dfs = [delayed(process_ncfile)(ncfile, ds_mask) for ncfile in ncfiles]

        # Merge DataFrames using Dask
        merged_df = dd.from_delayed(dfs)

            # Merge the Dask DataFrame with the main DataFrame
        if len(ds_meteo.index)==0:
            ds_meteo = merged_df
        else: ds_meteo = ds_meteo.merge(merged_df, on=["lon", "lat", "time"], how="left")
        print(ds_meteo)
        # Compute the final Dask DataFrame
    print("finish merging")
    df = ds_meteo.compute()
    df.loc[:,"lat": "lon"] = df.loc[:,"lat": "lon"].apply(lambda x: np.float64(x).round(4))
    df.loc[:,"Surfpress": "wind"] = df.loc[:,"Surfpress": "wind"].apply(lambda x: np.float64(x).round(1))
    df = format_df_meteo(df)
    with sqlite3.connect(DB_MI) as conn:
        cur = conn.cursor()
        cur.executescript("DROP TABLE RAclimateD;")
        conn.commit()
        df.to_sql('RAclimateD', conn, if_exists='replace', index=False)


if __name__ == "__main__":
    main()
