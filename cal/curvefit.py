import numpy as np
from  scipy.optimize import curve_fit


def func(X, a0, a1, a2, a3, a4, a5, a6):
#    print("X:")
#    print(X)
    x,y = X
    return a0 + a1*x + a2*y + a3*x**2 + a4*y**2 + a5*x**3 + a6*y**3


p_init = [1.0, 0.1, 0.1, 0.0, 0.0, 0.0, 0.0]

xdata = np.array([3,4,5,7, 9, 11, 12, 15])
ydata = np.array([3,1,0,-3, -4, -6, -7, -9])
xodata = np.array([10, 8, 6, 4, 2, 0, -1, -4])
yodata = np.array([-4, -1, 0, 2, 4, 6, 8, 10])

xresult = curve_fit(func, (xdata, ydata), xodata, p_init)
yresult = curve_fit(func, (xdata, ydata), yodata, p_init)

print(xresult)
print(yresult)

xpopt = xresult[0]
ypopt = yresult[0]

print("XPARAMS:")
print(xpopt)
print("YPARAMS:")
print(ypopt)

for i in range(0,len(xdata)):
    print("[%f, %f] = %f, %f" % (xdata[i],ydata[i],func((xdata[i],ydata[i]), *xpopt), func((xdata[i],ydata[i]), *ypopt)))
