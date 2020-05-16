import os
import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plot
import time
 
rm = visa.ResourceManager()
print(rm.list_resources())
addr = 'USB0::0x1AB1::0x0517::DS1ZE214403082::INSTR'
myScope = rm.get_instrument(addr)


print(myScope.ask("*IDN?"))

# Initialize our scope
test = myScope

test.write(":RUN")

time.sleep(1)


 
 
# Stop data acquisition

 
# Grab the data from channel 1
test.write(":WAV:POIN:MODE RAW")

finalData = []

test.write(":WAV:DATA? CHAN1")
rawdata = test.read().split(',')


rawdata[0] = rawdata[0][11:]


realdata = rawdata


finalData = finalData + [float(val) for val in realdata]





 
# Get the voltage scale
voltscale = float(test.ask(":CHAN1:SCAL?"))

 
# And the voltage offset
voltoffset = float(test.ask(":CHAN1:OFFS?"))

 
 
# Get the timescale
timescale = float(test.ask(":TIM:SCAL?"))
print(timescale)

 
# Get the timescale offset
timeoffset = float(test.ask(":TIM:OFFS?"))





# Now, generate a time axis.  The scope display range is 0-600, with 300 being
# time zero.
time = np.linspace(0, timescale*len(finalData),len(finalData))/10**(-6)

 
# Start data acquisition again, and put the scope back in local mode
test.write(":RUN")
test.write(":KEY:FORC")



# Plot the data
x = len(finalData)
print(x)
print("\n\n")
print(time.size)

plot.plot(time,finalData)
plot.title("Oscilloscope Channel 1")
plot.ylabel("Voltage (V)")
plot.xlabel("Time (uS)")
plot.show()