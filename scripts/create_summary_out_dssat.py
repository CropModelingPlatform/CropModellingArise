# -*- coding: utf-8 -*-


import os
import sqlite3
import sys
import traceback
from glob import glob
import pandas as pd
import numpy as np
from joblib import Parallel, delayed
from datetime import datetime, date
import argparse

import re

THREADS = 96


def get_coord(d):
    res = re.findall("([-]?\d+[.]\d+)[_]", d)
    lat = float(res[0])
    lon = float(res[1])
    year = int(float(res[2]))
    return {'lon': lon, 'lat': lat, 'year': year}


def transform(fil):
    with open(fil, "r") as fil_:
        FILE = fil_.readlines()
    d_name = os.path.dirname(fil).split(os.path.sep)[-1]
    c = get_coord(d_name)
    outData = FILE[4:]
    varId = FILE[3]					# Read the raw variables
    varId = list(map(str, str.split(varId[1:])[13:]))		# Only get the useful variables
    nYear = np.size(outData)
    dataArr = [list(map(float, str.split(outData[i])[13:]))
		                   for i in range(nYear)][0]   
    df = pd.DataFrame({varId[i]: [dataArr[i]] for i in range(len(varId))})
    df = df.reset_index().rename(columns={"PDAT": "Planting","EDAT":"Emergence","ADAT":"Ant","MDAT":"Mat","CWAM":"Biom_ma","HWAM":"Yield","H#AM":'GNumber',"LAIX":"MaxLai","NLCM":"Nleac","NIAM":"SoilN","CNAM":"CroN_ma","ESCP":"CumE","EPCP":"Transp"})
    df.insert(0, "Model", "Dssat")
    df.insert(1, "Idsim", d_name)
    df.insert(2, "Texte", "")

    df['lon'] = c['lon']
    df['lat'] = c['lat']
    df['time'] = int(c['year'])

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
        files = glob(os.path.join(EXP_DIR, "Dssat", '*', 'Summary.OUT'))

        res = Parallel(n_jobs=THREADS, verbose=100, max_nbytes=None, prefer="processes")(
            delayed(transform)(f) for f in files)
        df = pd.concat(res)

        df["Planting"]= df["Planting"]%1000
        df["Emergence"]= df["Emergence"]%1000
        df["Ant"]= df["Ant"]%1000
        df["Mat"]= df["Mat"]%1000
        df["Yield"] = df["Yield"].div(1000)
        df["Biom_ma"] = df["Biom_ma"].div(1000)

        v = list(set(["_".join(u.split("_")[3:]) for u in df["Idsim"]]))
        
        def create_netcdf(id_, df):
            df_2 = df[df["Idsim"].str.endswith(id_)]
            dsfin = df_2[["time","lat","lon","Planting","Emergence","Ant","Mat","Biom_ma","Yield","GNumber","MaxLai","Nleac","SoilN","CroN_ma","CumE","Transp"]]
            dsfin = dsfin.reset_index().set_index(
                        ['time', 'lat', 'lon']).to_xarray()
            o = os.path.join(EXP_DIR, 'dssat' + '_yearly_' + id_ + "_" + str(i) + '.nc')
            dsfin.to_netcdf(o)
        
        Parallel(n_jobs=THREADS, verbose=100, max_nbytes=None, prefer="processes")(
            delayed(create_netcdf)(f, df) for f in v)
        df.reset_index()
        print("DONE!")
        df = df[["Model","Idsim","Texte","Planting","Emergence","Ant","Mat","Biom_ma","Yield","GNumber","MaxLai","Nleac","SoilN","CroN_ma","CumE","Transp"]]
        with sqlite3.connect(dbname, timeout=15) as c:
            cur = c.cursor()
            cur.execute("DELETE FROM SummaryOutput WHERE Model='Dssat';")
            c.commit()
            df.to_sql('SummaryOutput', c, if_exists='append', index=False)
            c.commit()
    except:
        print("Unexpected error have been catched:", sys.exc_info()[0])
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()



