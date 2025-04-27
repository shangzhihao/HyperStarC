import numpy as np

rate = 10
shape, scale = 2., 1/rate
num_samples = 1000
gamma_random_numbers = np.random.gamma(shape, scale, num_samples)

np.savetxt("gamma_samples.txt", gamma_random_numbers)