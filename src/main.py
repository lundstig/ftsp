from simulation import simulate
import analyze


SIMULATION_MINUTES = 10
result = simulate(
    n=5,
    connect_closest=5,
    delay_mean=1,
    delay_sigma=0,
    offset_sigma=10,
    skew_sigma=1e-2,
    simulation_length=60 * SIMULATION_MINUTES,
    debug_print=True
)
analyze.plot_single_run(result, "../img/test.pdf")
