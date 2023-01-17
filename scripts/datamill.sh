#!/usr/bin/env bash

VERBOSE='false'
DEM_INPUT_DIR=''
CLIM_INPUT_DIR=''
MASK_FILE=''
SHP=''
CROP_MASK_FILE=''
OUTPUT=''
COMMAND=''
MODELS=''
dbMasterInput=''
dbModelsDictionary=''
export NODES=1
export THREADS=1
export START_AT=0
export END_AT=10
FUN=''
TEST=0
CREATE_MASK=1
LOAD_NC=0
CONVERT_STICS=0
CONVERT_DSSAT=0
CONVERT_CELSIUS=0
RUN_STICS=0
RUN_DSSAT=0
RUN_CELSIUS=0
OUT_STICS=0
OUT_DSSAT=0
OUT_CELSIUS=0
CLEAN_CONFIG=0

for i in "$@"; do
  case "$1" in
    -v|--verbose)
      export VERBOSE='true'
      shift
    ;;
    -t|--threads)
      export THREADS=$2
      shift
      shift
    ;;
    -n|--nodes)
      export NODES=$2
      shift
      shift
    ;;    
    -m|--models)
      export MODELS=$2
      shift
      shift
    ;;
    -c|--command)
      export COMMAND=$2
      shift
      shift
    ;;
    -fun|--function)
      export FUN=$2
      shift
      shift
    ;;
    -dem|--dem)
      export DEM_INPUT_DIR="$2"
      shift
      shift
    ;;
    -clim|--climate)
      export CLIM_INPUT_DIR="$2"
      shift
      shift
    ;;
    -mask|--mask)
      export MASK_FILE="$2"
      shift
      shift
    ;;
    -shp|--shp)
      export SHP="$2"
      shift
      shift
    ;;
    -cropmask|--cropmask)
      export CROP_MASK_FILE="$2"
      shift
      shift
    ;;
    -o|--output)
      export OUTPUT="$2"
      shift
      shift
    ;;
    -dbMasterInput)
      export dbMasterInput="-dbMasterInput $2"
      shift
      shift
    ;;
    -dbModelsDictionary)
      export dbModelsDictionary="-dbModelsDictionary $2"
      shift
      shift
    ;;       
    -startAt|--startAt)
      export START_AT="$2"
      shift
      shift
    ;;    
    -endAt|--endAt)
      export END_AT="$2"
      shift
      shift
    ;;
    --no-load-netcdf)
      LOAD_NC=0
      shift
    ;;
    *) # unknown option
      if [ "$1" != "" ]; then
        if [ "$1" != "-h" ]; then
          echo "unknown option: $1 ($i)"
        else
          echo "under construction"
        fi
        exit 2
      fi
      shift
    ;;
  esac
done

myecho (){
  if [ "$VERBOSE" == 'true' ]; then
    echo $@
  fi
}
export -f myecho

mv_stics (){
  STICS=$(find "$1" -mindepth 2 -type d -name "Stics" 2> /dev/null)
  wait
  echo $STICS
  mv $STICS $1
  wait
}
export -f mv_stics

mv_dssat (){
  DSSAT=$(find "$1" -mindepth 2 -type d -name "Dssat" 2> /dev/null)
  wait
  echo $DSSAT
  mv $DSSAT $1
  wait
}
export -f mv_dssat

conf_stics (){
  echo $1
  cp "$DATAMILL_WORK/data/ficplt1.txt" "$1/"
  wait
}
export -f conf_stics

