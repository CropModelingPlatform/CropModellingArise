# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 13:54:43 2022

@author: MIDINGOYI
"""

import os
import sqlite3
from glob import glob
import traceback
import argparse
import sys
import pandas as pd
from joblib import Parallel, delayed
import re


THREADS = 96

def get_coord(d):
    res = re.findall("([-]?\d+[.]\d+)[_]", d)
    lat = float(res[0])
    lon = float(res[1])
    year = int(float(res[2]))
    return {'lon': lon, 'lat': lat, 'year': year}

def remove_comma(f):
    with open(f, "r") as fil:
        cod =fil.readlines()
    if cod[-1].endswith(";\n"):
        cod[-1] = cod[-1].replace(";\n", "\n")
    with open(f, "w") as fil:
        fil.writelines(cod)
    

def create_df_summary(f):
    d_name = os.path.dirname(f).split(os.path.sep)[-1]
    remove_comma(f)
    c = get_coord(d_name)
    df = pd.read_csv(f, sep=';', skipinitialspace=True)
    df = df.reset_index().rename(columns={"iplts": "Planting","ilevs":"Emergence","iflos":"Ant","imats":"Mat","masec(n)":"Biom_ma","mafruit":"Yield","chargefruit":'GNumber',"laimax":"MaxLai","Qles":"Nleac","QNapp":"SoilN","QNplante":"CroN_ma","ces":"CumE","cep":"Transp"})
    df.insert(0, "Model", "Stics")
    df.insert(1, "Idsim", d_name)
    df.insert(2, "Texte", "")
    df['time'] = int(df['ansemis'])
    df['lon'] = c['lon']
    df['lat'] = c['lat']
    return df

def main():
    try:
        print("summary_output.py")
        work_dir = '/work'
        parser = argparse.ArgumentParser(description='load soil data into database')
        parser.add_argument('-i', '--index', help="Specify the index of the sub virtual experience")
        args = parser.parse_args()
        i = args.index
        EXPS_DIR = os.path.join(work_dir, 'EXPS')
        EXP_DIR = os.path.join(EXPS_DIR, 'exp_' + str(i))
        db = 'MasterInput.db'
        dbname = os.path.join(EXP_DIR, db)
        print('EXP_DIR : ' + EXP_DIR)
        files = glob(os.path.join(EXP_DIR, 'Stics', '*', 'mod_r*'))
        res = Parallel(n_jobs=THREADS, verbose=100, max_nbytes=None, prefer="processes")(
            delayed(create_df_summary)(f) for f in files)
        df = pd.concat(res)
        dffin = pd.concat(res)
        dffin = dffin[["time","lat","lon","Planting","Emergence","Ant","Mat","Biom_ma","Yield","GNumber","MaxLai","Nleac","SoilN","CroN_ma","CumE","Transp"]]
        df.reset_index()
        print("DONE!")
        dsfin = dffin.reset_index().set_index(['time', 'lat', 'lon']).to_xarray()
        o = os.path.join(EXP_DIR, 'stics' + '_yearly_' + str(i) + '.nc')
        dsfin.to_netcdf(o)
        df = df[["Model","Idsim","Texte","Planting","Emergence","Ant","Mat","Biom_ma","Yield","GNumber","MaxLai","Nleac","SoilN","CroN_ma","CumE","Transp"]]
        with sqlite3.connect(dbname) as c:
            cur = c.cursor()
            cur.executescript("DELETE FROM SummaryOutput WHERE Model='Stics';")
            c.commit()
            df.to_sql('SummaryOutput', c, if_exists='append', index=False)
            c.commit()

    except:
        print("Unexpected error have been catched:", sys.exc_info()[0])
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
