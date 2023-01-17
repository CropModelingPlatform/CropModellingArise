
import sqlite3
import calculate_etp
from joblib import Parallel, delayed
import argparse
import sys
import traceback
import os
import pandas as pd

THREADS = 96


def call_calculate_etp(data, DB_MI):

    # data : lat, Alt, J, Tn, Tx, Tm, Tdewn, Tdewx, Vm, Rg
    sqlite_connection = sqlite3.connect(DB_MI)
    sqlite_cursor = sqlite_connection.cursor()
    alt_lat = sqlite_cursor.execute(f"select altitude, latitudeDD from Coordinates where idPoint='{data[0]}';").fetchall()
    Alt = alt_lat[0][0]
    lat = alt_lat[0][1]
    J = data[3]
    Tn = data[8]
    Tx = data[7]
    Tm = data[9]
    Tdewn = data[14]
    Tdewx = data[15]
    Vm = data[11]
    Rg = data[6]
    sqlite_connection.close()
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
        sqlite_connection = sqlite3.connect(DB_MI)
        sqlite_cursor = sqlite_connection.cursor()

        rows = sqlite_cursor.execute("select * from RaClimateD;").fetchall()

        res = Parallel(n_jobs=THREADS, verbose=100, max_nbytes=None, prefer="processes")(
                delayed(call_calculate_etp)(f,DB_MI ) for f in rows)

        with sqlite3.connect(DB_MI, timeout=10) as conn:
            df = pd.read_sql('select * from RaClimateD', conn)
            df["Etppm"] = res
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