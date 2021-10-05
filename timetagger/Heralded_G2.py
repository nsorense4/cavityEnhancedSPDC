#################################################################################################
get_ipython().run_line_magic('pylab', 'notebook')
import os
import sys
import numpy as np
import matplotlib
try:
    import TimeTagger
except:
    print ("Time Tagger lib is not in the search path.")
    pyversion = sys.version_info
    from winreg import ConnectRegistry, OpenKey, HKEY_LOCAL_MACHINE, QueryValueEx
    registry_path = "SOFTWARE\\Python\\PythonCore\\" + str(pyversion.major) + "." + str(pyversion.minor) + "\\PythonPath\\Time Tagger"
    reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
    key = OpenKey(reg, registry_path) 
    module_path = QueryValueEx(key,'')[0]
    print ("adding " + module_path)
    sys.path.append(module_path)
    
from TimeTagger import createTimeTagger, Combiner, Coincidence, Coincidences, Counter, Countrate, Correlation, Dump, TimeDifferences, TimeTagStream, Scope, Event, CHANNEL_UNUSED, UNKNOWN, LOW, HIGH

from time import sleep, time
from pylab import *
from datetime import datetime

#################################################################################################
#script to run cross correlation 

# create a timetagger instance
tagger = createTimeTagger()
tagger.reset()


# Set the trigger level and deadtime for each channel
[tagger.setTriggerLevel(i, 0.5) for i in range(8)]
[tagger.setDeadtime(i, 6000) for i in range(8)]

binwidth_input = 100 #set the binwidth
binnumber = 200 #set the number of bins
measurementTime = 10 #set the length of measurement in seconds

#delay the two beamsplit channels to coincide with zero time difference at the idler (correlation)
tagger.setInputDelay(channel=6,delay=-20100)
tagger.setInputDelay(channel=5,delay=-16120)
tagger.sync()

# cross correlation between channels 6 and 7, and 5 and 7
corr = Correlation(tagger, channel_1=6, channel_2=7, binwidth=binwidth_input, n_bins=binnumber)
corr1 = Correlation(tagger, channel_1=5, channel_2=7, binwidth=binwidth_input, n_bins=binnumber)
tstart = time.time()    # for profiling


ion()
sleep(1)
fig, ax = subplots(1, 1)
corr_plot, = plot(corr.getIndex()/1e3, corr.getData())
corr_plot1, = plot(corr1.getIndex()/1e3, corr1.getData())
xlabel('Time [ns]')
ylabel('Clicks')
title('Cross correlation between channel 6 and 7')

for i in range(measurementTime*500):
    corr_plot.set_ydata(corr.getData())
    corr_plot1.set_ydata(corr1.getData())
    fig.canvas.draw()
    ylim(0, 1.2*max(max(corr.getData()),max(corr1.getData())))
    time.sleep(.01)

################################################################################################
save("0223_cross_correlation_data_channel1.npy", corr.getData())
print("done")
save("0223_cross_correlation_data_channel2.npy", corr1.getData())
print("done")

################################################################################################
#Script to take countrate

# create a timetagger instance
tagger = createTimeTagger()
tagger.reset()

# Set the trigger level and deadtime for each channel
[tagger.setTriggerLevel(i, 0.5) for i in range(8)]
[tagger.setDeadtime(i, 6000) for i in range(8)]

measurementTime = 5 #time to measure in seconds

#set the channels to count
cr = Countrate( tagger, channels=[1,2,3,4,5,6,7,8] )
tagger.sync()

#wait and then start taking data
sleep(0.1)
data = cr.getData()

#set the labels for the axes
objects = ('1', '2', '3', '4', '5', '6', '7', '8')
y_pos = np.arange(len(objects))
tstart = time.time()

ion()
fig, ax = subplots(1, 1)
barg = bar(y_pos, data, align='center', alpha=0.5)
xticks(y_pos, objects)
ylabel('Countrate (c/s)')
title('Countrate')

for i in range(measurementTime*20):
    data = cr.getData()
    #barg = bar(y_pos, data, align='center', alpha=0.5)
    fig.canvas.draw()
    ylim(-1000, 1.2*max(cr.getData()))
    time.sleep(.05)

################################################################################################
#Script to run g2 measurement. 

