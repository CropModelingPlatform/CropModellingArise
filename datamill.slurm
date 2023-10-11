#!/bin/bash
##SBATCH -p agap_short
#SBATCH -p agap_long
#SBATCH -a agap
#SBATCH --job-name=DATAMILL
#SBATCH --output="datamill_%A_%a.out"
#SBATCH --error="datamill_%A_%a.err"
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
##SBATCH --ntasks-per-node=10
#SBATCH --mem=96G
# #SBATCH --time=2:00:00
##SBATCH --mail-type=begin        
##SBATCH --mail-type=end          
##SBATCH --mail-user=cyrille_ahmed.midingoyi@cirad.fr

export SIMUL_DIR=$SLURM_SUBMIT_DIR

echo "SIMUL_DIR =  ${SIMUL_DIR} "

#export SINGULARITY_CAHEDIR=${SIMUL_DIR}/tmp

#echo "SSINGULARITY_CAHEDIR =  ${SINGULARITY_CAHEDIR} "

cd ${SIMUL_DIR}

module load singularity/3.5 squashfs/4.3 libarchive/3.3.2


date

singularity exec --no-home -B /lustre/midingoyic/CropModellingArise:/work -B /lustre/midingoyic/tmp:$TMPDIR -B /home/midingoyic/projects/AIDA/LIMA/merged_data:/inputData datamill.sif /work/scripts/main.sh

date

# Example on how to submit this jobarray to SLURM:
#  sbatch --array=1-N%C   --export='cgid=x,ss=y' serial-ncl-cu-jobarray.slurm  , where N=number of total jobs & C= the concurrent tasks at the same time

# References:
# https://help.rc.ufl.edu/doc/Using_Variables_in_SLURM_Jobs
# https://oit.utk.edu/hpsc/isaac-open-enclave-new-kpb/isaac-open-enclave-slurm/

