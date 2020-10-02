from typing import List

import numpy as np
import matplotlib.pyplot as plt

from simulation import StatPoint


def calc_mean_maximum_errors(stats: List[StatPoint]):
    mean = [np.mean(stat.prediction_error_ms) for stat in stats]
    maximum = [np.max(stat.prediction_error_ms) for stat in stats]
    return mean, maximum


def plot_single_run(stats: List[StatPoint], filename=None):
    mean, maximum = calc_mean_maximum_errors(stats)
    scatter_x = np.concatenate(
        [[stat.real_time] * len(stat.prediction_error_ms) for stat in stats]
    )
    scatter_y = np.concatenate([stat.prediction_error_ms for stat in stats])
    synced_nodes = [stat.synced_count for stat in stats]

    fig, ax1 = plt.subplots()
    plt.scatter(scatter_x, scatter_y, s=2, c="#333")
    ax1.set_xlabel("Simulation time (s)")
    ax1.set_ylabel("Time prediction error (ms)")
    ax1.plot(mean, "-", linewidth=1, label="Mean")

    ax2 = ax1.twinx()
    ax2.set_ylabel("Synced nodes")
    ax2.set_ylim(0, stats[0].total_nodes)
    ax2.plot(synced_nodes, "--", linewidth=1, label="Synced nodes")
    if filename:
        plt.savefig(filename, transparent=True)
    else:
        plt.show()
