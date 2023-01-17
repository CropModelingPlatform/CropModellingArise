#!/usr/bin/env python

import os
import sqlite3
from glob import glob
import xarray as xr
import pandas as pd
import numpy as np
# import dask
import numba
# from numba import jit
import time
# from dask.distributed import Client
# import multiprocessing
from joblib import Parallel, delayed
from datetime import datetime
import subprocess
import argparse
import sys
import traceback

work_dir = os.getcwd()

MASK_FILE = os.path.join(
    work_dir, 'ANNUAL_AREA_HARVESTED_IRC_CROP2_HA_mask.nc')
DEM_INPUT_DIR = os.path.join(work_dir, 'TNZ_srtm_gridded')
CLIM_INPUT_DIR = os.path.join(work_dir, 'TNZ_2010_to_2011')
OUTPUT_DIR = os.path.join(work_dir, 'SIM2010')
db_master_input = os.path.join(work_dir, 'db', 'NEW', 'MasterInput.db')
THREADS = 2
NODES = 1
VERBOSE = True
CLEAN_OUTPUT = True
CLEAN_DB = True
LOAD_CLIM = True
LOAD_CSV = True
LOAD_DEM = True
CREATE_SIMS = True

#  netcdf TNZ_chirps-v2.0.1981-2019.days_p05_2000-2001 {
#  dimensions:
#       time = UNLIMITED ; // (731 currently)
nlon = 0
nlat = 0
nt = 0

t_start = 0
t_step = nt
t_end = nt
#t_end = 1*t_step
lon_start = 0
lon_step = 10
lon_end = 1*lon_step
# lon_end = nlon

vars2rename = {'ssr': 'ssr', 't2m': 't2m', 'd2m': 'd2m'}
vars2convert = {
    'ssr': '/1000000',
    't2m': '-273.15',
    'd2m': '-273.15',
    # 'precip': '*1000'
}

vars2cols = {
    'idPoint': 'idPoint',
    'time': 'w_date',
    'year': 'year',
    'DOY': 'DOY',
    'Nmonth': 'Nmonth',
    'NdayM': 'NdayM',
    # 'ssrsum': 'srad',
    'ssrmean': 'srad',
    't2mmax': 'tmax',
    't2mmin': 'tmin',
    't2mmean': 'tmoy',
    'precip': 'rain',
    'ws2m': 'wind',
    'rhum': 'rhum',
    'Etppm': 'Etppm',
    'd2mmin': 'Tdewmin',
    'd2mmax': 'Tdewmax',
    'sp': 'Surfpress',
}
# cols = list(vars2cols.keys())
# cols_renamed = list(vars2cols.values())


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


def get_date():
    now = datetime.now()
    return now.strftime("%Y-%m-%d")


def get_time():
    now = datetime.now()
    return now.strftime("%Y-%m-%d_%H:%M:%S")


def log(txt):
    if VERBOSE:
        print(get_time() + "  " + txt)


def format_df_row(l):
    cols = (
        l.time.year,
        l.time.month,
        l.time.day,
        l.time.dayofyear,
        l.time.strftime('%Y-%m-%d'),
        str(l.lon) + '_' + str(l.lat),
        '',
        ''
    )
    return cols


def format_df2(df):
    log("format_df2")
    res = df.apply(lambda l: format_df_row(l), axis=1)
    print(res)
    return res


def format_ds_fun(r):
    print(r)
    return format_df_row(r)


def format_df_dem(df):
    log('format_df_dem')
    log("idPoint")
    df['idPoint'] = df.apply(lambda l: str(
        round(l.lon, 4)) + '_' + str(round(l.lat, 4)), axis=1)

    log("codeSWstation")
    df['codeSWstation'] = ''

    log("startRain")
    df['startRain'] = ''

    log("EndRain")
    df['EndRain'] = ''

    df = df[['Band1', 'lat', 'lon', 'codeSWstation',
             'idPoint', 'startRain', 'EndRain']]
    df.columns = ['altitude', 'latitudeDD', 'longitudeDD',
                  'codeSWstation', 'idPoint', 'startRain', 'EndRain']

    return df


