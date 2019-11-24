import math
import random
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import random_correlation as rndcorr

exp_yield = 2
numMeas = np.random.randint(10, 50)
numPorts = np.random.randint(1, 6) * 4
meas_eigenvalue = np.random.random(numMeas)
meas_eigenvalue *= numMeas / np.sum(meas_eigenvalue)
meas_cov = rndcorr.rvs(meas_eigenvalue)

meas_noise = np.zeros((numMeas, numMeas))
port_noise = np.zeros(numPorts)

meas_noise = np.random.multivariate_normal(np.zeros(numMeas), meas_cov) / exp_yield

meas_dist = []
for i in range(0, numMeas):
    meas_dist.append(meas_noise[i] ** 2)

plt.plot(meas_dist)
plt.show()
