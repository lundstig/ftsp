from simulation import simulate


SIMULATION_MINUTES = 10
results = simulate(n=10, simulation_length=60 * SIMULATION_MINUTES)
for stat_point in results:
    print(stat_point)
