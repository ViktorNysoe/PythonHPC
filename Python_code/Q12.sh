#!/bin/bash
#BSUB -J Q12
#BSUB -q hpc
#BSUB -W 12:00
#BSUB -o Q12%J.out
#BSUB -e Q12%J.err
#BSUB -n 8
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=4GB]"
#BSUB -R "select[model == XeonGold6126]"

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

python Q12.py 4571