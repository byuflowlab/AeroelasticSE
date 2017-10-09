import numpy as np

results = np.loadtxt('airfoil_data.txt')

results = results[:,0:3]

np.savetxt('airfoil_data.txt', results)