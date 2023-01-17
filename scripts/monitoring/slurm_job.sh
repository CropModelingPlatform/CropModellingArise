#!/usr/bin/env bash
JS=($(ls /home/robaldog/scratch/slurm-*.out))
for J in ${JS[@]};
do
 echo "******************************************"
 echo $J
 echo "******************************************"
 head $J
 echo "[...]"
 echo ""
 F=$(basename $J)
 # echo $F
 I=$(echo $F | cut -c7-13)
 # echo $I
 sacct -j $I --format=JobID,JobName,MaxRSS,Elapsed
 echo ""
done
