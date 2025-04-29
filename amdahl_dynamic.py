import os
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool, cpu_count
from os.path import join

def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask

def jacobi(u, interior_mask, max_iter, atol=1e-6):
    u = np.copy(u)
    for _ in range(max_iter):
        u_new = 0.25 * (u[1:-1, :-2] + u[1:-1, 2:] + u[:-2, 1:-1] + u[2:, 1:-1])
        u_new_interior = u_new[interior_mask]
        delta = np.abs(u[1:-1, 1:-1][interior_mask] - u_new_interior).max()
        u[1:-1, 1:-1][interior_mask] = u_new_interior
        if delta < atol:
            break
    return u

def summary_stats(u, interior_mask):
    u_interior = u[1:-1, 1:-1][interior_mask]
    return {
        'mean_temp': u_interior.mean(),
        'std_temp': u_interior.std(),
        'pct_above_18': np.sum(u_interior > 18) / u_interior.size * 100,
        'pct_below_15': np.sum(u_interior < 15) / u_interior.size * 100,
    }

def process_building(bid):
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
    u0, interior_mask = load_data(LOAD_DIR, bid)
    MAX_ITER = 20_000
    ABS_TOL = 1e-4
    u = jacobi(u0, interior_mask, MAX_ITER, ABS_TOL)
    stats = summary_stats(u, interior_mask)
    return bid, stats

def run_parallel(building_ids, num_workers):
    start = time.time()
    with Pool(processes=num_workers) as pool:
        results = list(pool.imap_unordered(process_building, building_ids, chunksize=1))
    end = time.time()
    return end - start, results

def plot_and_save_speedup(workers, times, filename="speedup_plot_dynamic.png"):
    baseline = times[0]
    speedups = [baseline / t for t in times]

    plt.figure(figsize=(8, 6))
    plt.plot(workers, speedups, marker='o')
    plt.xlabel("Number of Workers")
    plt.ylabel("Speed-up")
    plt.title("Speed-up vs Number of Workers (Dynamic Scheduling)")
    plt.grid(True)
    plt.savefig(filename)
    plt.close()
    print(f"[✓] Saved speed-up plot as {filename}")
    return speedups

def save_speedup_csv(workers, times, speedups, filename="speedup_data_dynamic.csv"):
    with open(filename, 'w') as f:
        f.write("workers,time_seconds,speedup\n")
        for w, t, s in zip(workers, times, speedups):
            f.write(f"{w},{t:.4f},{s:.4f}\n")
    print(f"[✓] Saved speed-up data to {filename}")

def estimate_amdahl(speedup, num_cores):
    P = (num_cores * (1 - 1 / speedup)) / (num_cores - 1)
    S_max = 1 / (1 - P)
    return P, S_max

def save_amdahl_analysis(parallel_fraction, max_speedup, achieved_speedup, num_cores, total_buildings, time_per_building, filename="amdahl_analysis_dynamic.txt"):
    with open(filename, 'w') as f:
        f.write("Amdahl's Law Analysis (Dynamic Scheduling)\n")
        f.write("==========================================\n")
        f.write(f"Estimated parallel fraction: {parallel_fraction:.4f} ({parallel_fraction*100:.2f}%)\n")
        f.write(f"Theoretical max speed-up: {max_speedup:.2f}\n")
        f.write(f"Max achieved speed-up: {achieved_speedup:.2f} with {num_cores} cores\n")
        est_time = (total_buildings * time_per_building) / achieved_speedup
        f.write(f"Estimated time to process all {total_buildings} floorplans with best parallel setup: {est_time:.2f} seconds\n")
    print(f"[✓] Saved Amdahl analysis to {filename}")

if __name__ == "__main__":
    # Load buildings
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
    with open(join(LOAD_DIR, 'building_ids.txt')) as f:
        all_ids = f.read().splitlines()

    N = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    building_ids = all_ids[:N]
    total_buildings = len(all_ids)

    max_workers = min(cpu_count(), N)
    worker_range = list(range(1, max_workers + 1))
    times = []

    print("[•] Measuring performance using dynamic scheduling...")
    for workers in worker_range:
        print(f"   → Running with {workers} worker(s)...")
        elapsed, results = run_parallel(building_ids, workers)
        times.append(elapsed)

    speedups = plot_and_save_speedup(worker_range, times)
    save_speedup_csv(worker_range, times, speedups)

    best_speedup = max(speedups)
    best_workers = worker_range[speedups.index(best_speedup)]
    parallel_fraction, theoretical_max = estimate_amdahl(best_speedup, best_workers)
    save_amdahl_analysis(parallel_fraction, theoretical_max, best_speedup, best_workers, len(all_ids), times[0] / N)
