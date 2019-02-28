import numpy as np
from  scipy.optimize import curve_fit


##def func(X, a0, a1, a2, a3, a4, a5, a6):
##    x,y = X
##    return a0 + a1*x + a2*y + a3*x**2 + a4*y**2 + a5*x**3 + a6*y**3

def func(X, a0, a1, a2, a3, a4):
    x,y = X
    return a0 + a1*x + a2*y + a3*x**2 + a4*y**2


p_init = [1.0, 0.1, 0.1, 0.0, 0.0]

xodata = np.array([26.5,26.5,26.5,36,36,36])
yodata = np.array([11.5,0,-11,11.5,0,-11])
xdata = np.array([58,130,208,76,135,198])
ydata = np.array([204,208,205,165,165,162])

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
