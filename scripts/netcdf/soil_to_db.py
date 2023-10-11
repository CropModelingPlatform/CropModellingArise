#!/usr/bin/env python

import os
import xarray as xr
import sqlite3
from glob import glob
import numpy as np
import argparse
import sys
import traceback


def main():
    try:
        print("soil_to_db.py")
        # work_dir = os.getcwd()
        work_dir = '/work'
        data_dir = '/inputData'

        parser = argparse.ArgumentParser(description='load soil data into database')
        parser.add_argument('-i', '--index', help="Specify the index of the sub virtual experience")
        parser.add_argument('--soilTexture', help="soil texture")
        args = parser.parse_args()
        i = args.index
        soilTexture = args.soilTexture
        
        EXPS_DIR = os.path.join(work_dir, 'EXPS')
        EXP_DIR = os.path.join(EXPS_DIR, 'exp_' + str(i))
        DB_MI = os.path.join(EXP_DIR, 'MasterInput.db')

        ds_mask = xr.open_dataset(glob(os.path.join(data_dir, 'land', '*.nc'))[0])
        print(ds_mask)
        ds_mask = ds_mask.reindex({'lat': sorted(ds_mask.lat)})
        df_mask = ds_mask.to_dataframe().dropna(axis=0, how="any")
        df_mask = df_mask.reorder_levels(['lat', 'lon'])
        df_mask = df_mask.sort_index(level='lat')

        df_mask = df_mask.reset_index()
        df_mask = df_mask.astype(np.float64).round(4)
        df_mask.columns = ['lat', 'lon', 'mask']
        df_mask = df_mask.set_index(['lat', 'lon'])
        print(df_mask.head(10))

        SOIL_DIR = os.path.join(data_dir, 'soil')
        ncs = glob(os.path.join(SOIL_DIR, '*.nc'))
        ds = xr.open_mfdataset(ncs, cache=False)
        print(ds)
        ds = ds.reindex({'lat': sorted(ds.lat)})
        ds.coords['mask'] = (('lat', 'lon'), ds_mask.mask.to_masked_array(copy=True))
        # ds = ds.where(ds.mask == 1)
        df = ds.to_dataframe().dropna(axis=0, how="any")
        print(df.head(5))
        df = df.reset_index()
        df = df.astype(np.float64).round(4)
        df = df.round({'SoilTotalDepth':1, 'SoilRDepth':1, 'Wwp':1, 'Wfc':1, 'bd':1, 'OrganicNStock': 3, 'pH': 1, 'OrganicC':2, 'cf':1})
        with sqlite3.connect(DB_MI) as conn:
            df.to_sql('SoilTemp', conn, if_exists='replace', index=False)


        sql_as_string  = """INSERT INTO Soil
                            SELECT SoilTemp.lat || '_' || SoilTemp.lon as IdSoil ,
                                   'simple' as SoilOption,
                                    ? as SoilTextureType,
                                    SoilTemp.SoilRDepth,
                                    SoilTemp.SoilTotalDepth,
                                    SoilTemp.OrganicNstock,
                                    null as Slope,
                                    1 as RunoffType,
                                    SoilTemp.Wwp,
                                    SoilTemp.Wfc,
                                    SoilTemp.bd,
                                    '0.3' as albedo,
                                    SoilTemp.pH,
                                    SoilTemp.OrganicC,
                                    SoilTemp.cf
                            FROM SoilTemp
                        """
        """sql_as_string = ""
        with open(os.path.join(work_dir, "scripts", "db", "init_soil.sql")) as f:
            sql_as_string = f.read()"""
        # print(sql_as_string)

        with sqlite3.connect(DB_MI) as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM Soil;")
            cur.execute(sql_as_string, (soilTexture,))
            conn.commit()
            cur.executescript("DROP TABLE SoilTemp;")
            conn.commit()
    except:
        print("Unexpected error have been catched:", sys.exc_info()[0])
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
