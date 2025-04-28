from os.path import join
import sys
from numba import jit, njit, prange
import numpy as np
import time
import matplotlib.pyplot as plt

def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask


def jacobi(u, interior_mask, max_iter, atol=1e-6):
    u = np.copy(u)

    for i in range(max_iter):
        # Compute average of left, right, up and down neighbors, see eq. (1)
        u_new = 0.25 * (u[1:-1, :-2] + u[1:-1, 2:] + u[:-2, 1:-1] + u[2:, 1:-1])
        u_new_interior = u_new[interior_mask]
        delta = np.abs(u[1:-1, 1:-1][interior_mask] - u_new_interior).max()
        u[1:-1, 1:-1][interior_mask] = u_new_interior

        if delta < atol:
            break
    return u

@jit(nopython=True)
def jacobi_numba_jit(u, interior_mask, max_iter, atol=1e-6):
    #check that it is stored row-wise
    print("strides to check how it is stored:", u.strides)
    
    u = np.copy(u)

    for _ in range(max_iter):
        delta = 0
        for j in range(1,u.shape[0]-1):
            for k in range(1,u.shape[1]-1):
                if interior_mask[j-1, k-1] == True:
                    u_new = 0.25 * (u[j+1,k] + u[j-1,k] + u[j, k+1] + u[j, k-1])
                    
                    
                    delta = max(delta, np.abs(u[j,k]-u_new))
                    u[j][k] = u_new
        if delta < atol:
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
    start_time = time.time()
    for i, (u0, interior_mask) in enumerate(zip(all_u0, all_interior_mask)):
        u = jacobi_numba_jit(u0, interior_mask, MAX_ITER, ABS_TOL)
        all_u[i] = u
        plt.imshow(u, cmap='magma', interpolation='nearest')
    plt.savefig("heat_maps.png")
    end_time = time.time()-start_time
    print("iterator call: ", end_time)

    total_time = int(end_time)/20*4571
    total_time = total_time/3600
    dec = total_time % 1
    total_hours = int(total_time)
    total_minutes = int(dec * 60)
    
    
    print("Total time for all floorplans: ", total_hours, "hours and ", total_minutes, "minutes")
