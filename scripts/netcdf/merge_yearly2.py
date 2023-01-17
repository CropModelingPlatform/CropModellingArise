import os
import xarray as xr
from glob import glob
import sys
import traceback


def main():
    try:
        print("merge.py")
        models = ["stics","dssat","celsius"]
        work_dir = '/work'
        EXPS_DIR = os.path.join(work_dir, 'EXPS')
        for m in models:                                                                                                                                                                    
            ncs = glob(os.path.join(EXPS_DIR, 'exp_*', m+'_yearly_*.nc'))
            if len(ncs)==0:
                continue
            dss = list()
            for nc in ncs:
                dss.append(xr.open_dataset(nc))
            ofin = os.path.join(EXPS_DIR, m+'_yearly.nc')
            xr.merge(dss).to_netcdf(ofin)
        print("DONE!")
    except:
        print("Unexpected error have been catched:", sys.exc_info()[0])
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()        

