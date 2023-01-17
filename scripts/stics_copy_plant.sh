#!/usr/bin/env bash
echo ${PWD}
STICS_PATH=${PWD}/DonneesFA/modelisation/Arise/datamillarise/applidatamill/Stics
USMS=($(find $STICS_PATH -type d))
echo "USMS : "${#USMS[@]}
for u in ${USMS[@]}; do
	echo $u
	cp ./data/ficplt1.txt $u/
done