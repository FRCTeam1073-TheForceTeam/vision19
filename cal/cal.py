import numpy as np
from  scipy.optimize import curve_fit


def func(X, a0, a1, a2, a3, a4):
#    print("X:")
#    print(X)
    x,y = X
    return a0 + a1*x + a2*y + a3*x**2 + a4*y**2


p_init = [1.0, 0.1, 0.1, 0.0, 0.0]

xdata = np.array([3,4,5,7, 9, 11])
ydata = np.array([3,1,0,-3, -4, -6])
odata = np.array([10, 8, 6, 4, 2, 0])

result = curve_fit(func, (xdata, ydata), odata, p_init)

print(result)

popt = result[0]
print("PARAMS:")
print(popt)


for i in range(0,len(xdata)):
    print("[%f, %f] = %f" % (xdata[i],ydata[i],func((xdata[i],ydata[i]), *popt)))
