#!/usr/bin/env bash

run_dssat (){
  local USM_DIR="${PWD}"
  for i in "$@"; do
    case "$1" in
        -u|--usm-directory)
          USM_DIR=$2
          shift
          shift
        ;;
        *) # unknown option
          if [ "$1" != "" ]; then
            echo "unknown option: $1"
            exit 2
          fi
          shift
        ;;
    esac
  done
  local OLD_PWD="${PWD}"
  cd $USM_DIR
  if [ "$VERBOSE" == 'true' ]; then
    dssat B DSSBatch.v47
  else
    dssat B DSSBatch.v47 > /dev/null
  fi
  cd $OLD_PWD
}
export -f run_dssat

myecho (){
  if [ "$VERBOSE" == 'true' ]; then
    echo $@
  fi
}
export -f myecho

INPUT_DIR=''
THREADS=1
KEEP_CONFIG='false'
VERBOSE='false'

for i in "$@"; do
  case "$1" in
      -t|--threads)
        THREADS=$2
        shift
        shift
      ;;
      -i|--input)
        INPUT_DIR="$2"
        shift
        shift
      ;;
      -k|--keep-configuration)
        KEEP_CONFIG='true'
        shift
      ;;
      -v|--verbose)
        VERBOSE='true'
        shift
      ;;
      *) # unknown option
        if [ "$1" != "" ]; then
          echo "unknown option: $1 ($i)"
          exit 2
        fi
        shift
      ;;
  esac
done

export DSSAT_CONFIG_FILES=""
export KEEP_CONFIG=$KEEP_CONFIG
export VERBOSE=$VERBOSE
export THREADS=$THREADS

if [ "$INPUT_DIR" == "" ]; then
  echo "error: no input dir, please use -i | --input"
  exit 2
fi
echo "*************************"
echo "*  DSSAT is running..."
echo "*************************"
echo "INPUT_DIR : $INPUT_DIR"
echo "THREADS : $THREADS"
echo "VERBOSE : $VERBOSE"
echo "KEEP_CONFIG : $KEEP_CONFIG"

WKS_PATH=$INPUT_DIR
USMS_DIRS=$(find $WKS_PATH -type d -mindepth 1 2> /dev/null)
echo ""
#echo "--> USMS_DIRS : $USMS_DIRS"
echo "run several usms (parallelized)"
printf "${USMS_DIRS//" "/\\n}" | xargs -n1 -P$THREADS -I{} bash -c "run_dssat -u {}"
wait
 
echo "*************************"
echo "*  DSSAT completed !!!"
echo "*************************"
exit 0
