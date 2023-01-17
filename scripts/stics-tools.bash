#!/usr/bin/env bash

myecho (){
  if [ "$VERBOSE" == 'true' ]; then
    echo $@
  fi
}
export -f myecho

ls_wks(){
    local WKS=$(find $1/*/* -type d 2> /dev/null)
    if [ "$WKS" != "" ]; then
        local WKS=$(ls -d $1/*)
    fi
    echo $WKS
}
export -f ls_wks

ls_usms(){
    local USMS=$(find $1 -type d 2> /dev/null)
    echo $USMS
}
export -f ls_usms

force_code_optim(){
  myecho "param.sti : force code optim 1 in new_travail.usm file"
  sed -i -z 's/codeoptim\n0/codeoptim\n1/g' $1/new_travail.usm
}
export -f force_code_optim

clean_config () {
  if [ "$KEEP_CONFIG" == 'false' ]; then
    myecho "clean configuration files for $1"
    OLD_PWD=$(pwd)
    cd $1
    rm -rf $STICS_CONFIG_FILES
    cd $OLD_PWD
  fi
}
export -f clean_config

clean_rapport () {
  myecho "clean rapport for workspace $1"
  sed -i 's/ //g' $1/mod_rapport.sti
  sed -i -z 's/;\n/\n/g' $1/mod_rapport.sti
}
export -f clean_rapport

merge_rapport () {
  myecho "merge rapport for workspace $1"
  local USMS_DIRS=( $(ls_usms "$1") )
  if [ "$USMS_DIRS" != '' ]; then
    cp ${USMS_DIRS[0]}/mod_rapport.sti $1/mod_rapport.sti
    for u in ${USMS_DIRS[@]:1}; do
      tail -n +2 ${u}/mod_rapport.sti >> $1/mod_rapport.sti
    done
  fi
  clean_rapport $1 
}
export -f merge_rapport