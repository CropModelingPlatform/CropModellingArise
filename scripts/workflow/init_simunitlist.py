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
        #parser.add_argument('--option', nargs="*",type=int,  help="Specify the index of the sub virtual experience")
        args = parser.parse_args()
        i = args.index
        #o = args.option
        EXPS_DIR = os.path.join(work_dir, 'EXPS')
        EXP_DIR = os.path.join(EXPS_DIR, 'exp_' + str(i))
        DB_MI = os.path.join(EXP_DIR, 'MasterInput.db')
        DB_Celsius = os.path.join(EXP_DIR, 'CelsiusV3nov17_dataArise.db')
            
        init_sql = """DELETE FROM Coordinate_years;
        INSERT INTO Coordinate_years
        SELECT distinct idPoint,year
        FROM RAClimateD;"""

        sql_as_string = """INSERT INTO SimUnitList ( idOption, idPoint, idMangt, IdSoil, StartYear, StartDay, EndYear, EndDay, idIni, idsim )
        SELECT DISTINCT SimulationOptions.IdOptions, Coordinate_years.idPoint, CropManagement.idMangt, Soil.IdSoil, Coordinate_years.Year as StartYear, 100 AS StartDay, Coordinate_years.Year as EndYeary,360 as EndDay, 1 as IdIni, Coordinate_years.idpoint || '_' || Coordinate_years.year || '_' || CropManagement.idMangt || '_' || SimulationOptions.IdOptions AS ids
        FROM CropManagement, SimulationOptions, Soil INNER JOIN (Coordinate_years INNER JOIN RAClimateD ON Coordinate_years.idPoint = RAClimateD.idPoint) ON Soil.IdSoil = RAClimateD.idPoint
        where CropManagement.idMangt='Fert160' ORDER BY  Coordinate_years.idPoint, CropManagement.idMangt, Soil.IdSoil, Coordinate_years.year, SimulationOptions.IdOptions;"""
	
        #where CropManagement.idMangt='Fert80'and SimulationOptions.IdOptions=1

        with sqlite3.connect(DB_MI) as conn:
            cur = conn.cursor()
            cur.executescript(init_sql)
            cur.executescript("DELETE FROM SimUnitList")
            cur.executescript(sql_as_string)
            #cur.executescript(f"UPDATE CropManagement set SowingDate={o[5]}")
            conn.commit()
    except:
        print("Unexpected error have been catched:", sys.exc_info()[0])
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()