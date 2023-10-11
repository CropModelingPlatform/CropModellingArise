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
        #parser.add_argument('-i', '--index', help="Specify the index of the sub virtual experience")
        #parser.add_argument('--option', nargs="*",type=int,  help="Specify the simulation option")

        parser.add_argument("--index", type=int, help="Index value")
        parser.add_argument("--startdate", type=int, help="Start date")
        parser.add_argument("--enddate", type=int, help="End date")
        parser.add_argument("--cropvariety", nargs="+", help="Crop variety")
        parser.add_argument("--option", nargs="+", type=int, help="Simulation option") 
        parser.add_argument("--ferti", nargs="+", help="fertilizer option") 
        parser.add_argument("--sowingoption", type=int, help="sowing option")

        

        #parser.add_argument('--option', nargs="*",type=int,  help="Specify the index of the sub virtual experience")
        args = parser.parse_args()
        
        i = args.index
        startd = args.startdate
        endd = args.enddate
        variety = args.cropvariety
        simoption = args.option
        fertioption = args.ferti
        sd = args.sowingoption
        print(fertioption)
        print(simoption)
        print(variety)
        
        #o = args.option
        EXPS_DIR = os.path.join(work_dir, 'EXPS')
        EXP_DIR = os.path.join(EXPS_DIR, 'exp_' + str(i))
        DB_MI = os.path.join(EXP_DIR, 'MasterInput.db')
        DB_Celsius = os.path.join(EXP_DIR, 'CelsiusV3nov17_dataArise.db')
        
        if sd==1:
            with sqlite3.connect(DB_Celsius, timeout=15) as c:
                cur = c.cursor()
                cur.execute(f'update OptionsModel set CyberST=1')
                c.commit()  
            
        init_sql = """DELETE FROM Coordinate_years;
        INSERT INTO Coordinate_years
        SELECT distinct idPoint,year
        FROM RAClimateD;"""

        sql_as_string = """INSERT INTO SimUnitList ( idOption, idPoint, idMangt, IdSoil, StartYear, StartDay, EndYear, EndDay, idIni, idsim )
        SELECT DISTINCT SimulationOptions.IdOptions, Coordinate_years.idPoint, CropManagement.idMangt, Soil.IdSoil, Coordinate_years.Year as StartYear, ? AS StartDay, Coordinate_years.Year as EndYear,? as EndDay, 1 as IdIni, Coordinate_years.idpoint || '_' || Coordinate_years.year || '_' || CropManagement.idMangt || '_' || SimulationOptions.IdOptions AS ids
        FROM CropManagement, SimulationOptions, Soil INNER JOIN (Coordinate_years INNER JOIN RAClimateD ON Coordinate_years.idPoint = RAClimateD.idPoint) ON Soil.IdSoil = RAClimateD.idPoint
        ORDER BY  Coordinate_years.idPoint, CropManagement.idMangt, Soil.IdSoil, Coordinate_years.year, SimulationOptions.IdOptions;"""
	
        with sqlite3.connect(DB_MI) as conn:
            cur = conn.cursor()
            
            # Create a temporary table to hold the idcultivar values
            cur.execute('CREATE TEMPORARY TABLE temp_varcult (idcultivar TEXT)')
            # Create a temporary table to hold the fertilizer values
            cur.execute('CREATE TEMPORARY TABLE temp_ferti (idferti TEXT)')
            # Create a temporary table to hold the simulation options
            cur.execute('CREATE TEMPORARY TABLE temp_simoption (idoption TEXT)')
            for idcultivar in variety:
                cur.execute('INSERT INTO temp_varcult (idcultivar) VALUES (?)', (idcultivar,))
            for idferti in fertioption:
                cur.execute('INSERT INTO temp_ferti (idferti) VALUES (?)', (idferti,))
            for idoption in simoption:
                cur.execute('INSERT INTO temp_simoption (idoption) VALUES (?)', (idoption,))

            # Modify the Cropmanagement table by keeping only the desired rows
            cur.execute('DELETE FROM CropManagement WHERE Idcultivar NOT IN (SELECT idcultivar FROM temp_varcult) OR InoFertiPolicyCode NOT IN (SELECT idferti FROM temp_ferti) ')

            cur.executescript(init_sql)
            cur.executescript("DELETE FROM SimUnitList")
            cur.execute(sql_as_string, (startd, endd, ))
            cur.execute('DELETE FROM SimUnitList WHERE idOption NOT IN (SELECT idoption FROM temp_simoption)')

            #cur.executescript(f"UPDATE CropManagement set SowingDate={o[5]}")
            conn.commit()
    except:
        print("Unexpected error have been catched:", sys.exc_info()[0])
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()