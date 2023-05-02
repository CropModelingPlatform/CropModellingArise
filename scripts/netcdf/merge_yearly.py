import os
import xarray as xr
from glob import glob
import sys
import traceback
from joblib import Parallel, delayed


def merge(m):
    work_dir = '/work'
    EXPS_DIR = os.path.join(work_dir, 'EXPS')
    ncs = glob(os.path.join(EXPS_DIR,'exp_*', m+'_yearly_*.nc'))
    v = list(set(["_".join(os.path.basename(u).split("_")[2:-1]) for u in ncs]))
    if len(ncs) == 0:
        return
    for n in v:
        ncss = glob(os.path.join(EXPS_DIR,'exp_*', m+'_yearly_'+n+'_*.nc'))
        if len(ncss)==0: return
        dss = list()
        for nc in ncss:
            dss.append(xr.open_dataset(nc))
        outdir = os.path.join(work_dir,"outputs")
        os.makedirs(outdir, exist_ok=True)
        ofin1 = os.path.join(outdir, m+'_yearly_'+n+'.nc')
        xr.merge(dss).to_netcdf(ofin1)
    print("DONE!")

def main():
    try:
        print("merge_csv.py")
        models = ["stics","dssat","celsius"]
        Parallel(n_jobs=-1)(
            delayed(merge)(f) for f in models)
    except:
        print("Unexpected error have been catched:", sys.exc_info()[0])
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()        

