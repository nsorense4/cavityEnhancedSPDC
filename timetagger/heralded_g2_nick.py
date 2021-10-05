# -*- coding: utf-8 -*-
"""
@author: Evan@Edits: Nick
"""

import numpy as np
import time

from time import sleep, localtime, strftime
from TimeTagger import *


tagger = createTimeTagger()
tagger.reset()
# Set the trigger level and deadtime for each channel
[tagger.setTriggerLevel(i, 0.05) for i in [3,4]] #
[tagger.setTriggerLevel(i, 0.05) for i in [0,1,2,7]]
[tagger.setDeadtime(i, 6000) for i in range(8)]
tagger.sync()

coincidenceWindow = 5000 # coicidnce window in ps
inttime = 10 # integration time in s

# Set up your three channels for the g2
# Delay them to be coincident, using the web GUI to find the delay value
herald = DelayedChannel(tagger, 1, delay=0)
heralded_1 = DelayedChannel(tagger, 2, delay=1797000)
heralded_2 = DelayedChannel(tagger, 3, delay=1798000)  

S1 = Coincidence(tagger, [herald.getChannel(),heralded_1.getChannel()], coincidenceWindow)
S2 = Coincidence(tagger, [herald.getChannel(),heralded_2.getChannel()], coincidenceWindow)
C12 = Coincidence(tagger, [S1.getChannel(),S2.getChannel()], coincidenceWindow)

counters = Countrate(tagger, [herald.getChannel(), S1.getChannel(), S2.getChannel(), C12.getChannel()])

tagger.sync()
counters.start()
sleep(inttime)
counters.stop()
countersdata = counters.getData()

#g2 is heralded coincidences times heralds divided by heralded singles times heralded singles

g2 = countersdata[3]*countersdata[0]/(countersdata[1]*countersdata[2])

print(g2)



