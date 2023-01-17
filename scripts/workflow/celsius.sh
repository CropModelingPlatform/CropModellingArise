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

  python3 ${DATAMILL_WORK}/scripts/functions/compute_etp.py --index $i;

  cd $DIR_EXP
  datamill convert -m celsius \
    -t ${THREADS} \
    -dbMasterInput ${DB_MI} \
    -dbModelsDictionary ${DB_MD} \
    -dbCelsius ${DB_CEL}
  wait

  celsius convert -m celsius \
  -t ${THREADS} \
  -dbMasterInput ${DB_MI} \
  -dbModelsDictionary ${DB_MD} \
  -dbCelsius ${DB_CEL}
   wait

   rm -Rf $DIR_EXP/DonneesFA
   wait

  python3 ${DATAMILL_WORK}/scripts/create_summary_out_celsius.py --index $i;
  wait
done
