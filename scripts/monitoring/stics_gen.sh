#!/usr/bin/env bash
JOBID=$1
echo "job : $JOBID"
IT=($(cat slurm-${JOBID}.out | grep -o "Iteration"))
D=($(cat slurm-${JOBID}.out | grep -o "done"))
wait
cat "slurm-$JOBID.out" | grep "number of"
echo "Iteration : "${#IT[@]}
echo "Done : "${#D[@]};