clean_config (){
  rm -Rf $1/DonneesFA
  rm -Rf $1/*.csv
  rm -Rf $1/MasterInput.db
  wait
}
export -f clean_config

print_error (){
  echo "**************************"
  echo "* !!! WORKFLOW ERROR  !!! "
  echo "**************************"
  echo "**************************************************************************************************************"
}
export -f print_error

if [[ -z "$DATAMILL_WORK" ]]; then
  export DATAMILL_WORK='/work'
fi

echo "**************************************************************************************************************"
echo "*******************"
echo "*  WORKFLOW START  "
echo "*******************"
echo " "
echo "DATAMILL_WORK : '"$DATAMILL_WORK"'"
cd $DATAMILL_WORK

echo "VERBOSE : $VERBOSE"
echo "DEM_INPUT_DIR : '"$DEM_INPUT_DIR"'"
echo "CLIM_INPUT_DIR : '"$CLIM_INPUT_DIR"'"
echo "MASK_FILE : '"$MASK_FILE"'"
echo "OUTPUT : '"$OUTPUT"'"
echo "COMMAND : $COMMAND"
echo "MODELS : $MODELS"
echo "VERBOSE : $VERBOSE"
echo "dbMasterInput : '"$dbMasterInput"'"
echo "dbModelsDictionary : '"$dbModelsDictionary"'"
echo "NODES : $NODES"
echo "THREADS : $THREADS"
echo "START_AT : $START_AT"
echo "END_AT : $END_AT"
echo "FUN : $FUN"
echo "LOAD_NC : $LOAD_NC"
echo "CONVERT_STICS : $CONVERT_STICS"
echo "CONVERT_DSSAT : $CONVERT_DSSAT"
echo "CONVERT_CELSIUS : $CONVERT_CELSIUS"
echo "RUN_STICS : $RUN_STICS"
echo "RUN_DSSAT : $RUN_DSSAT"
echo "RUN_CELSIUS : $RUN_CELSIUS"
echo "OUT_STICS : $OUT_STICS"
echo "OUT_DSSAT : $OUT_DSSAT"
echo "OUT_CELSIUS : $OUT_CELSIUS"
echo "CLEAN_CONFIG : $CLEAN_CONFIG"

if [ "$OUTPUT" == "" ]; then
  echo "error: no output, please use -o | --output"
  exit 2
else
  myecho "OUTPUT : $OUTPUT"
fi

echo "*******************"
echo "*  python env      "
echo "*"
conda --version
python3 --version
#   EXPS=$(find "$INPUT" -maxdepth 1 -type d -name "exp*"  2> /dev/null)
#   wait
#   echo "exps: $EXPS"

#  echo "load water ..."
#  python3 ${DATAMILL_WORK}/scripts/load_water.py
#  wait
if [ $TEST -eq 1 ]; then
  echo "**************************************************************************************************************"
  echo "*******************"
  echo "*  TEST     "
  echo "*                  "
  export work_dir=${DATAMILL_WORK}
  export MASK_FILE=${DATAMILL_WORK}/mask_IRC.nc
  export CLIM_INPUT_DIR=${DATAMILL_WORK}/TNZ_2010_to_2011/
  export OUTPUT_DIR=${DATAMILL_WORK}/TNZ2010TEST
  python3 ${DATAMILL_WORK}/scripts/test.py
  wait
  echo " "
  echo "*  TEST DONE !"
  echo " "
  echo "**************************************************************************************************************"
fi

if [ $CREATE_MASK -eq 1 ]; then
  echo "**************************************************************************************************************"
  echo "*******************"
  echo "*  create mask     "
  echo "*                  "
  if [ "$CROP_MASK_FILE" == "" ]; then
    echo "error: no crop mask/grid file, please use -cropmask | --cropmask"
    exit 2
  else
    myecho "CROP_MASK_FILE : $CROP_MASK_FILE"
  fi  
  if [ "$SHP" == "" ]; then
    echo "error: no shape file, please use -shp | --shp"
    exit 2
  else
    myecho "SHP : $SHP"
  fi    
  #export CROP_MASK_SHORT="${DATAMILL_WORK}/ANNUAL_AREA_HARVESTED_IRC_CROP2_HA"
  export CROP_MASK_SHORT="${DATAMILL_WORK}/$CROP_MASK_FILE"
  export MASK_OUTPUT_DIR=${DATAMILL_WORK}
  # export SHP=${DATAMILL_WORK}/TZAwaterProvinces.shp
  ${DATAMILL_WORK}/scripts/netcdf/create_mask.sh
  wait
  echo " "
  echo "*  create mask : DONE !"
  echo " "
  echo "**************************************************************************************************************"  
fi

if [ $LOAD_NC -eq 1 ]; then
  echo "**************************************************************************************************************"
  echo "*******************"
  echo "*  load netcdf     "
  echo "*                  "
  
  if [ "$MASK_FILE" == "" ]; then
    echo "error: no mask/grid file, please use -mask | --mask"
    exit 2
  else
    myecho "MASK_FILE : $MASK_FILE"
  fi
  if [ "$DEM_INPUT_DIR" == "" ]; then
    echo "error: no digital elevation model, please use -dem | --dem"
    exit 2
  else
    myecho "DEM_INPUT_DIR : $DEM_INPUT_DIR"
  fi
  if [ "$CLIM_INPUT_DIR" == "" ]; then
    echo "error: no climate data, please use -clim | --clim"
    exit 2
  else
    myecho "CLIM_INPUT_DIR : $CLIM_INPUT_DIR"
  fi
  
  python3 ${DATAMILL_WORK}/scripts/netcdf2csv.py \
   -t $THREADS \
   -n $NODES \
   --dem "${DATAMILL_WORK}/$DEM_INPUT_DIR" \
   --clim "${DATAMILL_WORK}/$CLIM_INPUT_DIR" \
   --mask "${DATAMILL_WORK}/$MASK_FILE" \
   -o "${DATAMILL_WORK}/$OUTPUT"
  RES=$?
  echo "RES: "$RES
  if [ $RES -eq 1 ]; then
    print_error
    exit 1
  fi

  echo " "
  echo "*  load netcdf : DONE !"
  echo " "
  echo "**************************************************************************************************************"    
fi
# echo "create_simunitlist ..."
# python3 ${DATAMILL_WORK}/scripts/create_simunitlist.py
# wait

#  echo "compute ETP ..."
#  EXPS=$(find "$INPUT" -maxdepth 1 -type d -name "exp*"  2> /dev/null)
#  wait
#  echo "exps: $EXPS"
#  printf "${EXPS//" "/\\n}" | xargs -n1 -P50 -I{} \
#    bash -c "cd {} && datamill compute -fun etp -t ${THREADS} -dbModelsDictionary \"${DATAMILL_WORK}/db/ModelsDictionaryArise.db\" -dbMasterInput \"{}/MasterInput.db\""
#  wait

#  echo "copying workspace from ${INPUT} to ${INPUT}CPL"
#  printf "${EXPS//" "/\\n}" | xargs -n1 -P20 -I{} \
#     bash -c "cp -R {} ${INPUT}CPL/"
#  wait

echo " "

if [ $CONVERT_DSSAT -eq 1 ]; then
  echo "**************************************************************************************************************"
  echo "*******************"
  echo "*  generate DSSAT  "
  echo " "
  EXPS=$(find "${DATAMILL_WORK}/${OUTPUT}" -mindepth 1 -maxdepth 1 -type d -name "exp*"  2> /dev/null)
  wait
  echo "EXPS : "${#EXPS[@]}
  printf "${EXPS//" "/\\n}" | xargs -n1 -P${NODES} -I{} \
    bash -c "echo {} && cd {} && \
    datamill convert -m dssat \
    -t ${THREADS} \
    -dbModelsDictionary \"${DATAMILL_WORK}/db/NEW/ModelsDictionaryArise.db\" \
    -dbMasterInput \"{}/MasterInput.db\" \
    -sstart ${START_AT} \
    -send ${END_AT}"
  wait
  echo " "
  echo "*  generate DSSAT : DONE !"
  echo " "

  echo "*******************"
  echo "*  mv DSSAT        "
  echo " "
  printf "${EXPS//" "/\\n}" | xargs -n1 -P${THREADS} -I{} \
  bash -c "echo {} && rm -Rf {}/Dssat && mv_dssat {}"
  wait
  echo " "
  echo "*  mv DSSAT : DONE !"
  echo " "  
  echo "**************************************************************************************************************"  
fi

if [ $CONVERT_STICS -eq 1 ]; then
  echo "**************************************************************************************************************"
  echo "*******************"
  echo "*  generate STICS  "
  echo " "
  EXPS=$(find "${DATAMILL_WORK}/${OUTPUT}" -mindepth 1 -maxdepth 1 -type d -name "exp*"  2> /dev/null)
  wait
  echo "EXPS : "${#EXPS[@]}
  printf "${EXPS//" "/\\n}" | xargs -n1 -P${NODES} -I{} \
    bash -c "echo {} && cd {} && \
    datamill convert -m stics \
    -t ${THREADS} \
    -dbModelsDictionary \"${DATAMILL_WORK}/db/NEW/ModelsDictionaryArise.db\" \
    -dbMasterInput \"{}/MasterInput.db\"\
    -sstart ${START_AT} \
    -send ${END_AT}"
  wait
  echo " "
  echo "*  generate STICS : DONE !"
  echo " "

  echo "*******************"
  echo "*  mv STICS        "
  echo " "
  #EXPS=$(find "$OUTPUT" -mindepth 1 -maxdepth 1 -type d -name "exp*"  2> /dev/null)
  #wait
  #echo "EXPS : "${#EXPS[@]}
  printf "${EXPS//" "/\\n}" | xargs -n1 -P${THREADS} -I{} \
  bash -c "echo {} && rm -Rf {}/Stics && mv_stics {}"
  wait
  echo " "
  echo "*  mv STICS : DONE !"
  echo " "
 
  echo "*******************"
  echo "*  config STICS    "
  echo " "
  EXPS=$(find "${DATAMILL_WORK}/${OUTPUT}" -mindepth 3 -type d -name "*_*"  2> /dev/null | grep "Stics")
  wait
  echo "EXPS : "${#EXPS[@]}
  printf "${EXPS//" "/\\n}" | xargs -n1 -P${THREADS} -I{} \
      bash -c "conf_stics {}"
  wait
  echo " "
  echo "*  config STICS : DONE !"
  echo " "  
  echo "**************************************************************************************************************"  
fi

if [ $CLEAN_CONFIG -eq 1 ]; then
  echo "**************************************************************************************************************"
  echo " "
  echo "*******************"
  echo "*  cleaning        "
  echo " "
  EXPS=$(find "${DATAMILL_WORK}/${OUTPUT}" -mindepth 1 -maxdepth 1 -type d -name "exp*"  2> /dev/null)
  #EXPS=$(find "$OUTPUT" -mindepth 1 -maxdepth 1 -type d -name "exp*"  2> /dev/null)
  wait
  printf "${EXPS//" "/\\n}" | xargs -n1 -P${THREADS} -I{} \
      bash -c "clean_config {}"
  wait
# rm -Rf $STICS/*/ && rm -Rf $x/DonneesFA && rm -Rf $x/*.csv
  #  wait
    # rm -Rf $x/MasterInput.db
#  done  
  echo " "
  echo "*  cleaning : DONE !"
  echo " "
  echo "**************************************************************************************************************"  
fi

if [ $RUN_STICS -eq 1 ]; then
  echo "**************************************************************************************************************"
  echo "*******************"
  echo "*  run STICS       "
  echo " "
  DIRS=$(find "${DATAMILL_WORK}/${OUTPUT}" -mindepth 2 -maxdepth 2 -type d -name "Stics" 2> /dev/null)
  wait
  echo "DIRS : "${#DIRS[@]}
  printf "${DIRS//" "/\\n}" | xargs -n1 -P${NODES} -I{} \
      bash -c "echo {} && /work/scripts/stics-main.bash -v -k -i {} -t ${THREADS}"
  wait
  echo " "
  echo "*  run STICS : DONE !"
  echo " "
  echo "**************************************************************************************************************"  
fi

if [ $RUN_DSSAT -eq 1 ]; then
  echo "**************************************************************************************************************"
  echo "*******************"
  echo "*  run DSSAT       "
  echo " "
  DIRS=$(find "${DATAMILL_WORK}/${OUTPUT}" -mindepth 2 -maxdepth 2 -type d -name "Dssat" 2> /dev/null)
  wait
  echo "DIRS : "${#DIRS[@]}
  printf "${DIRS//" "/\\n}" | xargs -n1 -P${NODES} -I{} \
      bash -c "echo {} && /work/scripts/dssat-main.bash -v -k -i {} -t ${THREADS}"
  wait
  echo " "
  echo "*  run DSSAT : DONE !"
  echo " "
  echo "**************************************************************************************************************"
fi

if [ $OUT_STICS -eq 1 ]; then
  echo "**************************************************************************************************************"
  echo "*******************"
  echo "*  format          " 
  echo "*  Stics outputs   "
  echo " "

  python3 ${DATAMILL_WORK}/scripts/csv2netcdf.py
  wait
#  echo "cleaning $INPUT workspace..."
#  printf "${EXPS//" "/\\n}" | xargs -n1 -P15 -I{} \
#    bash -c "echo {} && rm -Rf {}/Stics && rm -f {}/*.csv && rm -f {}/*.nc"
#  wait
  echo " "
  echo "*  Stics outputs : DONE !"
  echo " "
  echo "**************************************************************************************************************"
fi

# cd $DATAMILL_WORK/DonneesFA/modelisation/Arise/datamillarise/applidatamill/Stics
# DATE=$(date --iso-8601=s)
# OUTPUT_FILE="USMS_$DATE.zip"
# zip -rq $OUTPUT_FILE ./*
# cp $OUTPUT_FILE $OUTPUT
#  cp -Rf /home/robaldog/scratch/OUTPUT2 /home/robaldog/scratch/OUTNOCPL

echo "*******************"
echo "*  WORKFLOW END!   "
echo "*******************"  

exit 0