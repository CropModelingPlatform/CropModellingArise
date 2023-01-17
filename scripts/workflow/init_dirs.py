#!/usr/bin/env python

import os
import argparse
import sys
import traceback
import subprocess


def main():
    try:
        print("init.py")
        # work_dir = os.getcwd()
        work_dir = '/work'
        parser = argparse.ArgumentParser(description='Initialize virtual experience directories')
        parser.add_argument('-i', '--index', help="Specify the index of the sub virtual experience")
        args = parser.parse_args()
        i = args.index
        OUTPUT_DIR = os.path.join(work_dir, 'EXPS')
        outdir = os.path.join(OUTPUT_DIR, 'exp_' + str(i))

        os.makedirs(outdir, exist_ok=True)
        dbfrom = os.path.join(work_dir, 'db', 'MasterInput.db')
        dbto = os.path.join(outdir, 'MasterInput.db')
        res = subprocess.check_call(['cp',  dbfrom, dbto])

        dbfrom = os.path.join(work_dir, 'db', 'CelsiusV3nov17_dataArise.db')
        dbto = os.path.join(outdir, 'CelsiusV3nov17_dataArise.db')
        res = subprocess.check_call(['cp',  dbfrom, dbto])

    except:
        print("Unexpected error have been catched:", sys.exc_info()[0])
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
