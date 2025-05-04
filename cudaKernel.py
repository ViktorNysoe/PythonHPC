import sys
from os.path import join
import numpy as np
from numba import cuda

### How to run this script:
# python cudaKernel.py <N> <LOAD_DIR>
# where <N> is the number of buildings to process and <LOAD_DIR> is the directory containing the data files.

def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))  # padded grid
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask

@cuda.jit
def jacobi_kernel(u, u_new, interior_mask):
    i, j = cuda.grid(2)
    if 1 <= i < u.shape[0] - 1 and 1 <= j < u.shape[1] - 1:
        if interior_mask[i - 1, j - 1]:  # mask is 512x512
            u_new[i, j] = 0.25 * (
                u[i - 1, j] + u[i + 1, j] + u[i, j - 1] + u[i, j + 1]
            )

def jacobi_cuda(u_host, interior_mask_host, max_iter=10000):
    # Allocate GPU memory
    u_dev = cuda.to_device(u_host)
    u_new_dev = cuda.device_array_like(u_host)
    interior_mask_dev = cuda.to_device(interior_mask_host)

    threads_per_block = (16, 16)
    blocks_per_grid_x = (u_host.shape[0] + threads_per_block[0] - 1) // threads_per_block[0]
    blocks_per_grid_y = (u_host.shape[1] + threads_per_block[1] - 1) // threads_per_block[1]
    blocks_per_grid = (blocks_per_grid_x, blocks_per_grid_y)

    for _ in range(max_iter):
        jacobi_kernel[blocks_per_grid, threads_per_block](u_dev, u_new_dev, interior_mask_dev)
        u_dev, u_new_dev = u_new_dev, u_dev  # swap buffers

    return u_dev.copy_to_host()

if __name__ == '__main__':
    N = int(sys.argv[1])
    LOAD_DIR = sys.argv[2]

    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

    building_ids = building_ids[:N]
    all_u0 = np.empty((N, 514, 514))
    all_interior_mask = np.empty((N, 512, 512), dtype='bool')

    for i, bid in enumerate(building_ids):
        u0, interior_mask = load_data(LOAD_DIR, bid)
        all_u0[i] = u0
        all_interior_mask[i] = interior_mask

    MAX_ITER = 20000
    all_u = np.empty_like(all_u0)

    for i in range(N):
        u = jacobi_cuda(all_u0[i], all_interior_mask[i], MAX_ITER)
        all_u[i] = u
