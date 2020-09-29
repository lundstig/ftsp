import numpy as np
from numpy.random import randn
from pathlib import Path

def gen_normal(n, mean, sigma):
    return mean + randn(n) * sigma

def gen_sync_error(hops, hop_time, sigma):
    def for_hop_dist(i):
        if i == 0:
            return [0]
        else:
            return np.maximum(0, gen_normal(i ** 2, i * hop_time, sigma * np.sqrt(i)))

    return np.concatenate([for_hop_dist(i) for i in range(hops + 1)])

def gen_fake_data(mean_multiplier):
    NUM_HOPS = 4
    T_MAX = 20
    def mean(t):
        return 1 / np.log(1 + t) * mean_multiplier
    def sigma(t):
        return mean(t) * 0.2
    return np.stack([gen_sync_error(NUM_HOPS, mean(t), sigma(t)) for t in range(1, T_MAX + 1)])

path = "fake_data"
Path(path).mkdir(parents=True, exist_ok=True)
for i in range(0, 10):
    d = gen_fake_data((i + 1) ** 1.5 * 0.005)
    filename = f"{path}/{i}"
    np.save(filename, d)
    print(f"Created {filename}")
