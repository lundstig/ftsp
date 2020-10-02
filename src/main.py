from simulation import simulate
import analyze

SIMULATION_MINUTES = 1
result = simulate(n=30, simulation_length=60 * SIMULATION_MINUTES)
analyze.plot_single_run(result)
