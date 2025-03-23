#!/bin/bash
#BSUB -J simulate
#BSUB -q hpc
### -- ask for number of cores (default: 1) --
#BSUB -n 4
#BSUB -R "span[hosts=1]" 
### -- set walltime limit: hh:mm --
#BSUB -W 00:30
### -- specify that we need 4GB of memory per core/slot -- 
#BSUB -R "rusage[mem=1GB]"
### -- Specify CPU type --
#BSUB -R "select[model==XeonGold6126]"
#BSUB -o simulate_%J.out
#BSUB -e simulate_%J.err
#BSUB -u s204696@dtu.dk
### -- send notification at start --
#BSUB -B
### -- send notification at completion--
#BSUB -N

# Initialize conda enviroment
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

lscpu # Print info about CPU

# Run python script and pass 20 as argument for the number of floorplans to simulate
# also time it in a loop and take the average of the time
time python simulate.py 20 # This will simulate 20 floorplans and take the average time it took to simulate using the time command
