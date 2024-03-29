# A workflow for HPC crop simulations (STIC, DSSAT, CELSIUS) using Datamill database

Imperial College provides research computing resources for all College researchers, with the standard service for these being free at the point of use.
You must be registered in order to access the HPC service. The steps for registration are described [here](https://www.imperial.ac.uk/admin-services/ict/self-service/research-support/rcs/get-access/) 

## 1 - Prerequists for Windows OS users to connect to the HPC

For Windows users, the interactions with the Imperial College Computing platform can be made with :
-  _Putty_ software (https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html) to connect to the computing platform
-  _Winscp_ software (https://winscp.net/eng/download.php) to perform the files transfer to the computing platform

These softwares must be installed on the local computer.

A VPN must also be set up to secure the connection : https://www.imperial.ac.uk/admin-services/ict/self-service/connect-communicate/remote-access/virtual-private-network-vpn/  



### Connection to the computing platform

 <img src="images/Scr2_PuTTY_free-download.webp" alt="logo" width="500" align="center" />

 Once Putty software is installed, in the frame 'Host Name (or IP adress)', the domain adress and username must be indicated :

 `user@login.hpc.ic.ac.uk` (replace 'user' by your username), and the connection type must be set on `SSH`. Then click on `Òpen`and type your password.

A terminal appears when the connection is realized. Please note that no graphic interface is provided so the Linux command lines are used.  


### Transfer of files to and from the computing platform

 <img src="images/Winscp-connect.png" alt="logo" width="500" align="center" />

Once Winscp software is installed, open it and in the frame `Host name`, type the domain adress `login.hpc.ic.ac.uk`, and the password and username in the appropriate frames. In file protocol, choose 'SFTP', then click on 'Login' and a double window appears with on the right the file system of the remote computing platform, and on the left, the local file system :


 <img src="images/WinSCP-transfer.jpeg" alt="logo" width="500" align="center" />

In each of the windows, choose the appropriate directories and to transfer a file from a machine to the other, you have to select and drag the file(s).

## 2 - File system

The example directory is located on Imperial college cluster at the adress /rds/general/project/arise/live/CropModellingArise.  

The required subdirectories to launch execution are :
  
`/data` includes input data of DEM, land, grid, soil and Stics files such as ficplt1.txt   
`/db` includes the MasterInput.db databases with ModelsDictonaryArise.db and the Celsius databasis CelsiusV3nov17_dataArise.db  
`/scripts` list of the scripts called by the main script `main.sh`

On Imperial College, the PBS job scheduler is used, so a launching script `datamill.pbs` must be provided with the container file `datamill.sif` (these files must be located in the folder that contains the subdirectories data, db and scripts).


## 3 - Overview of the implementation of the main file


The launch of the workflow on further nodes is performed with the PBS script `datamill.pbs` which uses a Singularity container `datamill.sif`.

The PBS `datamill.pbs` file is the following :

```
#!/bin/bash
  
#PBS -J 0-87:1
#PBS -S /bin/bash
#PBS -lselect=1:ncpus=48:mem=64gb
#PBS -lwalltime=20:00:00
#PBS -N DATAMILL
#PBS -V

cd $PBS_O_WORKDIR

date

singularity exec --no-home -B /rds/general/user/`$user`/ephemeral/CropModellingArise:/work -B /rds/general/user/`$user`/ephemeral/tmp:$TMPDIR datamill.sif /work/scripts/main.sh


date
```

The first lines starting by `#PBS` allow to set up the size of the array jobs, the number of CPUs per node, the maximum time for the jobs and the job name.

Then for each job, it triggers a running container `datamill.sif` in the host directory  `/rds/general/user/`$user`/ephemeral/CropModellingArise` with an local directory name `work` (the directory name in the image). 
The container `datamill.sif` calls the main script `main.sh`, triggering the steps of the workflow. 

This `main.sh` script triggers the following actions. All the scripts called in  `main.sh` are located in the subdirectory `scripts`.

Here, we described the main instructions in `main.sh` script that will be execute to address the model simulations.

**3.1. Create subdirectories 'EXPS' and copy of MasterInput, this step must lead to `n` directories 'EXP_k' (k: 0..n-1 with n the length of the jobs arrray). In this configuration n = 88 :**

```
python3 ${DATAMILL_WORK}/scripts/workflow/init_dirs.py --index $i;
  wait
```

**3.2. Load Soil data in MasterInput database in each EXP_k folder:**

```  
  python3 ${DATAMILL_WORK}/scripts/netcdf/soil_to_db.py --index $i;
  wait 
```

**3.3. Load climate data  in each MasterInput according to the selected pixels of each job  :**

```
python3 ${DATAMILL_WORK}/scripts/netcdf/meteo_to_db.py --index $i;
wait
```

**3.4. Load DEM data in each MasterInput :**

```
  python3 ${DATAMILL_WORK}/scripts/netcdf/dem_to_db.py --index $i;
  wait
```

**3.5. Create simunitlist with global parameters of the simulation : soil, dates, ITK :**
```
  python3 ${DATAMILL_WORK}/scripts/workflow/init_simunitlist.py --index $i;
  wait
```

**3.6. Run Celsius Model :**

```
  /work/scripts/workflow/celsius.sh
  wait

```

 **3.7. Run Stics model :**

```
  /work/scripts/workflow/stics.sh
  wait

```

 **3.8. Run Dssat model :**

 ```
  /work/scripts/workflow/dssat.sh
  wait

```


## 4 - Launching the workflow on a HPC computer


  **After connecting to the HPC through WINSCP, copy the `CropModellingArise repository` from `/rds/general/project/arise/live` to /rds/general/user/`$user`/ephemeral/`   Replace `$user` by your username**
  
  **Create into /rds/general/user/`$user`/ephemeral/ the temporary folder `tmp`**

  **Open and modify the username in the `datamill.pbs` and `merge.pbs` files  in order to have the right path to access `tmp` and `CropModellingArise`. In the current files, the username is `cmidingo`**

  **After connecting with Putty, write (modify `$user` with `your user name` ):**

```
  cd  /rds/general/user/`$user`/ephemeral/CropModellingArise
```

  **The job `datamill.pbs` can be launched to trigger the workflow with the command :**

```
  qsub datamill.pbs
```


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

  **After each execution, remove all `DATAMILL.o*.*` and `DATAMILL.e*.*`files** generated in the working repository

  **Launch merge.pbs job**
  
  After launching the job for all models and management practices, it requires to launch `merged.pbs` that allows to merge all the results from each model with different simulation options and management practices.
  The combined results are saved in `outputs` folder.


!!!Attention: 

Please save your repository on your local computer

Do not store sensitive or personally-identifiable data in Ephemeral.

Data within $RDS/ephemeral/ is unquotaed but will be DELETED 30 DAYS AFTER CREATION.



## 5 - Verification between Datamill windows and Cluster

  To ensure the equivalence of the results between DataMill Windows and Cluster, a test dataset has been provided and is located in the `test` folder. Therefore, a directory named `CropModellingAriseTest` has been created in the cluster, which contains the code to perform the tests with this dataset.
  
  ### Verification process

   - Launch `datamill.pbs` in the cluster from the CropModellingAriseTest repository. Please, follow the instructions in `section 4`. (The repository is now CropModellingAriseTest instead of CropModellingArise)
   - Create in your computer a folder `e.g: RESULT` where you copy the `MasterInput.db` in the `EXPS\exp_1`folder.
   - Convert the `MasterInput.db` into access format using the function `convert_sqlite_to_access` in `script\fucntions\sqlite_to_access.py`. The result will be `MasterInput.mdb`. Please, change the format in `accdb`
   - Please duplicate the MasterInput.accdb and named them MasterInput.accdb and `MasterInput_clust.accdb`.
   - Empty the `SummaryOutput` table in MasterInput.accdb
   - Empty Dweather, OutputSynt, Soil, ListPAnnexes, SimunitList, SummaryOutput tables in CelsiusV3nov17_dataArise.accdb
   - Launch Datamill windows and run the three models. Please use the ModelDictionnay.accdb, CelsiusV3nov17_dataArise.accdb, maiplt.txt, stics_modulo.exe provided in `test folder` in this github repositoory. The version of dssat is 4.7 and use the cultivar file in `data\dssat\genotype`
   - Rename masterInput as `MasterInput_win.accdb`
   - At the end, call  `compare_results` function in `scripts\functions\compare_clust_win.py`. It takes as inputs the path of `MasterInput_clust.accdb` and `MasterInput_win.accdb`
   - The result should be [as this](test/plot.pdf)

!!!Attention: mAke sure that in the path of your directory or file there is no space (no space in the name of folder)
