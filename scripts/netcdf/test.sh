#!/usr/bin/env bash

source $PWD/config/datamill.ini

DIR_SOIL=$PWD/$DIR_SOIL

TIFS=($TIF_BD $TIF_CF)
for i in ${TIFS[@]};
do
	echo $i
done

#-16.92,13.5,-14.8,15.375

#,-16.92,-14.8,15.36,13.48 
