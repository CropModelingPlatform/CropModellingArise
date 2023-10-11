#!/bin/bash
#SBATCH -p agap_short
#SBATCH -a agap
#SBATCH --job-name=NETCDF
#SBATCH --ntasks=3
#SBATCH --time=1:00:00
#SBATCH --mail-type=begin        
#SBATCH --mail-type=end          
#SBATCH --mail-user=cyrille_ahmed.midingoyi@cirad.fr

export SIMUL_DIR=$SLURM_SUBMIT_DIR

cd ${SIMUL_DIR}

echo "SIMUL_DIR =  ${SIMUL_DIR} "


module load singularity/3.5 squashfs/4.3 libarchive/3.3.2


date

singularity exec --no-home -B /lustre/midingoyic/CropModellingArise:/work -B /lustre/midingoyic/tmp:$TMPDIR datamill.sif python3 /work/scripts/netcdf/merge_yearly.py

date
