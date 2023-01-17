#!/usr/bin/env python

import os
import sqlite3
from glob import glob
import xarray as xr
import pandas as pd
import numpy as np
import time
from joblib import Parallel, delayed
from datetime import datetime, date
import subprocess
import argparse
import sys
import traceback
import re

THREADS = 7

def get_coord(d):
    res = re.findall("([-]?\d+[.]\d+)[_]", d)
    lat = float(res[0])
    lon = float(res[1])
    year = int(float(res[2]))
    return {'lon': lon, 'lat': lat, 'year': year}

def load_csv_sub(f):
    f_name = os.path.basename(f)
    d_name = os.path.dirname(f).split(os.path.sep)[-1]
    c = get_coord(d_name)
    df = pd.read_csv(f, sep=';')
    df = df.reset_index().rename(columns={"lai(n)": "lai","mafruit":"Yield", "chargefruit":'GNumber', "Qles":"Nleac","QNapp":"SoilN","QNplante":"CroN_ma","ces":"CumE","cep":"Transp"})
    df = df[['ian', 'mo', 'jo', 'lai',"Yield",'GNumber', "Nleac","SoilN","CroN_ma","CumE","Transp"]]
    df['time'] = df.apply(lambda l: datetime(int(l.ian), int(l.mo), int(l.jo)), axis=1)
    df['lon'] = c['lon']
    df['lat'] = c['lat']
    df = df.loc[:, ['time', 'lat', 'lon', 'lai',"Yield",'GNumber', "Nleac","SoilN","CroN_ma","CumE","Transp"]]
    df = df.set_index(['time', 'lat', 'lon'])
    return df

def main():
    try:
        print("stics_to_netcdf.py")
        work_dir = '/work'
        parser = argparse.ArgumentParser(description='load soil data into database')
        parser.add_argument('-i', '--index', help="Specify the index of the sub virtual experience")
        args = parser.parse_args()
        i = args.index
        
        EXPS_DIR = os.path.join(work_dir, 'EXPS')
        EXP_DIR = os.path.join(EXPS_DIR, 'exp_' + str(i))
        print('EXP_DIR : ' + EXP_DIR)
        files = glob(os.path.join(EXP_DIR, 'Stics', '*', 'mod_s*'))
        dfin = pd.DataFrame()
        res = Parallel(n_jobs=THREADS, verbose=100, max_nbytes=None, prefer="processes")(
            delayed(load_csv_sub)(f) for f in files)
        dffin = pd.concat(res)
        dsfin = dffin.reset_index().set_index(['time', 'lat', 'lon']).to_xarray()
        o = os.path.join(EXP_DIR, 'stics' + '_daily_' + str(i) + '.nc')
        dsfin.to_netcdf(o)
        print("DONE!")

    except:
        print("Unexpected error have been catched:", sys.exc_info()[0])
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()



