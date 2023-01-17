#!/usr/bin/env bash
THREADS=$1
WAIT=1 #second
echo "available CPUs : $(nproc)"
echo "THREADS : $THREADS"
echo "WAIT : $WAIT"
seq 10 | xargs -n1 -P$THREADS -I{} bash -c "echo {};sleep $WAIT"
NODES=3
N=$(($NODES*$THREADS))
echo $N