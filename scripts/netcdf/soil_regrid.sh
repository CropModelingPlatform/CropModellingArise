#!/usr/bin/env bash

source $PWD/config/datamill.ini

DIR_SOIL=$PWD/$DIR_SOIL
DIR_DEM=$PWD/$DIR_DEM
DIR_GRID=$PWD/$DIR_GRID

echo "DIR_GRID : " $DIR_GRID
echo "TXT_GRID : " $DIR_GRID/$TXT_GRID
ls $DIR_GRID/$TXT_GRID

echo "DIR_DEM : " $DIR_DEM
echo "NC_DEM_30 : " $DIR_DEM/$NC_DEM_30
ls $DIR_DEM/$NC_DEM_30


echo "DIR_SOIL : " $DIR_SOIL

TIFS=$(find $DIR_SOIL/5km  -type f -name *_fin.nc 2> /dev/null)
NC_SUFIX="_5km.nc"
for i in ${TIFS[@]};
do
	ls $i
	echo "regrid..."
	NC_NEW=$DIR_SOIL/5km/$(basename -s _5km_fin.nc $i)$NC_SUFIX
	echo $NC_NEW
	cdo -P $CDO_THREADS -remapcon,$DIR_GRID/$TXT_GRID $i $NC_NEW
	wait
	ls $NC_NEW
done
