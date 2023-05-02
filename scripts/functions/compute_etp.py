
import sqlite3
import calculate_etp
from joblib import Parallel, delayed
import argparse
import sys
import traceback
import os
import pandas as pd

THREADS = 46


def call_calculate_etp(data):

    # data : lat, Alt, J, Tn, Tx, Tm, Tdewn, Tdewx, Vm, Rg
    Alt = data[17]
    lat = data[18]
    J = data[3]
    Tn = data[8]
    Tx = data[7]
    Tm = data[9]
    Tdewn = data[14]
    Tdewx = data[15]
    Vm = data[11]
    Rg = data[6]
    res = calculate_etp.ET0pm_Tdew(lat, Alt, J, Tn, Tx, Tm, Tdewn, Tdewx, Vm, Rg)
    return res
    

def main():
    try:
        work_dir = '/work' 
        parser = argparse.ArgumentParser(description='load etp into database')
        parser.add_argument('-i', '--index', help="Specify the index of the sub virtual experience")
        args = parser.parse_args()
        i = args.index
        EXPS_DIR = os.path.join(work_dir, 'EXPS')
        EXP_DIR = os.path.join(EXPS_DIR, 'exp_' + str(i))
        DB_MI = os.path.join(EXP_DIR, 'MasterInput.db')
        
        sql1 = """ALTER TABLE RaClimateD
                ADD COLUMN altitude FLOAT;
                ALTER TABLE RaClimateD
                    ADD COLUMN latitude FLOAT;"""

        sql = """UPDATE RaClimateD
        SET altitude = (SELECT Coordinates.altitude
                            FROM Coordinates
                            WHERE Coordinates.idPoint = RaClimateD.idPoint),
        latitude = (SELECT  Coordinates.latitudeDD
                            FROM Coordinates
                            WHERE Coordinates.idPoint = RaClimateD.idPoint)"""
        with sqlite3.connect(DB_MI, timeout=15) as conn:
            cur = conn.cursor()
            cur.executescript(sql1)
            cur.executescript(sql)
            conn.commit()

        with sqlite3.connect(DB_MI, timeout=10) as conn:
            df = pd.read_sql('select * from RaClimateD', conn)
            df["Etppm"] = df.apply(lambda x: calculate_etp.ET0pm_Tdew(df["latitude"], df["altitude"], df["DOY"], df["tmin"], df["tmax"], df["tmoy"], df["Tdewmin"], df["Tdewmax"], df["wind"], df["srad"]), axis=1)
            cur = conn.cursor()
            cur.executescript("DROP TABLE RAclimateD;")
            conn.commit()
            df.to_sql('RAclimateD', conn, if_exists='replace', index=False)
            conn.commit()
        
        print("ETP DONE")
    except:
        print("Unexpected error have been catched:", sys.exc_info()[0])
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()