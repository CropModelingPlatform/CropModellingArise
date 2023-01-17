#!/usr/bin/env bash

F=($(ls db/initial/Celsius*.csv))
for i in ${F[@]}; do
		echo $i
	  N=$(basename -s .csv $i)
	  echo $N
	  sqlite3 db/NEW/CelsiusV3nov17_dataArise.db "delete from $N"
	  sqlite3 -separator ';' db/NEW/CelsiusV3nov17_dataArise.db ".import $i $N"
done
