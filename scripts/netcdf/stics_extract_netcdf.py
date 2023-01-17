import os
import xarray as xr
from glob import glob
import sys
import traceback


def main():
    try:
        print("stics_extract_netcdf.py")
        # work_dir = os.getcwd()
        work_dir = '/work'
        EXPS_DIR = os.path.join(work_dir, 'EXPS')
        ds = xr.open_dataset(os.path.join(EXPS_DIR, 'stics_lai.nc'))
        for y in ds.start_year.values:
            print(str(y))
            f = os.path.join(EXPS_DIR, 'stics_lai_' + str(y) + '.nc')
            print('writing ' + f + '...')
            ds.loc[{'start_year': y}].drop_vars('start_year').to_netcdf(f)
        print("DONE!")
    except:
        print("Unexpected error have been catched:", sys.exc_info()[0])
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()