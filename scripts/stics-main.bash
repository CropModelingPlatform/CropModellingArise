#!/usr/bin/env bash

INPUT_DIR=''
THREADS=1
KEEP_CONFIG='false'
VERBOSE='true'

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

export STICS_CONFIG_FILES=" climat.txt ficini.txt ficplt1.txt fictec1.txt \
                            new_travail.usm param.sol station.txt tempopar.sti \
                            tempoparv6.sti var.mod prof.mod rap.mod recup.tmp \
                            snow_variables.txt"
export KEEP_CONFIG=$KEEP_CONFIG
export VERBOSE=$VERBOSE
export THREADS=$THREADS

. stics-tools.bash --source-only
. stics-run.bash --source-only

if [ "$INPUT_DIR" == "" ]; then
  echo "error: no input dir, please use -i | --input"
  exit 2
fi
echo "*************************"
echo "*  STICS is running..."
echo "*************************"
echo "INPUT_DIR : $INPUT_DIR"
echo "THREADS : $THREADS"
echo "VERBOSE : $VERBOSE"
echo "KEEP_CONFIG : $KEEP_CONFIG"

WKS_PATH=$INPUT_DIR
USMS_DIRS=$(find $WKS_PATH -type d -mindepth 1 2> /dev/null)
myecho ""
#myecho "--> USMS_DIRS : $USMS_DIRS"
myecho "run several usms (parallelized)"
printf "${USMS_DIRS//" "/\\n}" | xargs -n1 -P$THREADS -I{} bash -c "run_usm -u {}"
wait
 
echo "*************************"
echo "*  STICS completed !!!"
echo "*************************"
exit 0