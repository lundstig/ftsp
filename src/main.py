from simulation import simulate
import analyze


SIMULATION_MINUTES = 30
result = simulate(
    n=30,
    connect_closest=10,
    delay_mean=1e-3,
    delay_sigma=0.5e-3,
    offset_sigma=1000,
    skew_sigma=1e-4,
    simulation_length=60 * SIMULATION_MINUTES,
    debug_print=False
)
analyze.plot_single_run(result, "../img/test.pdf")
