#!/usr/bin/env bash

source $PWD/config/datamill.ini

DIR_SOIL=$PWD/$DIR_SOIL
DIR_LAND=$PWD/$DIR_LAND

echo "---------------------"
echo "---------------------"
echo "DIR_SOIL : " $DIR_SOIL

# TIFS=($TIF_BD $TIF_CF $TIF_ORGANICNSTOCK)
TIFS=$(find $DIR_SOIL -type f -name "*.tif" -not -name "af250m_nutrient_n_m_agg30cm*.*" 2> /dev/null)
for i in ${TIFS[@]};
do
	echo "---------------------"
	ls $i
	echo "assign EPSG:4326..."
	gdal_edit.py -a_srs "+proj=laea +lat_0=5 +lon_0=20 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs" $i
	echo "convert to netcdf..."
	gdal_translate -ot float32 -of netcdf -co COMPRESS=NONE -projwin -3933255.963213522 1318901.0993628108 -3687739.8486090107 1083803.2256698813 $i $i".nc"
	ls $i".nc"
done

# -3933255.963213522 1318901.0993628108 -3687739.8486090107 1083803.2256698813
echo "---------------------"
ls $DIR_SOIL/af250m_nutrient_n_m_agg30cm.tif
echo "assign EPSG:4326..."
gdal_edit.py -a_srs EPSG:4326 $DIR_SOIL/af250m_nutrient_n_m_agg30cm.tif
echo "reproject..."
gdalwarp -s_srs EPSG:4326 -t_srs "+proj=laea +lat_0=5 +lon_0=20 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs" -r average -of GTiff -co COMPRESS=NONE -co BIGTIFF=IF_NEEDED -overwrite $DIR_SOIL/af250m_nutrient_n_m_agg30cm.tif $DIR_SOIL/af250m_nutrient_n_m_agg30cm_prj.tif
echo "convert to netcdf..."
gdal_translate -ot float32 -of netCDF -co COMPRESS=NONE -projwin -3933255.963213522 1318901.0993628108 -3687739.8486090107 1083803.2256698813 $DIR_SOIL/af250m_nutrient_n_m_agg30cm_prj.tif $DIR_SOIL/af250m_nutrient_n_m_agg30cm_prj.tif.nc
ls $DIR_SOIL/af250m_nutrient_n_m_agg30cm_prj.tif.nc

echo "---------------------"
echo "---------------------"
echo "DIR_LAND : " $DIR_LAND
ls $DIR_LAND/$TIF_LAND
echo "assign EPSG:4326..."
gdal_edit.py -a_srs EPSG:4326 $DIR_LAND/$TIF_LAND
echo "reproject..."
TIF_NEW=$(basename -s .tif $DIR_LAND/$TIF_LAND )"_prj.tif"
echo "TIF_NEW : $TIF_NEW"
gdalwarp -s_srs EPSG:4326 -t_srs "+proj=laea +lat_0=5 +lon_0=20 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs" -r average -of GTiff -co COMPRESS=NONE -co BIGTIFF=IF_NEEDED -overwrite $DIR_LAND/$TIF_LAND $DIR_LAND/$TIF_NEW
echo "convert to netcdf..."
gdal_translate -ot float32 -of netCDF -co COMPRESS=NONE -projwin -3933255.963213522 1318901.0993628108 -3687739.8486090107 1083803.2256698813 $DIR_LAND/$TIF_NEW $DIR_LAND/$TIF_NEW".nc"
ls $DIR_LAND/$TIF_NEW".nc"
