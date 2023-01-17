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
        parser.add_argument('--option', nargs="*",  help="Specify the index of the sub virtual experience")
        args = parser.parse_args()
        i = args.index
        o = args.option
        EXPS_DIR = os.path.join(work_dir, 'EXPS')
        EXP_DIR = os.path.join(EXPS_DIR, 'exp_' + str(i))
        DB_MI = os.path.join(EXP_DIR, 'MasterInput.db')
     
        idCultivar = o[0]  
        sdens = o[1]
        OFertiPolicyCode = o[2]
        InoFertiPolicyCode = o[3]
        IrrigationPolicyCode = o[4]
        SoilTillPolicyCode = o[5]        

        with sqlite3.connect(DB_MI, timeout = 10) as conn:
            cur = conn.cursor()
            df = pd.read_sql('SELECT * FROM SummaryOutput', conn)
            df2 = pd.DataFrame()
            df2["idMangt"] = df.loc[df["Model"]=="Celsius", "Idsim"]
            id_ = df2["idMangt"]
            df2["Idcultivar"] = str(idCultivar)
            df2["sowingdate"] =  df.loc[df["Model"]=="Celsius", "Planting"]
            df2["sdens"] = int(sdens)
            df2["OFertiPolicyCode"] = str(OFertiPolicyCode)
            df2["InoFertiPolicyCode"] = str(InoFertiPolicyCode)
            df2["IrrigationPolicyCode"] = str(IrrigationPolicyCode)
            df2["SoilTillPolicyCode"] = str(SoilTillPolicyCode)
            df2.to_sql("CropManagement", conn, if_exists='replace', index=False)
            cur.executescript(f"update SimUnitList set idMangt=idsim;")
            conn.commit()
    except:
        print("Unexpected error have been catched:", sys.exc_info()[0])
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()