def format_df_clim(df):
    log('format_df_clim')
    # print(df)
    log("year")
    df['year'] = df.time.apply(lambda l: l.year)

    log("Nmonth")
    df['Nmonth'] = df.apply(lambda l: l.time.month, axis=1)

    log("NdayM")
    df['NdayM'] = df.apply(lambda l: l.time.day, axis=1)

    log("DOY")
    df['DOY'] = df.apply(lambda l: l.time.dayofyear, axis=1)

    log("time")
    df['time'] = df.apply(lambda l: l.time.strftime('%Y-%m-%d'), axis=1)

    log("idPoint")
    df['idPoint'] = df.apply(lambda l: str(
        round(l.lon, 4)) + '_' + str(round(l.lat, 4)), axis=1)

    log("rhum")
    df['rhum'] = ''

    log("Etppm")
    df['Etppm'] = ''

    log("df.reset_index")
    df = df.reset_index()
    df = df[list(vars2cols.keys())]
    df.columns = list(vars2cols.values())
    return df


# def format_df_clim(df):


def load_dem(ncdir):
    log("load_dem : " + ncdir)
    res = None
    files = glob(os.path.join(ncdir, '*.nc'))

    for f in files:
        print('file : ' + f)
        dst = xr.load_dataset(f)

        if not res:
            print('copy')
            res = dst
        else:
            print('merge')
            res = res.combine_first(dst)
    return res


def load_clim(ncdir):
    log("load_clim : " + ncdir)
    res = None
    files = glob(os.path.join(ncdir, '*.nc'))

    for f in files:
        print('file : ' + f)
        dst = xr.open_dataset(f, chunks={'time': t_step, 'lon': lon_step})
        # dst = xr.open_dataset(f, chunks={'lon': 1})
        try:
            dst = dst.drop_vars("time_bnds")
            print("drop dim time_bnds")
        except Exception as e:
            print("no time_bnds")

        v = str(list(dst.data_vars.keys())[0])
        # var = spl[-3]
        print("v : " + v)
        if v in vars2convert.keys():
            cmd = 'dst' + vars2convert[v]
            print("convert : " + cmd)
            dst = eval(cmd)

        if v in vars2rename.keys():
            spl = f.split('_')
            suf = str(spl[-5]).lower()
            if suf.find('-') != -1:
                v_new = suf.replace('-', '')
            else:
                v_new = vars2rename[v] + suf
            print("rename var '" + v + "' to '" + v_new + "'")
            dst = dst.rename_vars({vars2rename[v]: v_new})

        # print(dst)
        if not res:
            print('copy')
            res = dst
        else:
            print('merge')
            res = xr.merge([res, dst])
    return res


def dem_to_db(dataset):
    # for i in range(0, 2, 1):
    for i in range(lon_start, lon_end, lon_step):
        print("-> lon : " + str(i))

        outdir = os.path.join(OUTPUT_DIR, 'exp_' + str(i))
        os.makedirs(outdir, exist_ok=True)

        # db = 'MasterInput_' + str(i) + '.db'
        db = 'MasterInput.db'
        dbname = os.path.join(outdir, db)

        print("isel")
        ds = dataset.isel(lon=slice(i, i + lon_step))

        log("to_dataframe")
        df = ds.to_dataframe()

        log("reset_index")
        df = df.reset_index()

        print("dropna")
        df = df.dropna(axis=0, how='any')

        print("format_df")
        df = format_df_dem(df)
        # res = xr.apply_ufunc(format_ds_fun, ds, [ds.time, ds.lat, ds.lon], dask='allowed', vectorize=True)
        # res
        # print(res)
#         print("to_csv")
#         csv_file = str(os.path.join(outdir, 'coordinates.csv'))
#         df.to_csv(csv_file, index=False)

        print("to_db")
        with sqlite3.connect(dbname) as c:
            df.to_sql('Coordinates', c, if_exists='append', index=False)

    return 0


