# A workflow for HPC crop simulations (STIC, DSSAT, CELSIUS) using Datamill databasis


## 1 - Prerequists for Windows OS users

For Windows users, the interactions with the Imperial College Computing platform can be made with :
-  _Putty_ software (https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html) to connect to the computing platform
-  _Winscp_ software (https://winscp.net/eng/download.php) to perform the files transfer to the computing platform

These softwares must be installed on the local computer.

A VPN must also be set up to secure the connection : https://www.imperial.ac.uk/admin-services/ict/self-service/connect-communicate/remote-access/virtual-private-network-vpn/  



### Connection to the computing platform

 <img src="Scr2_PuTTY_free-download.webp" alt="logo" width="500" align="center" />

 Once Putty software is installed, in the frame 'Host Name (or IP adress)', the domain adress and username must be indicated :

 `user@login.hpc.ic.ac.uk` (replace 'user' by your username), and the connection type must be set on `SSH`. Then click on `Òpen`and type your password.

A terminal appears when the connection is realized. Please note that no graphic interface is provided so the Linx command lines are used.  


### Transfer of files to and from the computing platform

 <img src="Winscp-connect.png" alt="logo" width="500" align="center" />

Once Winscp software is installed, open it and in the frame `Host name`, type the the domain adress `login.hpc.ic.ac.uk`, and the password and username in the appropriate frames. In file protocol, choose 'scp', then click on 'Login' and a double window appears with on the right the file system of the remote computing platform, and on the left, the local file system :


 <img src="WinSCP-transfer.jpeg" alt="logo" width="500" align="center" />

In each of the windows, choose the appropriate directories and to transfer a file from a machine to the other, you juste have to select and drag the file(s).

## 2 - File system

The example directory set by Guillaume Robaldo is located on Imperial college cluster at the adress /rds/general/project/arise/live/CropModellingGR.  
To setup the necessary environment, the file `datamill.tar.gz` must be uncompressed in a given directory with the command `tar -xvf datamill.tar.gz`.

The subdirectories are :
  
`/data` includes input data of DEM, land, grid, soil ans Stics files such as ficplt1.txt   
`/db` includes the MasterInput.db databases with ModelsDictonaryArise.db and the Celsius databasis CelsiusV3nov17_dataArise.db  
`/scripts` list of the scripts called by the main script `main.sh`

On Imperial College, the PBS job scheduler is used, so a launching script `datamill.pbs` must be provide with the container file `datamill.sif` (these files must be located near to the subdirectories bin, data, db, scripts).


## 3 - Launching the workflow on a HPC computer

### Principle 

The launch of the workflow on further nodes is performed with the PBS script `datamill.pbs` which uses a Singularity container `datamill.sif`.

The PBS `datamill.pbs` file is the following :

```
#!/bin/bash
  
#PBS -J 0-49:1
#PBS -S /bin/bash
#PBS -lselect=1:ncpus=48:mem=64gb
#PBS -lwalltime=20:00:00
#PBS -N DATAMILL
#PBS -V

cd $PBS_O_WORKDIR

date

singularity exec --no-home -B $RDS/projects/arise/live/CropModelling:/work -B $RDS/projects/arise/live/CropModellingTmp:$TMPDIR datamill.sif /work/scripts/main.sh

date
```

The first lines starting by `#PBS` allow to set up the number of nodes, the number of CPUs per node, the maximum time for the jobs and the job name.
Then for each job, it triggers a running container `datamill.sif` in the host directory  `$RDS/projects/arise/live/CropModelling` with an local directory name `work` (the directory name in the image). The directory `$RDS/projects/arise/live/CropModellingTmp` is a temporary directory used by Singularity.
The container `datamill.sif` calls the main script `main.sh`, triggering the steps of the workflow. 

This `main.sh` script triggers the following actions, whose lines can be activated or commented (for example an inactivation can be necessary when the weather data are already loaded because this step is time consuming). The example below is given with Stics model :

**Copy of the STICS plants related files in all subdirectories :**

```
conf_stics (){
  cp "$DATAMILL_WORK/data/$STICS_PLANT" "$1/ficplt1.txt"
  wait
}
export -f conf_stics
```

**Create subdirectories 'EXPS' and copy of MasterInput, this step must lead to 50 directories 'EXPS' :**

```
python3 ${DATAMILL_WORK}/scripts/workflow/init_dirs.py --index $i;
  wait
```

**Load data in MasterInput database :**

```  
  python3 ${DATAMILL_WORK}/scripts/netcdf/soil_to_db.py --index $i;
  wait 
```

**Load meteorological data  in MasterInput - Higly time consuming, activate when necessary :**

```
python3 ${DATAMILL_WORK}/scripts/netcdf/meteo_to_db.py --index $i;
wait
```

**Load DEM data in MasterInput :**

```
  python3 ${DATAMILL_WORK}/scripts/netcdf/dem_to_db.py --index $i;
  wait
```

**Create simunitlist with global parameters of the simulation : soil, dates, ITK (ex: fert0, fert160...) :**
```
  python3 ${DATAMILL_WORK}/scripts/workflow/init_simunitlist.py --index $i;
  wait
```

**Stics files : 'datamill' is the compilated Visual Basic code, 1 subdirectory/simu is created. The 3 lines after create the name of the subdirectory 'lat-lon-years-ID-ITK' :**

```
  cd $DIR_EXP
  datamill convert -m stics \
    -t ${THREADS} \ 
    -dbMasterInput ${DB_MI} \
    -dbModelsDictionary ${DB_MD}
  wait
  ```

 **Run of Stics :**

 ```
  cd ${DATAMILL_WORK}/scripts
  ./stics-main.bash -v -k -i $DIR_EXP/Stics -t ${THREADS}
  cd ${DATAMILL_WORK}
  wait
  ```

**Indications of the variables to output (ex: LAI) :**
```
python3 ${DATAMILL_WORK}/scripts/netcdf/stics_to_netcdf.py --index $i;
  wait
 ```

In order to use this `main.sh` script for DSSAT model, replace words 'Stics' by 'Dssat' and launch the workflow with command line explained below. All the scripts used in  `main.sh` are located in the subdirectory `scripts`.


### Commands to launch the workflow

Before launching the PBS script, make sure that the `main.sh` script has a permission of execution. To do so, go in the /scripts directory and type the command :

```
chmod u+x main.sh
```

Then the script `datamill.pbs` can be launched to trigger the workflow with the command : 

```
qsub datamill.pbs
```

The launch of the script inserts the requested jobs in a queue while waiting for the availability of the computing ressources. With that experiment, a set of 50 nodes with 48 CPUs on each nodes is then requested. 

The state of the job can be checked with the command 

```
qstat -u $user
```
 Which returns :

```
 pbs: 
                                                            Req'd  Req'd   Elap
Job ID          Username Queue    Jobname    SessID NDS TSK Memory Time  S Time
--------------- -------- -------- ---------- ------ --- --- ------ ----- - -----
5303692[].pbs   mginer   v1_singl DATAMILL      --    1  48   64gb 20:00 Q   --  `

```

In this table :
- `Job ID` is the ID of the job,
- `username` is the name of the account from where the job has been launched
- `Queue` is the name of the queue where the user is allowed to reserv nodes
- `NDS`: number of nodes requested
- `TSK`: number of CPUs (tasks) requested per node
- `Reqd Memory`: maximum amount of memory requested for these jobs- 
- `Reqd Time`: time limit after wich the simulation is 
-  `S` : status of the job : (B) run for array jobs, (Q) in queue, etc ...
-  `Elap time`: elapsed time since the beginning of the simulation 

The simulation is running when the status is set on (B).

While the simulation is running, a set of files `DATAMILL.o*.*` are created with the output of each job (allowing to verify the step performed by the main.sh script), and a set of file `DATAMILL.e*.*` are created to display the errors during the workflow.

To kill a job, pick its ID with the `qstat -u $USER` command line, and type (ID of job is 5303692[].pbs in this example):

```
qdel 5303692[].pbs
```


