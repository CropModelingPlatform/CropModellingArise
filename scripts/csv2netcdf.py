#!/usr/bin/env python

import os
import sqlite3
from glob import glob
import xarray as xr
import pandas as pd
import numpy as np
# import dask
# from numba import jit
import time
# from dask.distributed import Client
# import multiprocessing
from joblib import Parallel, delayed
from datetime import datetime, date
import subprocess
# import matplotlib.pyplot as plt

THREADS = 100

#  netcdf TNZ_chirps-v2.0.1981-2019.days_p05_2000-2001 {
#  dimensions:
#       time = UNLIMITED ; // (731 currently)
nlon = 1440
nlat = 1344
nt = 731

t_start = 0
t_end = nt
t_step = 10
lon_start = 0
lon_end = nlon
lon_step = 100

work_dir = '/work'
# work_dir = '.'
# work_dir = '/media/guyomji/DATA_ON_MX500/Documents/data/TEST'
os.chdir(work_dir)

# work_dir = os.getcwd()
print('work_dir : ' + work_dir)

mask_file = os.path.join(work_dir, 'ANNUAL_AREA_HARVESTED_IRC_CROP2_HA_mask.nc')
# output_dir = os.path.join(work_dir, 'OUTPUT')
output_dir = os.path.join(work_dir, 'SIM2010CPL')


def get_coord(fn):
    tp = fn.replace("mod_s", "").split("_")
    ln = tp[0].replace("xxx", ".")
    lt = tp[1].split("xxx")
    return {'lon': float(ln), 'lat': float(lt[0] + '.' + lt[1])}


def load_csv_sub(f):
    f_name = os.path.basename(f)
    c = get_coord(f_name)
    df = pd.read_csv(f, sep=';')
    df = df.reset_index().rename(columns={"lai(n)": "lai"})
    df = df[['ian', 'mo', 'jo', 'lai']]
    df['time'] = df.apply(lambda l: datetime(int(l.ian), int(l.mo), int(l.jo)), axis=1)
    df['lon'] = c['lon']
    df['lat'] = c['lat']
    df = df[['time', 'lat', 'lon', 'lai']]
    # df = df.set_index(['time', 'lat', 'lon'])
    # print(df)
    return df

print('convert csv to netcdf...')
# ds_mask = xr.load_dataset(mask_file)
input_dir = output_dir
for l in range(lon_start, lon_end, lon_step):
    e = os.path.join(input_dir, 'exp_' + str(l))
    print(e)
    files = glob(os.path.join(e, '*', '*', 'mod_s*'))
    # print(len(files))
    dfin = pd.DataFrame()
    res = Parallel(n_jobs=THREADS, verbose=100, max_nbytes=None, prefer="processes")(
        delayed(load_csv_sub)(f) for f in files)
    #print("res")
    dffin = pd.concat(res)
    dsfin = dffin.set_index(['time', 'lat', 'lon']).to_xarray()
    # dst = ds.isel(time=300)
    ds_mask = xr.load_dataset(mask_file)
    ds_mask_sub = ds_mask.isel(lon=slice(l, l + lon_step))
    df_mask_sub = ds_mask_sub.to_dataframe().reset_index()
    df_mask_sub_nona = df_mask_sub.dropna(axis=0, how='any')
    dsfin = dsfin.assign_coords(lon=np.unique(df_mask_sub_nona.lon))
    dsfin = dsfin.assign_coords(lat=np.unique(df_mask_sub_nona.lat))
    dsfin2 = xr.merge([dsfin, ds_mask_sub], join='outer', compat='override')
    dsfin2 = dsfin2.drop_vars('Band1')
    o = os.path.join(e, 'stics' + '_' + str(l) + '.nc')
    dsfin2.to_netcdf(o)

print('merge netcdf...')
ncs = glob(os.path.join(input_dir, '*', 'stics_*.nc'))
ofin = os.path.join(output_dir, 'stics.nc')
ncfin = xr.open_mfdataset(ncs, parallel=True)
ncfin.load().to_netcdf(ofin)

print("DONE!")


