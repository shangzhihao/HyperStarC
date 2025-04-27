import numpy as np

rate = 10
scale_param = 1 / rate
exp_random_number = np.random.exponential(scale=scale_param)
num_samples = 1000
exp_random_numbers = np.random.exponential(scale=scale_param, size=num_samples)
np.savetxt("exp_samples.txt", exp_random_numbers)
