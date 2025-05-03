from os.path import join
import sys
from numba import njit, prange
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask


@njit(parallel=True)
def jacobi_numba_jit(u, interior_mask,max_iter,atol=1e-6):
    #check if it stored row-wise or column-wise
    #print("strides to check how it is stored", u.strides)

    for i in range(max_iter):
        delta=0
        u_copy=np.copy(u)
        for j in prange(1,u.shape[0]-1):
            for k in range(1,u.shape[1]-1):
                if interior_mask[j-1][k-1]==True:
                    u_new = 0.25*(u[j+1][k] + u[j-1][k] + u[j][k-1] + u[j][k+1])
                    delta = max(delta,np.abs(u[j][k]-u_new))
                    u_copy[j][k]=u_new

        u=u_copy

        if delta<atol:
            break

    return u


def summary_stats(u, interior_mask):
    u_interior = u[1:-1, 1:-1][interior_mask]
    mean_temp = u_interior.mean()
    std_temp = u_interior.std()
    pct_above_18 = np.sum(u_interior > 18) / u_interior.size * 100
    pct_below_15 = np.sum(u_interior < 15) / u_interior.size * 100
    return {
        'mean_temp': mean_temp,
        'std_temp': std_temp,
        'pct_above_18': pct_above_18,
        'pct_below_15': pct_below_15,
    }


if __name__ == '__main__':
    # Load data
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

    if len(sys.argv) < 2:
        N = 1
    else:
        N = int(sys.argv[1])
    
    building_ids = building_ids[:N]

    # Load floor plans
    all_u0 = np.empty((N, 514, 514))
    all_interior_mask = np.empty((N, 512, 512), dtype='bool')
    for i, bid in enumerate(building_ids):
        u0, interior_mask = load_data(LOAD_DIR, bid)
        all_u0[i] = u0
        all_interior_mask[i] = interior_mask

    # Run jacobi iterations for each floor plan
    MAX_ITER = 20_000
    ABS_TOL = 1e-4
    
    #initial call for it to compile
    jacobi_numba_jit(all_u0[0], all_interior_mask[0], MAX_ITER, ABS_TOL)

    all_u = np.empty_like(all_u0)
    for i, (u0, interior_mask) in enumerate(zip(all_u0, all_interior_mask)):
        u = jacobi_numba_jit(u0, interior_mask, MAX_ITER, ABS_TOL)
        all_u[i] = u
        
    # Print summary statistics in CSV format
    data = []
    stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
    #print('building_id, ' + ', '.join(stat_keys))  # CSV header
    for bid, u, interior_mask in zip(building_ids, all_u, all_interior_mask):
        point_values = [float(bid)]
        
        stats = summary_stats(u, interior_mask)
        for k in stat_keys:
            point_values.append(float(stats[k]))

        data.append(point_values)

        
    df = pd.DataFrame(data, columns = ['building_id', 'mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15'])
    print(df.mean())

    buildings_above_18_50 = df[df['pct_above_18'] > 50].shape[0]
    buildings_below_15_50 = df[df['pct_below_15'] > 50].shape[0]

    print("buildings_above_18_50%", buildings_above_18_50)
    print("buildings_below_15_50%", buildings_below_15_50)

    h = df['mean_temp'].hist(color='lightseagreen')
    h.set_xlabel("Temperature")
    h.set_ylabel("Number of occurences")
    h.set_title("Distribution of mean temperature")
    
    plt.savefig("histogram.png")

   

    
