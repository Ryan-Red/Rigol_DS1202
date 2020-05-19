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
#test.write(":STOP")
time.sleep(1)
 
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
data1 = np.add(np.multiply(data2,-1), 255)

finalData1 = np.multiply(np.divide(np.add(data1,-130 - voltoffset1/voltscale1*25), 25),voltscale1)
finalData2 = np.multiply(np.divide(np.add(data2,-130 - voltoffset2/voltscale2*25), 25),voltscale2)



time1 = np.linspace(timeoffset1, timescale1*len(finalData1)-timeoffset1,len(finalData1))/10**(-6)
time2 = np.linspace(timeoffset2, timescale2*len(finalData2)-timeoffset2,len(finalData2))/10**(-6)

test.write(":RUN")
test.write(":KEY:FORC")



plot.plot(time1,finalData1)
plot.title("Oscilloscope Channel 1")
plot.ylabel("Voltage (V)")
plot.xlabel("Time (uS)")
plot.show()

plot.plot(time2,finalData2)
plot.title("Oscilloscope Channel 2")
plot.ylabel("Voltage (V)")
plot.xlabel("Time (uS)")
plot.show()