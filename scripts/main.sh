#!/usr/bin/env bash

set -e

export THREADS=46
export INDEXES=($SLURM_ARRAY_TASK_ID)

data='/inputData'
DATAMILL_WORK='/work'




##############Data########
# you need to have soil, climate, elevation and crop mask (spatial data with the same resolution and grid)
#

##################################################################### BEGIN OF CONFIGURATION PART################################################################
### Please don't use underscore (_) to name the id of CropManagement records


### which varieties in crop management table you would like to simulate
variety=("1.10")
 
### model options # which models would you like to simulate
models=("stics") #("stics" "celsius" "dssat") # or mod=("celsius") for only celsius simulation

###Sowing options
# 1) use gridded sowing date estimated by Celsius as inputs of STICS and DSSAT simulations SD=1
# 2) use fixed sowing date SD=0
# 3) use a list of sowing dates SD=3
SD=0  

###initial conditions
initcond=1

### type of soil : check in soilType table of MasterInput.db database the soil texture type which will be applied
soilTextureType='Loamy Sand'

### simulation options; you will see the description of corresponding simulation options in SimulationOption table of MasterInput.db
    #option=(1 2 3 4) 
simoption=(2 4)

### fertilization options # give the list of fertilization options you would like to simulate In CropManagement table InoFertiPolicyCode column
    #fertioption=(0 1 2)   
fertioption=(0)

### irrigation options

#### start date and end date of simulation # we suppose to use the same start and end date for all pixels
startd=110
endd=360

##################################################################### END OF CONFIGURATION PART################################################################


echo "INDEXES : $INDEXES"
i=$INDEXES;

DIR_EXP=${DATAMILL_WORK}/EXPS/exp_$i
DB_MI=$DIR_EXP/MasterInput.db
DB_CEL=$DIR_EXP/CelsiusV3nov17_dataArise.db
DB_MD=${DATAMILL_WORK}/db/ModelsDictionaryArise.db
echo "DIR_EXP : $DIR_EXP"
echo "DB_MI : $DB_MI"
echo "DB_MD : $DB_MD"
  
#python3 ${DATAMILL_WORK}/scripts/workflow/init_dirs.py --index $i;
wait

#python3 ${DATAMILL_WORK}/scripts/netcdf/soil_to_db.py --index $i --soilTexture "$soilTextureType";
wait

#python3 ${DATAMILL_WORK}/scripts/netcdf/meteo_to_db.py --index $i;
python3 ${DATAMILL_WORK}/scripts/netcdf/test_meteo_to_db.py --index $i;
wait

:<<comment

python3 ${DATAMILL_WORK}/scripts/netcdf/dem_to_db.py --index $i;
wait

python3 ${DATAMILL_WORK}/scripts/workflow/init_simunitlist.py --index $i --startdate $startd --enddate $endd --cropvariety "${variety[@]}" --ferti "${fertioption[@]}" --option "${simoption[@]}" --sowingoption $SD;
wait

#
if [[ " ${models[@]} " =~ " celsius " ]]; then
   /work/scripts/workflow/celsius.sh
fi
wait


if [ $SD -eq 1 ]
then
python3 ${DATAMILL_WORK}/scripts/workflow/modify_simunilist.py --index $i;
fi 
wait

if [[ " ${models[@]} " =~ " stics " ]]; then
   /work/scripts/workflow/stics.sh
fi
wait

if [[ " ${models[@]} " =~ " dssat " ]]; then
   /work/scripts/workflow/dssat.sh
fi
wait

comment
