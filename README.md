Repository for course 02613 Python and High Performance Computing. The repository contains code for the mini-project, due on March 4th.


**Standard CPU configuration for job scripts**  
    -n 8  
    -R "span[hosts=1]"  
    -R "rusage[mem=4GB]"  
    -R "select[model == XeonGold6126]"  

**Standard GPU queue for job scripts**  
    -q gpuv100  
    -R "select[gpu32gb]"  


