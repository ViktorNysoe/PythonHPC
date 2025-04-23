#!/bin/bash
#BSUB -J load_and_plot
#BSUB -q hpc
### -- ask for number of cores (default: 1) --
#BSUB -n 8
#BSUB -R "span[hosts=1]" 
### -- set walltime limit: hh:mm --
#BSUB -W 00:30
### -- specify that we need 4GB of memory per core/slot -- 
#BSUB -R "rusage[mem=4GB]"
### -- Specify CPU type --
#BSUB -R "select[model==XeonGold6126]"
#BSUB -o load_and_plot_%J.out
#BSUB -e load_and_plot_%J.err
#BSUB -u s204696@dtu.dk
### -- send notification at start --
#BSUB -B
### -- send notification at completion--
#BSUB -N

# Initialize conda enviroment
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

lscpu # Print info about CPU

# Run python script
python  load_and_plot.py