@timerfunc
def clim_to_csv_sub(t, i, pds, outdir):
    log("clim_to_csv_sub -> t : " + str(t))
    # print(ds_clim)

    #print('isel lon')
    #ds = ds_clim.isel(lon=slice(i, i + lon_step))

    # log("isel time")
    ds = pds.isel(time=slice(t, t + t_step))

    # print("ds dropna")
    # ds = ds.dropna('time', how='all')

    log("to_dataframe")
    df = ds.to_dataframe()
    # df = ds.to_dask_dataframe()

    # log("reset_index")
    df = df.reset_index()

    # log("df dropna")
    df = df.dropna(axis=0, how='any')
    # df = df.dropna(how='any')

    if df.empty:
        log("empty df")
    else:
        # log("not empty df")
        # log("format_df")
        df = format_df_clim(df)
        # res = xr.apply_ufunc(format_ds_fun, ds, [ds.time, ds.lat, ds.lon], dask='allowed', vectorize=True)
        # res
        # print(res)
        # log("to_csv")
        # csv_file = str(os.path.join(OUTPUT_DIR, get_date() + '_raclimated_' + str(i) + '.csv'))
        csv_file = str(os.path.join(outdir, 'raclimated_' + str(t) + '.csv'))
        df.to_csv(csv_file, index=False)

    #     print("to_db")
    #     with sqlite3.connect(dbname) as c:
    #         cur = c.cursor()
    #         cur.execute("PRAGMA synchronous = OFF")
    #         # cur.execute("PRAGMA journal_mode = WAL2")
    #         df.to_sql('RAClimateD', c, if_exists='append', index=False)
    #         c.commit()
    #         cur.close()
    return 0


@timerfunc
def clim_to_csv(dataset):
    log("clim_to_csv")
    # for i in range(0, 2, 1):
    for i in range(lon_start, lon_end, lon_step):
        log("-> lon : " + str(i))

        outdir = os.path.join(OUTPUT_DIR, 'exp_' + str(i))
        os.makedirs(outdir, exist_ok=True)

        f_src = db_master_input  # os.path.join("db", "NEW", "MasterInput.db")
        # db = 'MasterInput_' + str(i) + '.db'
        db = 'MasterInput.db'
        f_dest = os.path.join(outdir, db)

        log('copy db from "' + f_src + '" to "' + f_dest + '"')
        # res = os.system('cp' + f_src + ' ' + f_dest)
        res = subprocess.check_call(['cp',  f_src, f_dest])

        log('isel lon')
        ds = dataset.isel(lon=slice(i, i + lon_step))

        log("Parallel")
        res = Parallel(n_jobs=THREADS, verbose=100, max_nbytes=None, prefer="threads")(
            delayed(clim_to_csv_sub)(t, i, ds, outdir) for t in range(t_start, t_end, t_step))
#         for t in range(0, t_end, t_step):
#             clim_to_csv_sub(t, i, dataset, outdir, f_dest)
    return 0


@timerfunc
def clim_to_db_sub(i, output_dir):
    log("clim_to_db_sub")
    log("-> lon : " + str(i))
    outdir = os.path.join(output_dir, 'exp_' + str(i))
    db = 'MasterInput.db'
    dbname = os.path.join(outdir, db)
    # with sqlite3.connect(dbname) as conn:
    # conn.isolation_level = None
    # cur = conn.cursor()
    # cur.execute("begin")
    # cur.execute("PRAGMA synchronous=OFF")
    # cur.execute("PRAGMA journal_mode=MEMORY")
    # print("commit PRAGMA")
    # cur.execute("commit")

    for t in range(t_start, t_end, t_step):
        csv_file = str(os.path.join(outdir, 'raclimated_' + str(t) + '.csv'))
        print(csv_file)
        df = pd.read_csv(csv_file)
        # df.to_csv(csv_file, index=False)

        print("to_db")
        with sqlite3.connect(dbname) as conn:
            df.to_sql('RAClimateD', conn, if_exists='append', index=False)
#         print("df.to_sql")
#         # cur.execute("begin")
#         res = df.to_sql('RAClimateD', conn, if_exists='append', index=False, method='multi')
#         print('res : ' + str(res))
        # print("commit")
        # conn.commit()


@timerfunc
def clim_to_db():
    log("clim_to_db")
    # for i in range(0, lon_end, lon_step):
    #     clim_to_db_sub(i, OUTPUT_DIR)

    res = Parallel(n_jobs=THREADS, verbose=100, max_nbytes=None, prefer="threads")(
        delayed(clim_to_db_sub)(i, OUTPUT_DIR) for i in range(lon_start, lon_end, lon_step))
    return res


