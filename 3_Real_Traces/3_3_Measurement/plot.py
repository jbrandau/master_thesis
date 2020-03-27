import matplotlib.pyplot as plt
import scipy.io as spio
import numpy as np
import sys


i = 0
ax = spio.loadmat(sys.argv[1])

line = plt.plot(ax[sys.argv[2]])

#plt.legend(fontsize='small')
#plt.title("Correlation Coefficient")
#plt.xlabel("Measure Point")
#plt.ylabel("Correlation Coefficient")
plt.show ()