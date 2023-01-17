#!/usr/bin/env bash

export THREADS=96
export INDEXES=($PBS_ARRAY_INDEX)


DATAMILL_WORK='/work'

# Parameters
## simulation options
### General
WS=1 # 1 if water limited else 0
NS=1 # 1 if nitrogen limited else 0
KS=0 # 1 if Potassium limited else 0
PS=0 # 1 if Phosphorous limited else 0


###Celsius
SD=1   # use gridded sowing date estimated by Celsius as inputs of STICS and DSSAT simulations 

## Crop Management
idCultivar="1.10"
sowingDate=195  
sdens=7
OFertiPolicyCode="0"
InoFertiPolicyCode="0"
IrrigationPolicyCode="0"
SoilTillPolicyCode="0"


conf_stics (){
  cp "$DATAMILL_WORK/data/$STICS_PLANT" "$1/ficplt1.txt"
  wait
}



#################### Do not change
export -f conf_stics

echo "INDEXES : $INDEXES"
for i in $INDEXES;
do
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

  python3 ${DATAMILL_WORK}/scripts/workflow/init_simunitlist.py --index $i --option $WS $NS $KS $PS $SD $sowingDate;
  wait
done

/work/scripts/workflow/celsius.sh
wait

# change Crop management and simunitlist
if [ $SD -eq 1 ]
then
python3 ${DATAMILL_WORK}/scripts/workflow/modify_simunilist.py --index $INDEXES --option $idCultivar $sdens $OFertiPolicyCode $InoFertiPolicyCode $IrrigationPolicyCode $SoilTillPolicyCode;
fi
wait

/work/scripts/workflow/stics.sh
wait
/work/scripts/workflow/dssat.sh
wait

