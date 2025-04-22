#!/bin/bash
#BSUB -J CuPy_nsys
#BSUB -q c02613
### -- ask for number of cores (default: 1) --
#BSUB -n 4
#BSUB -R "span[hosts=1]" 
### -- set walltime limit: hh:mm --
#BSUB -W 00:15
### -- specify that we need 1GB of memory per core/slot -- 
#BSUB -R "rusage[mem=1GB]"
#BSUB -gpu "num=1:mode=exclusive_process" 
#BSUB -o CuPy_nsys_%J.out
#BSUB -e CuPy_nsys_%J.err
#BSUB -u s204696@dtu.dk
### -- send notification at start --
#BSUB -B
### -- send notification at completion--
#BSUB -N

# Initialize conda enviroment
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

lscpu # Print info about CPU

nsys profile -o CuPy_simulation python CuPy_simulation.py 20




