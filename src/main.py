from simulation import simulate


SIMULATION_MINUTES = 10
results = simulate(n=10, simulation_length=60 * SIMULATION_MINUTES)
print(results)
