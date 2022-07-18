#!/bin/tcsh
#BSUB -n 11
#BSUB -W 72:00
#BSUB -R "rusage[mem=40GB]"
#BSUB -R "span[ptile=1]"
#BSUB -oo viewshed_out
#BSUB -eo viewshed_err
#BSUB -J viewshed


module use --append /usr/local/usrapps/gis/modulefiles/
module load grass
module load PrgEnv-intel

mpirun /home/akratoc/launch/launch /home/akratoc/continuous-viewscape-modeling/house_jobs_hpc.txt
