#!/usr/bin/env python

import os
import sqlite3
import argparse
import sys
import traceback
import pandas as pd


def main():
    try:
        print("modify_simunitlist.py")
        work_dir = '/work'
        parser = argparse.ArgumentParser(description='load')
        parser.add_argument('-i', '--index', help="Specify the index of the sub virtual experience")
        args = parser.parse_args()
        i = args.index
        EXPS_DIR = os.path.join(work_dir, 'EXPS')
        EXP_DIR = os.path.join(EXPS_DIR, 'exp_' + str(i))
        DB_MI = os.path.join(EXP_DIR, 'MasterInput.db')     

        with sqlite3.connect(DB_MI) as conn:
            cur = conn.cursor()
            df = pd.read_sql('SELECT * FROM SummaryOutput', conn)
            df2 = pd.DataFrame()
            df2["id"] = df.loc[df["Model"]=="Celsius", "IdSim"]
            df2["sowingdate"] =  df.loc[df["Model"]=="Celsius", "Planting"]
            df2.to_sql("Sowingtable", conn, if_exists='replace', index=False)
            
            df_mangt= pd.read_sql('SELECT * FROM CropManagement', conn)
            df2['idMangt'] = df2['id'].str.split('_').str[3]
            df2 = df2.merge(df_mangt[["idMangt",'Idcultivar', 'sdens',
                'OFertiPolicyCode', 'InoFertiPolicyCode', 'IrrigationPolicyCode',
                'SoilTillPolicyCode']], on='idMangt', how='left')

            df2.drop("idMangt", axis=1, inplace=True)
            df2.rename(columns={"id":"idMangt"}, inplace=True)

            df2.to_sql("CropManagement", conn, if_exists='replace', index=False)

            cur.executescript(f"update SimUnitList set idMangt=idsim;")
            conn.commit()

    except:
        print("Unexpected error have been catched:", sys.exc_info()[0])
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()