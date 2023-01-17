#!/usr/bin/env python

import os
import sqlite3
from glob import glob
import xarray as xr
import pandas as pd
import numpy as np
import time
from joblib import Parallel, delayed
from datetime import datetime
import subprocess

print("start")

THREADS = 20

#  netcdf TNZ_chirps-v2.0.1981-2019.days_p05_2000-2001 {
#  dimensions:
#       time = UNLIMITED ; // (731 currently)
nlon = 1440
nlat = 1344

lon_start = 0
lon_end = nlon
lon_step = 100

work_dir = '/work'
#work_dir = '.'
os.chdir(work_dir)
print('work_dir : ' + work_dir)

mask_file = os.path.join(work_dir, 'ANNUAL_AREA_HARVESTED_IRC_CROP2_HA_mask.nc')
input_file = os.path.join(work_dir, 'TNZ_PCGLOB_330', 'satDegTotal_dailyTot_output_330.nc')
output_dir = os.path.join(work_dir, 'SIM2010CPL')

ds_mask = xr.load_dataset(mask_file)
ds_w = xr.load_dataset(input_file)
ds_w = ds_w.fillna(0)
ds_w = ds_w.assign_coords(mask=(('lat', 'lon'), ds_mask.Band1.to_masked_array(copy=False)))
ds_w = ds_w.where(ds_w.mask == 1)
ds_w = ds_w.drop('mask')

# idIni;WStockinit;Ninit;TypMulchI;QmulchI;TypeResI;QResI
# 1    ;0.0       ;  0.0;        1;   0.0;        1;0.0
print('compute ids...')
ids = np.array([str(round(lo, 4)) + '_' + str(round(la, 4)) for la in np.array(ds_w.lat.to_series())
                for lo in np.array(ds_w.lon.to_series())]).reshape(nlat, nlon)
print('ids computed!')
ds_w = ds_w.assign(idIni=(('time', 'lat', 'lon'), np.broadcast_to(ids, (1, nlat, nlon))))
ds_w = ds_w.rename_vars({'soil_saturation_degree_for_the_entire_soil_layers': 'WStockinit'})
ds_w = ds_w.assign(Ninit=(('time', 'lat', 'lon'), np.broadcast_to(np.array([float(0.0)]), (1, nlat, nlon))))
ds_w = ds_w.assign(TypMulchI=(('time', 'lat', 'lon'), np.broadcast_to(np.array([int(1)]), (1, nlat, nlon))))
ds_w = ds_w.assign(QmulchI=(('time', 'lat', 'lon'), np.broadcast_to(np.array([float(0.0)]), (1, nlat, nlon))))
ds_w = ds_w.assign(TypeResI=(('time', 'lat', 'lon'), np.broadcast_to(np.array([int(1)]), (1, nlat, nlon))))
ds_w = ds_w.assign(QResI=(('time', 'lat', 'lon'), np.broadcast_to(np.array([float(0.0)]), (1, nlat, nlon))))

# ds_w = ds_w.assign(QResI=(('time', 'lat', 'lon'), np.broadcast_to(np.array([float(0.0)]), (1, nlat, nlon))))


def water_to_db_sub(lo):
    print("water_to_db_sub")
    outdir = os.path.join(output_dir, 'exp_' + str(lo))
    print("-> exp : " + str(outdir))
    db = 'MasterInput.db'
    dbname = os.path.join(outdir, db)
    df = ds_w.isel(lon=slice(lo, lo+lon_step)).to_dataframe()
    df = df.dropna(how='any', axis=0).reset_index()
    df = df[['idIni', 'WStockinit', 'Ninit', 'TypMulchI', 'QmulchI', 'TypeResI', 'QResI']]
    print('len : ' + str(len(df)))
    if os.path.exists(dbname):
        with sqlite3.connect(dbname) as c:
            cur = c.cursor()
            cur.execute('''delete from InitialConditions''')
            c.commit()
            df.to_sql('InitialConditions', c, if_exists='append', index=False)
            c.commit()
            cur.execute('''update SimUnitList set StartDay=\
                (select sowingdate from CropManagement where idMangt='S19C1OF0IF0')''')
            cur.execute('''update SimUnitList set idIni=idPoint''')
            c.commit()
    else:
        print("db not found : " + str(dbname))
    return 0

print("load into db")
res = Parallel(n_jobs=THREADS, verbose=100, max_nbytes=None)(
    delayed(water_to_db_sub)(lo) for lo in range(lon_start, lon_end, lon_step))

# exps = glob(os.path.join(output_dir, 'exp_*'))
# # for e in exps:
# #     print(str(e))
# #     create_simunitlist_sub(e, sql_as_string)
# res = Parallel(n_jobs=THREADS, verbose=100, max_nbytes=None, prefer="processes")(
#         delayed(create_simunitlist_sub)(e, sql_as_string) for e in exps)
print("res : " + str(res))

