#!/bin/bash
#BSUB -J gpujob
#BSUB -q gpuv100
#BSUB -W 00:30
#BSUB -n 8
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=4GB]"
#BSUB -R "select[gpu32gb]"
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -o batch_output/gpujob_%J.out
#BSUB -e batch_output/gpujob_%J.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

time python cudaKernel.py 20 /dtu/projects/02613_2025/data/modified_swiss_dwellings