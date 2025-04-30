#!/bin/bash
#BSUB -J CuPy_optimized_Simulation_time
#BSUB -q gpuv100
### -- ask for number of cores (default: 1) --
#BSUB -n 8
#BSUB -R "span[hosts=1]" 
### -- set walltime limit: hh:mm --
#BSUB -W 00:15
### -- specify that we need 4GB of memory per core/slot -- 
#BSUB -R "rusage[mem=4GB]"
#BSUB -gpu "num=1:mode=exclusive_process" 
#BSUB -R "select[gpu32gb]"
#BSUB -o CuPy_optimized_Simulation_time_%J.out
#BSUB -e CuPy_optimized_Simulation_time_%J.err
#BSUB -u s204696@dtu.dk
### -- send notification at start --
#BSUB -B
### -- send notification at completion--
#BSUB -N

# Initialize conda enviroment
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

lscpu # Print info about CPU

time python CuPy_simulation_optimized.py 20

