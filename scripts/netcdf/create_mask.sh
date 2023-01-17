#!/usr/bin/env bash

#CLIM_INPUT_DIR=./TNZ2010
#SHP=./TZAwaterProvinces.shp
  
GRID_SHORT="grid"
GRID_TXT=$MASK_OUTPUT_DIR/$GRID_SHORT".txt"

MASK_SHORT="mask_IRC"
MASK_NC=$MASK_OUTPUT_DIR/$MASK_SHORT".nc"
MASK_TIF=$MASK_OUTPUT_DIR/$MASK_SHORT".tif"
MASK_TMP=$MASK_OUTPUT_DIR/$MASK_SHORT"_tmp.nc"

#CROP_MASK_SHORT="ANNUAL_AREA_HARVESTED_IRC_CROP2_HA"
CROP_MASK_ASC=$CROP_MASK_SHORT".ASC"
CROP_MASK_NC=$CROP_MASK_SHORT".nc"
CROP_MASK_TMP=$CROP_MASK_SHORT"_tmp.nc"

echo "GRID_TXT : "$GRID_TXT
if [ -f $GRID_TXT ]; then
  echo "$GRID_TXT already exists, moving to "$GRID_TXT".bak" 
  mv $GRID_TXT ${GRID_TXT}".BAK"
fi
echo "MASK_NC : "$MASK_NC
if [ -f $MASK_NC ]; then
  echo "$MASK_NC already exists, moving to "$MASK_NC".bak" 
  mv $MASK_NC ${MASK_NC}".BAK"
fi
echo "MASK_TIF : "$MASK_TIF
if [ -f $MASK_TIF ]; then
  echo "$MASK_TIF already exists, moving to "$MASK_TIF".bak" 
  mv $MASK_TIF ${MASK_TIF}".BAK"
fi
echo "MASK_TMP : "$MASK_TMP
if [ -f $MASK_TMP ]; then
  echo "$MASK_TMP already exists, moving to "$MASK_TMP".bak" 
  mv $MASK_TMP ${MASK_TMP}".BAK"
fi
echo "CROP_MASK_NC : "$CROP_MASK_NC
if [ -f $CROP_MASK_NC ]; then
  echo "$CROP_MASK_NC already exists, moving to "$CROP_MASK_NC".bak" 
  mv $CROP_MASK_NC ${CROP_MASK_NC}".BAK"
fi
echo "SHP : "$SHP
BBOX=($(ogrinfo -so -al ${SHP} | grep Extent | grep -P '[-]*\d+[.]*\d+' -o))
echo "BBOX : "${BBOX[@]}
SRS=$(ogrinfo -so -al TZAwaterProvinces.shp | awk '/[\[]/,/[\]]/'| tr -d '\n' | sed 's/ //g')
echo "SRS : "$SRS

echo "CLIM_INPUT_DIR : "$CLIM_INPUT_DIR
FILES=($(find ${CLIM_INPUT_DIR} -type f -maxdepth 1 -name "*.nc"))
echo "FILES : "${FILES[@]}
F=${FILES[0]} 
echo "F : "$F 

echo "* create an empty mask"
cdo -P $THREADS -sellonlatbox,${BBOX[0]},${BBOX[2]},${BBOX[1]},${BBOX[3]} -seltimestep,1 $F $MASK_TMP

echo "* generate the grid definition file"
cdo -P $THREADS -griddes $MASK_TMP > $GRID_TXT
wait
GRID_XSIZE=$(cat ${GRID_TXT} | grep xsize | grep -P '\d+' -o)
GRID_YSIZE=$(cat ${GRID_TXT} | grep ysize | grep -P '\d+' -o)
echo "GRID_XSIZE : $GRID_XSIZE"
echo "GRID_YSIZE : $GRID_YSIZE"

echo "* translate to geotif"
gdal_translate $MASK_TMP $MASK_TIF

echo "* burn the shape file into the raster (values==1)"
# -where "watprovID=31"
gdal_rasterize -ts $GRID_XSIZE $GRID_YSIZE -init 0 -burn 1 -at $SHP $MASK_TIF

echo "* translate to netcdf"
gdal_translate -of netCDF $MASK_TIF $MASK_NC

echo "* regrid the mask"
cdo -P $THREADS -setmissval,0 -gtc,0 -remapcon,$GRID_TXT $MASK_NC $MASK_TMP

echo "* create a temporary crop mask"
gdal_translate -of netcdf $CROP_MASK_ASC $CROP_MASK_TMP

echo "* regrid the temporary crop mask"
cdo -P $THREADS -remapcon,$GRID_TXT -setmissval,0 -gtc,0 -sellonlatbox,${BBOX[0]},${BBOX[2]},${BBOX[1]},${BBOX[3]} $CROP_MASK_TMP $CROP_MASK_NC

echo "* generate the final mask"
cdo -P $THREADS -setmissval,0 -mul $CROP_MASK_NC $MASK_TMP $MASK_NC

echo "ncdump -h $MASK_NC"
ncdump -h $MASK_NC

echo "done!"