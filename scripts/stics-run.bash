#!/usr/bin/env bash

. stics-tools.bash --source-only

run_stics_modulo (){
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
    /opt/stics/bin/stics_modulo
  else
    /opt/stics/bin/stics_modulo > /dev/null
  fi
  cd $OLD_PWD
}
export -f run_stics_modulo

run_usm () {
  myecho "run_usm"
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
  myecho "USM : $USM_DIR"
  sed -i -z 's/codeseprapport\n1/codeseprapport\n2/g' $USM_DIR/tempopar.sti \
    || myecho "tempopar.sti not founded in $USM_DIR"
  if [ -f $USM_DIR/param.sti ]; then
     force_code_optim $USM_DIR
  fi

  run_stics_modulo -u $USM_DIR
};
export -f run_usm