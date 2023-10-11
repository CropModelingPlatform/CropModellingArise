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
import shutil

def main():
    try:
        print("genotype_dssat.py")
        work_dir = '/work'
        parser = argparse.ArgumentParser(description='load')
        parser.add_argument('-i', '--index', help="Specify the folder of the sub virtual experience")
        parser.add_argument('-d', '--dbmi', help="Specify the MasterInput of the sub virtual experience")
        args = parser.parse_args()
        exp_i = args.index
        dbname_mi = os.path.join(args.dbmi)
        sqlite_connection_mi = sqlite3.connect(dbname_mi)
        sq = "SELECT SimUnitList.idsim as idsim, ListCultOption.PRCROP as crop FROM (ListCultOption INNER JOIN (ListCultivars INNER JOIN CropManagement ON ListCultivars.IdCultivar = CropManagement.Idcultivar) ON ListCultOption.CodePSpecies = ListCultivars.CodePSpecies) INNER JOIN SimUnitList ON CropManagement.idMangt = SimUnitList.idMangt;"   
        df_sim = pd.read_sql(sq, sqlite_connection_mi)
        sqlite_connection_mi.close() 
        print(df_sim.head(5))
        
        def add_genotype(f):
            src_path_cul = os.path.join(work_dir, "data", "cultivars","dssat", f["crop"]+"CER047.CUL")
            src_path_eco = os.path.join(work_dir, "data", "cultivars","dssat", f["crop"]+"CER047.ECO")
            src_path_spe = os.path.join(work_dir, "data", "cultivars","dssat", f["crop"]+"CER047.SPE")
            dest_path = os.path.join(exp_i, f["idsim"])
            shutil.copy(src_path_cul, dest_path)
            shutil.copy(src_path_eco, dest_path)
            shutil.copy(src_path_spe, dest_path)
            
        Parallel(n_jobs=-1)(
            delayed(add_genotype)(f) for f in df_sim.iloc)
    except:
        print("Unexpected error have been catched:", sys.exc_info()[0])
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
