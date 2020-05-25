import os
import pyvisa as visa
import numpy as np

import time

from tftb.generators import fmlin, sigmerge, noisecg
from tftb.processing.cohen import WignerVilleDistribution

from mpl_toolkits.mplot3d import axes3d, Axes3D
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from matplotlib import cm
import matplotlib.pyplot as plt
 
rm = visa.ResourceManager()
print(rm.list_resources())
addr = 'USB0::0x1AB1::0x0517::DS1ZE214403082::INSTR'
myScope = rm.get_instrument(addr)


print(myScope.ask("*IDN?"))

# Initialize our scope
test = myScope

test.write(":RUN")
#
time.sleep(1)

test.write(":STOP")
 
# Grab the data from channel 1
test.write(":WAV:POIN:MODE RAW")


# Get the voltage scale
voltscale1 = float(test.ask(":CHAN1:SCAL?"))
voltscale2 = float(test.ask(":CHAN2:SCAL?"))
 
# And the voltage offset
voltoffset1 = float(test.ask(":CHAN1:OFFS?"))
voltoffset2 = float(test.ask(":CHAN2:OFFS?"))
 
 
# Get the timescale
timescale1 = float(test.ask(":TIM:SCAL?"))
timescale2 = float(test.ask(":TIM:SCAL?"))

 
# Get the timescale offset
timeoffset1 = float(test.ask(":TIM:OFFS?"))
timeoffset2 = float(test.ask(":TIM:OFFS?"))



finalDataChan1 = []

data1 = np.array(myScope.query_binary_values(":WAV:DATA? CHAN1",datatype='B')[10:])
data2 = np.array(myScope.query_binary_values(":WAV:DATA? CHAN2",datatype='B')[10:])

#Need to do some bitflips and  some weird scaling, http://www.righto.com/2013/07/rigol-oscilloscope-hacks-with-python.html did it first
data1 = np.add(np.multiply(data1,-1), 255)
data2 = np.add(np.multiply(data2,-1), 255)

finalData1 = np.multiply(np.divide(np.add(data1,-130 - voltoffset1/voltscale1*25), 25),voltscale1)
finalData2 = np.multiply(np.divide(np.add(data2,-130 - voltoffset2/voltscale2*25), 25),voltscale2)



time1 = np.linspace(timeoffset1, timescale1*len(finalData1)-timeoffset1,len(finalData1))/10**(-6)
time2 = np.linspace(timeoffset2, timescale2*len(finalData2)-timeoffset2,len(finalData2))/10**(-6)

test.write(":RUN")
test.write(":KEY:FORC")



plt.plot(time1,finalData1)
plt.title("Oscilloscope Channel 1")
plt.ylabel("Voltage (V)")
plt.xlabel("Time (uS)")
plt.show()

plt.plot(time2,finalData2)
plt.title("Oscilloscope Channel 2")
plt.ylabel("Voltage (V)")
plt.xlabel("Time (uS)")
plt.show()


#wvd = WignerVilleDistribution(finalData1)
#k = wvd.run()
#print(k)


n_fbins = 1190
signal = finalData1


y = np.linspace(10, 100, finalData1.shape[0])
X, Y = np.meshgrid(time1, y)


tausec = round(n_fbins / 2.0)
winlength = tausec - 1

ts = time1


tfr = np.zeros((n_fbins, ts.shape[0]), dtype=complex)



taulens = np.min(np.c_[np.arange(signal.shape[0]),
                        signal.shape[0] - np.arange(signal.shape[0]) - 1,
                        winlength * np.ones(ts.shape)], axis=1)


conj_signal = np.conj(signal)
for icol in range(0, len(time1)):
    taumax = taulens[icol]
    tau = np.arange(-taumax, taumax + 1).astype(int)
    indices = np.remainder(n_fbins + tau, n_fbins).astype(int)

    tfr[indices, icol] = signal[icol + tau] * conj_signal[icol - tau]


    if (icol <= signal.shape[0] - tausec) and (icol >= tausec + 1):

        tfr[tausec, icol] = signal[icol + tausec-1] * np.conj(signal[icol - tausec-1]) #+ signal[icol - tausec-1] * conj_signal[icol + tausec-1]


tfr = np.fft.fft(tfr, axis=0)
tfr = np.real(tfr)
print(tfr.shape)
print(Y.shape)
print(X.shape)

fig = plt.figure()
ax = Axes3D(fig) #fig.gca(projection="3d")#Axes3D(fig)


maxi = np.amax(tfr-10)
mini = np.amin(tfr)
levels = np.linspace(mini, maxi, 65)
ax.contour(X, Y, tfr, levels=levels)

ax.set_zlabel("Amplitude")
ax.set_xlabel("Time")
ax.set_ylabel("Frequency")




ax.set_title('Surface plot')

plt.show()

#wvd.plot(kind='surf')