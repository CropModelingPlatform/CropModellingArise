#!/usr/bin/env python

import os
import sqlite3
from glob import glob
import xarray as xr
import pandas as pd
import time


def timerfunc(func):
    """
    A timer decorator
    """
    def function_timer(*args, **kwargs):
        """
        A nested function for timing other functions
        """
        start = time.time()
        value = func(*args, **kwargs)
        end = time.time()
        runtime = end - start
        msg = "The runtime for {func} took {time} seconds to complete"
        print(msg.format(func=func.__name__,
                         time=runtime))
        return value
    return function_timer


@timerfunc
def to_csv_cdo(f_in, bbox_str, f_out):
    print('to_csv_cdo')
    exe = 'cdo -P ' + str(THREADS_CDO) \
        + ' -outputtab,name,lon,lat,date,value' \
        + ' -setmissval,NaN' \
        + ' -div ' \
        + ' -sellonlatbox,' + bbox_str \
        + ' ' + f_in \
        + ' -sellonlatbox,' + bbox_str \
        + ' ' + MASK_FILE \
        + ' | awk -F " " \'$5 != "nan"{print $1,$2,$3,$4,$5}\'' \
        + ' > ' + f_out
    exe = 'cdo -P ' + str(THREADS_CDO) \
        + ' -outputtab,name,lon,lat,date,value' \
        + ' -setmissval,NaN' \
        + ' -sellonlatbox,' + bbox_str \
        + ' ' + f_in \
        + ' | awk -F " " \'$5 != "nan"{print $1,$2,$3,$4,$5}\'' \
        + ' > ' + f_out
    print(exe)
    res = os.system(exe)
    print("res : " + str(res))


@timerfunc
def to_csv_xr(ds, bbox, f_out):
    print('to_csv_xr')
    dst = ds.sel(lon=slice(bbox[0], bbox[1]), lat=slice(bbox[1], bbox[2]), drop=False)
    #dst = ds.loc([slice(exp, exp+sp_size)])
    dst.to_dataframe().reset_index().dropna(axis=0, how='any').to_csv(f_out, index=False)


work_dir = '/media/guyomji/DATA_ON_MX500/Documents/data'
#work_dir = '/media/guyomji/DATA_ON_MX500/Documents/backup'
#work_dir = '/work'
#MASK_FILE = os.path.join(work_dir, 'ANNUAL_AREA_HARVESTED_IRC_CROP2_HA_mask.nc')
MASK_FILE = os.path.join(work_dir, 'mask_IRC.nc')
CLIM_INPUT_DIR = os.path.join(work_dir, 'TNZ_2010_to_2011/')
#CLIM_INPUT_DIR = os.path.join(work_dir, 'TNZ2010/')
OUTPUT_DIR = os.path.join(work_dir, 'TNZ2010TEST')
THREADS = 1
THREADS_CDO = 3
ds_mask = xr.load_dataset(MASK_FILE)
df_mask = ds_mask.where(ds_mask.Band1 == 1).to_dataframe().reset_index() #.dropna(axis=0, how='any')
N_SIMS = len(df_mask)
N_LAT = len(ds_mask.lat.to_series())
N_LON = len(ds_mask.lon.to_series())
print("number of simulations : " + str(N_SIMS))
print("grid : " + str(N_LAT) + " x " + str(N_LON))
csv_size = 50000
sp_size = 10
t_size = int(round(csv_size/1000))
sp_end = len(df_mask) # sp_size * 10  # len(df_mask)
t_end = t_size * 2  # 730
files = glob(os.path.join(CLIM_INPUT_DIR, '*.nc'))
for i in range(0, 1, 1):
    N = 0
    f_in = files[i]
    print("processing " + str(f_in))
    with xr.open_dataset(f_in, chunks={'lat': sp_size, 'lon': sp_size}) as ds:
        for exp in range(0, sp_end, sp_size):
            print("sim : " + str(N) + ", from " + str(exp) + " to " + str(exp+sp_size))
            sel = df_mask.iloc[slice(exp, exp+sp_size)]
            bbox = [min(sel.lon), max(sel.lon), min(sel.lat), max(sel.lat)]
            bbox_str = str(bbox).replace('[', '').replace(']', '').replace(' ', '')
            print("bbox : " + str(bbox))
            
            # for t in range(0, t_end, t_size):
            #     print("t from " + str(t) + " to " + str(t + t_size))
            
            #to_csv_cdo(f_in, bbox_str, f_in + '_CDO_' + str(N) + '.csv')
            to_csv_xr(ds, bbox, f_in + '_XR_' + str(N) + '.csv')
            N += 1











