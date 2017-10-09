import numpy as np
import matplotlib.pyplot as plt

# with open('omdaoCase1.out') as f:
#     results = f.readlines()[9:]
#
# results = results.replace("\n", "")
# results = np.loadtxt('results.txt')
results = np.loadtxt('TipDxc2.txt')

time = results[:,0] - 10.0
deflection = results[:,2]

moment = results[:,20]

#plot blade tip deflection
plt.figure()
plt.plot(time,deflection)
plt.xlabel('Time (s)')
plt.ylabel('Blade Tip Deflection (m)')
plt.title('FAST Output')
plt.show()

#plot blade tip deflection
# plt.figure()
# plt.plot(time,moment)
# plt.xlabel('Time (s)')
# plt.ylabel('In-Plane Moment @ Blade Root (kN*m)')
# plt.title('FAST Output')
# plt.show()