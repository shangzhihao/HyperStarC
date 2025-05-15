import numpy as np

rate = 10
shape, scale = 2., 1/rate
num_samples = 1000
erlang1 = np.random.gamma(shape, scale, num_samples)

rate = 5
shape, scale = 10., 1/rate
num_samples = 1000
erlang2 = np.random.gamma(shape, scale, num_samples)

np.savetxt("her.txt", np.concat([erlang1, erlang2]))