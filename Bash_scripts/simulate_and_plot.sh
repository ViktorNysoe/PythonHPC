#!/bin/bash
#BSUB -J simulate_and_plot_5
#BSUB -q hpc
#BSUB -W 10
#BSUB -o simulate_and_plot_5%J.out
#BSUB -e simulate_and_plot_5%J.err
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=2GB]"
#BSUB -R "select[model == XeonGold6126]"

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

python simulate_and_plot.py 10