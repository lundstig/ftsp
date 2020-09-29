import numpy as np
import matplotlib.pyplot as plt

def calc_mean_maximum(d):
    mean = np.mean(d, axis=1)
    maximum = np.max(d, axis=1)
    return mean, maximum

means = []
maxs = []
path = "fake_data"
for i in range(1, 10):
    filename = f"{path}/{i}.npy"
    d = np.load(filename)
    mean, maximum = calc_mean_maximum(d)
    means.append(mean[-1])
    maxs.append(maximum[-1])
    scatter_x = np.array([[i] * d.shape[1] for i in range(0, d.shape[0])]).flatten()
    # plt.scatter(scatter_x, d.flatten(), s=2, c="#333")
    # plt.plot(mean, '-', linewidth=1, label=f"{(i)*10}% network degradation")
# plt.legend()
    # plt.show()

plt.plot(means, label="Avg. sync error")
plt.plot(maxs, label="Max. sync error")
plt.ylabel("ms")
plt.xlabel("Network degradation")
plt.xticks(np.arange(0, 9), labels=[str((i+1)*10) + "%" for i in range(9)])
plt.legend()
plt.show()