def create_simunitlist_sub(e, sql):
    log("create_simunitlist_sub")
    print(e)
    with sqlite3.connect(os.path.join(e, 'MasterInput.db')) as conn:
        cur = conn.cursor()
        cur.execute("PRAGMA synchronous=OFF")
        cur.execute("PRAGMA journal_mode=MEMORY")
        cur. executescript(sql)
        conn.commit()
    return 0


def main():
    try:
        print("main()")

        # print(sys.argv[1:])
        # myopts, args = getopt.getopt(sys.argv[1:], "o:t:n:d:m:c")
        parser = argparse.ArgumentParser(
            description='Process netcdf to database')
        parser.add_argument(
            '-o', '--output', help="Specify the output directory")
        parser.add_argument(
            '-t', '--threads', help="Specify the number of cpu per node", type=int)
        parser.add_argument(
            '-n', '--nodes', help="Specify the number of nodes", type=int)
        parser.add_argument(
            '--clim', help="Specify the climate data directory")
        parser.add_argument(
            '--dem', help="Specify the digital elevation model data directory")
        parser.add_argument(
            '--mask', help="Specify the netcdf mask and grid file")
        parser.add_argument('--cleanouput', help="Delete output directory")
        parser.add_argument(
            '--cleandb', help="Delete the main database records")
        parser.add_argument(
            '--noloadclim', help="Don't load the netcdf climate files")
        parser.add_argument(
            '--noloadcsv', help="Don't load the csv climate files")
        parser.add_argument('--noloaddem', help="Don't load the dem file")
        parser.add_argument('--nosimunitlist',
                            help="Don't create the simUnitList table")
        # add_argument('integers', metavar='N', type=int, nargs='+',
        #                     help='an integer for the accumulator')
        # parser.add_argument('--sum', dest='accumulate', action='store_const',
        #                     const=sum, default=max,
        #                     help='sum the integers (default: find the max)')

        args = parser.parse_args()
        print(args)
        global MASK_FILE
        global DEM_INPUT_DIR
        global CLIM_INPUT_DIR
        global THREADS
        global NODES
        global OUTPUT_DIR
        global CLEAN_OUTPUT
        global CLEAN_DB
        global LOAD_CLIM
        global LOAD_CSV
        global LOAD_DEM
        global CREATE_SIMS
        global nlon
        global nlat
        global nt
        global lon_start
        global lon_step

        MASK_FILE = args.mask if args.mask else MASK_FILE
        DEM_INPUT_DIR = args.dem if args.dem else DEM_INPUT_DIR
        CLIM_INPUT_DIR = args.clim if args.clim else CLIM_INPUT_DIR
        THREADS = args.threads if args.threads else THREADS
        NODES = args.nodes if args.nodes else NODES
        OUTPUT_DIR = args.output if args.output else OUTPUT_DIR
        CLEAN_OUTPUT = False if args.cleanouput else CLEAN_OUTPUT
        CLEAN_DB = False if args.cleandb else CLEAN_DB
        LOAD_CLIM = False if args.noloadclim else LOAD_CLIM
        LOAD_CSV = False if args.noloadcsv else LOAD_CSV
        LOAD_DEM = False if args.noloaddem else LOAD_DEM
        CREATE_SIMS = False if args.nosimunitlist else CREATE_SIMS

        #
        #
        #     MASK_FILE
        # for o, a in myopts:
        #     print(str(o) + " : " + str(a))
        #     if o == '-dem':
        #         DEM_INPUT_DIR = a
        #     elif o == '-mask':
        #         MASK_FILE = a
        #     elif o == '-clim':
        #         CLIM_INPUT_DIR = a
        #     elif o == '-o':
        #         OUTPUT_DIR = a
        #     elif o == '-t':
        #         THREADS = a
        #     elif o == '-n':
        #         NODES = a
        #     else:
        #         print("Usage: %s -demi input -o output" % sys.argv[0])

        log("#############################################################")
        log("START")
        print('work_dir : ' + work_dir)
        print("CLIM_INPUT_DIR : " + str(CLIM_INPUT_DIR))
        print("DEM_INPUT_DIR : " + str(DEM_INPUT_DIR))
        print("MASK_FILE : " + MASK_FILE)
        print("OUTPUT_DIR : " + str(OUTPUT_DIR))
        print("NODES : " + str(NODES))
        print("THREADS : " + str(THREADS))
        print("CLEAN_OUTPUT : " + str(CLEAN_OUTPUT))
        print("CLEAN_DB : " + str(CLEAN_DB))
        print("LOAD_CLIM : " + str(LOAD_CLIM))
        print("LOAD_CSV : " + str(LOAD_CSV))
        print("LOAD_DEM : " + str(LOAD_DEM))
        print("CREATE_SIMS : " + str(CREATE_SIMS))

        print("")

        if CLEAN_OUTPUT:
            print('cleaning output dir')
            print(str(os.path.join(OUTPUT_DIR,  '*')))
            cm = subprocess.check_call(['rm', '-Rf', os.path.join(OUTPUT_DIR)])
            print(cm)

        if CLEAN_DB:
            print('cleaning db')
            try:
                with sqlite3.connect(db_master_input) as conn:
                    cur = conn.cursor()
                    cur.execute("PRAGMA synchronous=OFF")
                    cur.execute("PRAGMA journal_mode=MEMORY")
                    cur.execute("begin")
                    cur.execute("delete from Coordinates")
                    cur.execute("delete from Coordinate_years")
                    cur.execute("delete from SimUnitList")
                    cur.execute("delete from RAClimateD")
                    cur.execute("commit")
                    conn.commit()
                    # cur.execute("PRAGMA synchronous = OFF")
                    # cur.execute("PRAGMA journal_mode = MEMORY")
            except Exception as e:
                print("ERROR : " + str(e))
                exit(1)

        ####################
        # MASK
        #
        log("LOAD MASK")
        ds_mask = xr.load_dataset(MASK_FILE)
        df_mask = ds_mask.to_dataframe().dropna(how='all')
        #t_end = 1*t_step
        lon_start = 0
        lon_step = 10
        lon_end = 1*lon_step

        print(ds_mask)

        if LOAD_CLIM:
            ####################
            # CLIM
            #
            log("LOAD CLIMATE DATA")
            ds_clim = load_clim(CLIM_INPUT_DIR)

            log("ADD MASK TO CLIMATE DATA")
            ds_clim.coords['mask'] = (
                ('lat', 'lon'), ds_mask.Band1.to_masked_array(copy=False))

            print("mask")
            ds_clim = ds_clim.where(ds_clim.mask == 1)

            log("CONVERT TO DATAFRAME AND WRITE CSV FILES")
            res = clim_to_csv(ds_clim)
            print("res : " + str(res))

        if LOAD_CSV:
            log("CLIM TO DB")
            res = clim_to_db()
            print("res : " + str(res))

        if LOAD_DEM:
            ####################
            # DEM
            #
            log("LOAD DEM DATA")
            ds_dem = load_dem(DEM_INPUT_DIR)

            log("ADD MASK TO DEM DATA")
            ds_dem.coords['mask'] = (
                ('lat', 'lon'), ds_mask.Band1.to_masked_array(copy=False))
            ds_dem = ds_dem.where(ds_dem.mask == 1)

            log("CONVERT TO DATAFRAME AND LOAD INTO DB")
            res = dem_to_db(ds_dem)
            print("res: " + str(res))

        if CREATE_SIMS:
            log("CREATE SIMUNITLIST")
            sql_as_string = ''
            with open(os.path.join(work_dir, 'scripts', 'create_simunitlist.sql')) as f:
                sql_as_string = f.read()

            print(sql_as_string)
            exps = glob(os.path.join(OUTPUT_DIR, 'exp_*'))
            # for e in exps:
            #     print(str(e))
            #     create_simunitlist_sub(e, sql_as_string)
            res = Parallel(n_jobs=THREADS, verbose=100, max_nbytes=None, prefer="threads")(
                delayed(create_simunitlist_sub)(e, sql_as_string) for e in exps)
            #print("res : " + str(res))

        log("")
        log("END")
        log("#############################################################")

        return 0
    except:
        print("Unexpected error have been catched:", sys.exc_info()[0])
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
