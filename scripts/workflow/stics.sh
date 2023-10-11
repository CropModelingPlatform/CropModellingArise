#!/usr/bin/env bash

export THREADS=46
export INDEXES=($SLURM_ARRAY_TASK_ID)


if [[ -z "$DATAMILL_WORK" ]]; then
  export DATAMILL_WORK='/work'
fi

echo "INDEXES : $INDEXES"

i=$INDEXES;

DIR_EXP=${DATAMILL_WORK}/EXPS/exp_$i
DB_MI=$DIR_EXP/MasterInput.db
DB_CEL=$DIR_EXP/CelsiusV3nov17_dataArise.db
DB_MD=${DATAMILL_WORK}/db/ModelsDictionaryArise.db
echo "DIR_EXP : $DIR_EXP"
echo "DB_MI : $DB_MI"
echo "DB_MD : $DB_MD"
    
cd $DIR_EXP
datamill convert -m stics \
  -t ${THREADS} \
  -dbMasterInput ${DB_MI} \
  -dbModelsDictionary ${DB_MD} 
wait

cd ${DATAMILL_WORK}
mv  $DIR_EXP/DonneesFA/modelisation/Arise/datamillarise/applidatamill/Stics  $DIR_EXP/
wait
rm -Rf $DIR_EXP/DonneesFA
wait

echo "add genotype stics"
python3 ${DATAMILL_WORK}/scripts/genotype_stics.py --dbmi ${DB_MI} --index $DIR_EXP/Stics;
wait

cd ${DATAMILL_WORK}/scripts
./stics-main.bash -v -k -i $DIR_EXP/Stics -t ${THREADS}
cd ${DATAMILL_WORK}
wait


python3 ${DATAMILL_WORK}/scripts/create_summary_out_stics.py --index $i;
wait

#rm -Rf $DIR_EXP/Stics
wait
