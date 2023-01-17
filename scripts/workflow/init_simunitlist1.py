#!/usr/bin/env python

import os
import sqlite3
import argparse
import sys
import traceback


def main():
    try:
        print("init_simunitlist.py")
        # work_dir = os.getcwd()
        work_dir = '/work'
        parser = argparse.ArgumentParser(description='load soil data into database')
        parser.add_argument('-i', '--index', help="Specify the index of the sub virtual experience")
        parser.add_argument('--option', nargs="*",type=int,  help="Specify the index of the sub virtual experience")
        args = parser.parse_args()
        i = args.index
        o = args.option
        EXPS_DIR = os.path.join(work_dir, 'EXPS')
        EXP_DIR = os.path.join(EXPS_DIR, 'exp_' + str(i))
        DB_MI = os.path.join(EXP_DIR, 'MasterInput.db')
        DB_Celsius = os.path.join(EXP_DIR, 'CelsiusV3nov17_dataArise.db')    

        with sqlite3.connect(DB_Celsius, timeout=15) as c:
            cur = c.cursor()
            cur.execute(f'update OptionsModel set ActiveWstress={o[0]},ActiveNstress={o[1]}, ActivePstress={o[2]}, ActiveKstress={o[3]}, CyberST={o[4]}  where idCodModel=1')
            c.commit()         
        
        sql_as_string = ''
        with open(os.path.join(work_dir, 'scripts', 'db', 'init_simunitlist.sql')) as f:
            sql_as_string = f.read()

        with sqlite3.connect(DB_MI, timeout=15) as conn:
            cur = conn.cursor()
            cur.executescript(sql_as_string)
            cur.executescript(f"UPDATE CropManagement set SowingDate={o[5]}")
            cur.execute(f'update SimulationOptions set StressW_YN={o[0]},StressN_YN={o[1]}, StressP_YN={o[2]}, StressK_YN={o[3]}  where idOptions=1')
            conn.commit()
    except:
        print("Unexpected error have been catched:", sys.exc_info()[0])
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()