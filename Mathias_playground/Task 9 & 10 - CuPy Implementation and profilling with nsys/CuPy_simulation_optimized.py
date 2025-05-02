from os.path import join
import sys

import cupy as cp


def load_data(load_dir, bid):
    SIZE = 512
    u = cp.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = cp.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = cp.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask


jacobi_step = cp.ElementwiseKernel(
    # inputs: u[i-1,j], u[i+1,j], u[i,j-1], u[i,j+1], u_old[i,j], interior_mask
    'T u_im1j, T u_ip1j, T u_ijm1, T u_ijp1, T u_old_center, bool interior',
    # outputs: u_new_center, local_diff
    'T u_new_center, T local_diff',
    r'''
    // compute new center value
    T u_new = (u_im1j + u_ip1j + u_ijm1 + u_ijp1) * (T)0.25;
    if (interior) {
        // Update the new center value with the absolute difference which is the maximum of the two
        // values (u_new and u_old_center) subtracted by the minimum of the two values
        local_diff = u_new > u_old_center
                   ? u_new - u_old_center
                   : u_old_center - u_new;
        u_new_center = u_new;
    }
    else {
        local_diff = 0;
        u_new_center = u_old_center;
    }
    ''',
    name='jacobi_step'
)

def jacobi(u, interior_mask, max_iter, atol=1e-6):
    atol_gpu = cp.asarray(atol, dtype=u.dtype)

    for i in range(max_iter):
        # pull out neighbors and center
        u_im1j      = u[:-2, 1:-1]      # Up (i-1, j)
        u_ip1j      = u[2:,  1:-1]      # Down (i+1, j)
        u_ijm1      = u[1:-1, :-2]      # Left  (i, j-1)
        u_ijp1      = u[1:-1, 2:]       # Right  (i, j+1)
        u_old_center= u[1:-1, 1:-1]     # center (i, j)

        # call the combined jacobi step kernel
        u_new_center, local_diff = jacobi_step(
            u_im1j, u_ip1j, u_ijm1, u_ijp1, u_old_center, interior_mask
        )

        #update the interior of u
        u[1:-1, 1:-1] = u_new_center

        #find the maximum difference with the cp.max reduction
        delta = cp.max(local_diff)
        # early stopping
        if delta < atol_gpu:
            break

    return u

def summary_stats(u, interior_mask):
    u_interior = u[1:-1, 1:-1][interior_mask]
    mean_temp = u_interior.mean()
    std_temp = u_interior.std()
    pct_above_18 = cp.sum(u_interior > 18) / u_interior.size * 100
    pct_below_15 = cp.sum(u_interior < 15) / u_interior.size * 100
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
    all_u0 = cp.empty((N, 514, 514))
    all_interior_mask = cp.empty((N, 512, 512), dtype='bool')
    for i, bid in enumerate(building_ids):
        u0, interior_mask = load_data(LOAD_DIR, bid)
        all_u0[i] = u0
        all_interior_mask[i] = interior_mask

    # Run jacobi iterations for each floor plan
    MAX_ITER = 20_000
    ABS_TOL = 1e-4

    all_u = cp.empty_like(all_u0)
    for i, (u0, interior_mask) in enumerate(zip(all_u0, all_interior_mask)):
        u = jacobi(u0, interior_mask, MAX_ITER, ABS_TOL)
        all_u[i] = u

    # Print summary statistics in CSV format and store it 
    with open('all_floors.csv', 'w') as f:
        stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
        print('building_id, ' + ', '.join(stat_keys))  # CSV header
        f.write('building_id, ' + ', '.join(stat_keys) + '\n')
        for bid, u, interior_mask in zip(building_ids, all_u, all_interior_mask):
            stats = summary_stats(u, interior_mask)
            print(f"{bid},", ", ".join(str(stats[k]) for k in stat_keys))
            line = f"{bid}," + ", ".join(str(stats[k]) for k in stat_keys) + "\n"
            f.write(line)