#Create the time tagger instance
tagger = createTimeTagger()
tagger.reset()

# Set the trigger level and deadtime for each channel
[tagger.setTriggerLevel(i, 0.5) for i in range(8)]
[tagger.setDeadtime(i, 6000) for i in range(8)]

tagger.sync()

coincidenceWindow_ = 800 # coincidence window in ps
iterant = 1500
noDataPoints = 7 #odd integer

inttime = 1*60*60 # integration time in s


# Delay channels to be coincident, using the web GUI to find the delay value
channelDelay_1 = -16120
channelDelay_2 = -20100
tagger.setInputDelay(channel=6,delay=(channelDelay_2)) #comment out if sweeping both simultaneously

#initialise the data variable
countersdata = np.zeros((noDataPoints,4))


print('Starting to take data.')
#iteratively offset the first channel to test g2 spectrum-wise
for i in range(noDataPoints):
    
    #print the time every time that the code loops
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)
    
    #print the time offset (tau) the loop is currently testing
    print((channelDelay_1-i*iterant+int(noDataPoints/2)*iterant))
    
    #iteratively offset the first channel to test g2 spectrum-wise
    tagger.setInputDelay(channel=5,delay=(channelDelay_1-i*iterant+int(noDataPoints/2)*iterant))
    #iteratively offset the second channel to test g2 spectrum-wise
    #tagger.setInputDelay(channel=6,delay=(channelDelay_2-i*iterant+int(noDataPoints/2)*iterant)) #comment out if sweeping only one channel

    #prepare the coincidence channels to test
    C = Coincidences(tagger, [[5,7],[6,7],[5,6,7]], coincidenceWindow = coincidenceWindow_)
    coinc_chans = C.getChannels()
    S1 = coinc_chans[0] #double coincidence
    S2 = coinc_chans[1] #double coincidence
    C1 = coinc_chans[2] #triple coincidence
    
    #get the countrate for each channel
    sleep(0.5)
    counters = Countrate(tagger, [7, S1, S2, C1])
    
    #start counting
    tagger.sync()
    counters.start()
    sleep(inttime)
    counters.stop()
    countersdata[i] = counters.getData()
    
    #print the countrates
    print(countersdata[i])


#g2 is heralded coincidences times heralds divided by heralded singles times heralded singles
g2 = np.divide(countersdata[:,0]*countersdata[:,3],(countersdata[:,1]*countersdata[:,2]))
print(g2)
sleep(0.5)
fig, ax = subplots(1, 1)
g2plot, = plot(g2)
xlabel('Time [ns]')
ylabel('g2')
title('g2 measurement')

################################################################################################
save("0224_g2_data_1hr_7meas_800window_1500iterant.npy", countersdata)
print("done")

################################################################################################
#script to take raw time tagger data

# create a timetagger instance
tagger = createTimeTagger()
tagger.reset()


# Set the trigger level and deadtime for each channel
[tagger.setTriggerLevel(i, 0.5) for i in range(8)]
[tagger.setDeadtime(i, 6000) for i in range(8)]

#delay the two beamsplit channels to coincide with zero time difference at the idler (correlation)
tagger.setInputDelay(channel=6,delay=-20000)
tagger.setInputDelay(channel=5,delay=-16000)
tagger.sync()

import tempfile

tempdir = tempfile.gettempdir()
tmpfile = tempdir + os.sep + 'dump.tt'
print("1: Dump the data to " + tmpfile)
channels = [5, 6, 7]

# The number of maximum tags which should be dumped is limited only by the size of your storage device.
# Required space: tags * 16 byte
maximum_tags = 10**8
dump = Dump(tagger, tmpfile, maximum_tags, channels)
sleep(10*60)
print("Stop dumping and close the file.")
# by removing the measurement the output file is closed the dump stops
del dump
print("")
print("2: Load the data from " + tmpfile)
tagformat = np.dtype([('overflow', np.dtype('<u4')),
                      ('channel', np.dtype('<i4')), ('time', np.dtype('<u8'))])
data = np.fromfile(tmpfile, dtype=tagformat)

channel = data['channel'].astype('u1')
time = data['time']
channel, time

print("saving data")
save("channel.npy", channel)
save("times.npy", time)

print("Delete dump file.")
os.remove(tmpfile)
