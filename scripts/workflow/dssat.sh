#!/usr/bin/env bash

export THREADS=96
export INDEXES=($PBS_ARRAY_INDEX)

if [[ -z "$DATAMILL_WORK" ]]; then
  export DATAMILL_WORK='/work'
fi


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
  
  cd $DIR_EXP
  datamill convert -m dssat \
    -t ${THREADS} \
    -dbMasterInput ${DB_MI} \
    -dbModelsDictionary ${DB_MD} 
  wait

  cd ${DATAMILL_WORK}
  mv  $DIR_EXP/DonneesFA/modelisation/Arise/datamillarise/applidatamill/Dssat  $DIR_EXP/
  wait
  rm -Rf $DIR_EXP/DonneesFA
  wait

  EXPS=$(find "${DIR_EXP}/Dssat" -type d -name "*_*"  2> /dev/null)
  wait

  cd ${DATAMILL_WORK}/scripts
  ./dssat-main.bash -v -k -i $DIR_EXP/Dssat -t ${THREADS}
  cd ${DATAMILL_WORK}
  wait

  python3 ${DATAMILL_WORK}/scripts/create_summary_out_dssat.py --index $i;
  wait

  rm -Rf $DIR_EXP/Dssat
  wait
done