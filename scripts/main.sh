#!/usr/bin/env bash

export THREADS=46
export INDEXES=($PBS_ARRAY_INDEX)


DATAMILL_WORK='/work'

# Parameters

###Celsius
SD=0   # use gridded sowing date estimated by Celsius as inputs of STICS and DSSAT simulations 

conf_stics (){
  cp "$DATAMILL_WORK/data/$STICS_PLANT" "$1/ficplt1.txt"
  wait
}


#################### Do not change
export -f conf_stics

echo "INDEXES : $INDEXES"
i=$INDEXES;

DIR_EXP=${DATAMILL_WORK}/EXPS/exp_$i
DB_MI=$DIR_EXP/MasterInput.db
DB_CEL=$DIR_EXP/CelsiusV3nov17_dataArise.db
DB_MD=${DATAMILL_WORK}/db/ModelsDictionaryArise.db
echo "DIR_EXP : $DIR_EXP"
echo "DB_MI : $DB_MI"
echo "DB_MD : $DB_MD"
  
python3 ${DATAMILL_WORK}/scripts/workflow/init_dirs.py --index $i;
wait

python3 ${DATAMILL_WORK}/scripts/netcdf/soil_to_db.py --index $i;
wait

python3 ${DATAMILL_WORK}/scripts/netcdf/meteo_to_db.py --index $i;
wait

python3 ${DATAMILL_WORK}/scripts/netcdf/dem_to_db.py --index $i;
wait

python3 ${DATAMILL_WORK}/scripts/workflow/init_simunitlist.py --index $i;
wait

#
/work/scripts/workflow/celsius.sh
wait

# change Crop management and simunitlist
#if [ $SD -eq 1 ]
#then
#python3 ${DATAMILL_WORK}/scripts/workflow/modify_simunilist.py;
#fi
#wait

/work/scripts/workflow/stics.sh
wait
/work/scripts/workflow/dssat.sh
wait

