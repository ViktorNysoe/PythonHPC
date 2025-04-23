#!/bin/bash
#BSUB -J simulate
#BSUB -q hpc
#BSUB -W 10
#BSUB -o simulate%J.out
#BSUB -e simulate%J.err
#BSUB -n 8
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=4GB]"
#BSUB -R "select[model == XeonGold6126]"

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

python Q11_parallel_jit.py 20
