from os.path import join
import numpy as np
import matplotlib.pyplot as plt

def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask

# Settings
LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
building_ids = []
with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
    building_ids = f.read().splitlines()

# Choosing a subset of buildings to load
# 5 might be a good number?  
subset_buildings = building_ids[:5]  # Load first 5

for bid in subset_buildings:
    u, interior_mask = load_data(LOAD_DIR, bid)

    # Plot domain temperature
    plt.figure(figsize=(6, 5))
    plt.imshow(u[1:-1, 1:-1], cmap='coolwarm')
    plt.colorbar(label='Initial Temperature')
    plt.title(f"Initial temperature distribution - {bid}")
    plt.savefig(f"{bid}_domain.png")
    plt.close()

    # Plot interior mask
    plt.figure(figsize=(6, 5))
    plt.imshow(interior_mask, cmap='Greys')
    plt.title(f"Interior mask - {bid}")
    plt.savefig(f"{bid}_interior_mask.png")
    plt.close()
