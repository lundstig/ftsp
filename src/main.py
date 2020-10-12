from simulation import simulate
import analyze
import numpy as np


SIMULATION_MINUTES = 180
N = 50
CONNECT_CLOSEST = 10
OFFSET_SIGMA = 1000
SKEW_SIGMA = 1e-4

def run_test():
    result = simulate(
        n=100,
        connect_closest=10,
        delay_mean=1e-3,
        delay_sigma=0.35e-5,
        offset_sigma=1000,
        skew_sigma=1e-4,
        simulation_length=60 * SIMULATION_MINUTES,
        debug_print=False
    )
    analyze.plot_single_run(result, "../img/test.pdf")

def study_delay():
    delay_means_ms = np.arange(1e-4, 1e-3, 1e-4)
    final_errors = []
    xs = []
    for delay_mean_ms in delay_means_ms:
        delay_mean = delay_mean_ms
        delay_std = delay_mean / 10
        print("Delay: ", delay_mean, delay_std)
        result = simulate(
            n=N,
            connect_closest=CONNECT_CLOSEST,
            delay_mean=delay_mean_ms,
            delay_sigma=delay_std,
            offset_sigma=OFFSET_SIGMA,
            skew_sigma=SKEW_SIGMA,
            simulation_length=60 * SIMULATION_MINUTES,
        )
        analyze.plot_single_run(result, f"../img/delay_mean_ms{delay_mean_ms}.pdf")
        final_errors.append(result[-1].mean_error())
        xs.append(float(delay_mean))
    analyze.plot_error(final_errors, xs, "../img/varying_delay.pdf")
    make_table(xs, final_errors)

def study_drop():
    drop_rates = np.arange(0, 1.0, 0.1)
    final_errors = []
    for drop_rate in drop_rates:
        print("Drop-rate: ", drop_rate)
        result = simulate(
            n=N,
            connect_closest=CONNECT_CLOSEST,
            delay_mean=1e-3,
            delay_sigma=1e-4,
            offset_sigma=OFFSET_SIGMA,
            skew_sigma=SKEW_SIGMA,
            drop_rate=drop_rate,
            simulation_length=60 * SIMULATION_MINUTES,
        )
        analyze.plot_single_run(result, f"../img/drop_rate{round(drop_rate, 5)}.pdf")
        final_errors.append(result[-1].mean_error())
    analyze.plot_error(final_errors, drop_rates, "../img/varying_drop_rate.pdf")
    make_table(drop_rates, final_errors)

def make_table(xs, ys):
    for x, y in zip(xs, ys):
        print(round(x, 6), " & ", np.round(y, 6))


study_delay()
study_drop()
