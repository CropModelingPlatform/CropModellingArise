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


THREADS = 46

def get_lon(d):
    res_=d.split("_")
    lon_=float(res_[1])
    return lon_

def get_lat(d):
    res_=d.split("_")
    lat_=float(res_[0])
    return lat_

def get_time(d):
    res_=d.split("_")
    year_ = int(float(res_[2]))
    return year_ 
    


def main():
    try:
        print("summary_output.py")
        work_dir = '/work'
        parser = argparse.ArgumentParser(description='load')
        parser.add_argument('-i', '--index', help="Specify the index of the sub virtual experience")
        args = parser.parse_args()
        i = args.index
        EXPS_DIR = os.path.join(work_dir, 'EXPS')
        EXP_DIR = os.path.join(EXPS_DIR, 'exp_' + str(i))
        db_mi = 'MasterInput.db'
        db_celsius = 'CelsiusV3nov17_dataArise.db' 
        dbname_mi = os.path.join(EXP_DIR, db_mi)
        dbname_celsius = os.path.join(EXP_DIR, db_celsius)
        print('EXP_DIR : ' + EXP_DIR)
        sqlite_connection_mi = sqlite3.connect(dbname_mi)
        sqlite_connection_celsius = sqlite3.connect(dbname_celsius)
        df = pd.read_sql('SELECT * FROM OutputSynt', sqlite_connection_celsius)
        sqlite_connection_celsius.close()
        df = df.reset_index().rename(columns={"idsim":"Idsim","iplt":"Planting","JulPheno1_1":"Emergence","JulPheno1_4":"Ant","JulPheno1_6":"Mat","Biom(nrec)":"Biom_ma","Grain(nrec)":"Yield","LAI":"MaxLai","SigmaSimEsol":"CumE","Ngrain":"GNumber","stockNsol":"SoilN","SigmaCultEsol":"Transp"})
        df["Model"] = "Celsius" 
        df["Texte"] = "" 
        df['time'] = df.apply(lambda x: get_time(x['Idsim']), axis=1)    
        df['lon'] = df.apply(lambda x: get_lon(x['Idsim']), axis=1)
        df['lat'] = df.apply(lambda x: get_lat(x['Idsim']), axis=1)
        """df["lon"] = Parallel(n_jobs=-1)(
            delayed(get_lon)(f) for f in df["Idsim"])
        df["lat"] = Parallel(n_jobs=-1)(
            delayed(get_lat)(f) for f in df["Idsim"])
        df["time"] = Parallel(n_jobs=-1)(
            delayed(get_time)(f) for f in df["Idsim"])"""
        
        v = list(set(["_".join(u.split("_")[3:]) for u in df["Idsim"]]))
        
        def create_netcdf(id_, df):
            df_2 = df[df["Idsim"].str.endswith(id_)]

            dsfin = df_2[["time", "lat", "lon", "Planting", "Emergence", "Ant", "Mat",
                                "Biom_ma", "Yield", "GNumber", "MaxLai", "SoilN", "CumE", "Transp"]]
            dsfin = dsfin.reset_index().set_index(
                        ['time', 'lat', 'lon']).to_xarray()
            o = os.path.join(EXP_DIR, 'celsius' + '_yearly_' + id_ + "_" + str(i) + '.nc')
            dsfin.to_netcdf(o)
        
        Parallel(n_jobs=-1)(
            delayed(create_netcdf)(f, df) for f in v)
            
        df = df[["Model","Idsim","Texte","Planting","Emergence","Ant","Mat","Biom_ma","Yield","GNumber","MaxLai","SoilN","CumE","Transp"]]
        with sqlite3.connect(dbname_mi, timeout=10) as c:
            cur = c.cursor()
            cur.executescript("Delete from SummaryOutput;")
            c.commit()
            df.to_sql('SummaryOutput', c, if_exists='replace', index=False)
            c.commit()


    except:
        print("Unexpected error have been catched:", sys.exc_info()[0])
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
