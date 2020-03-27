#!/usr/bin/python

import gc
import time
import serial
import random
import struct
import numpy as np
import scipy.io as spio
import datetime
import os
import Oscilloscope as lecroy
import copy
import sys, traceback
import random
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math
import numpy as np
import scipy.io
import math
import pylab as py
import struct
from scipy.stats.stats import pearsonr
import csv

def calc_snr(label,traces):
    '''
    this is assuming that the label is from 0-n_bit (no number skipped)
    '''
    var_x = np.var(traces,axis=0)
    idzs = np.nonzero(var_x)[0]
    
    idd = np.unique(label)
    mean_l = np.zeros((len(idd),traces.shape[1]))
    counter = np.zeros(len(idd))
    for i in range(traces.shape[0]):
        iz2 = int(label[i])
        iz = np.where(idd == iz2)[0][0]
        mean_l[iz,:]+=traces[i,:]
        counter[iz]+=1
    for i in range(0,len(idd)):
        if counter[i]>0:
            mean_l[i,:] = mean_l[i,:]/float(counter[i])
    var_e = np.var(mean_l,axis=0)
    nicv = np.zeros(len(var_x))
    nicv[idzs] = var_e[idzs]/var_x[idzs]
    '''
    for x in range(traces.shape[1]):
        mean_l = np.zeros(len(idd))
        counter = np.zeros(len(idd))
        for i in range(traces.shape[0]):
            mean_l[label[i]]+=traces[i,x]
            counter[label[i]]+=1
        for i in range(0,len(idd)):
            if counter[i]>0:
                mean_l[i] = mean_l[i]/float(counter[i])
            var_e = np.var(mean_l)
            nicv_e = var_e/var_x
        nicv[x] = nicv_e
    '''
    snr = np.zeros(len(nicv))
    for i in range(len(snr)):
        snr[i] = 1/(1/(nicv[i])-1)
    return snr

if __name__ == "__main__":
    
    gc.enable()
    le = lecroy.Oscilloscope()
    le.connect()
    le.calibrate()
    #le.displayOff()

    ser = serial.Serial(
        port='COM37',
        baudrate=9600,
        timeout=None
    )

    ser.flushInput()
    print "here"

    traces = 10000
    traces_per_file = 500

    random.seed()
    # generate random data
    
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H_%M_%S')  
  
    if not os.path.exists("traces" + st):
        os.makedirs("traces" + st)
    os.chdir("traces" + st)

    time.sleep(0.05)

    ts1 = time.time()
    n_feats = 2500
    tracesA = np.empty((traces_per_file, n_feats),np.uint8)
    #tracesB = np.empty((traces_per_file, 50000))
    nonces = np.empty((traces_per_file, 1), np.uint8)
    noncesA = np.empty((traces_per_file, 1), np.uint8)
    msg2 = [0]
    msg3 = [0]

    totaltraces = 0
    #n = np.empty((1), np.uint8)
    

    for i in xrange(0,traces) :
        
        le.trigger()
        msg2[0] = int(random.randint(0,0xFF))
        #msg2[0] = int(123)
		
        ser.write(struct.pack("B", msg2[0]))

        # read ack byte from target
        #print "getting back: "
        read_byte = ser.read(1)
        #print read_byte.encode("hex")
        for xxx in range(1):
            msg3[xxx] = ord(read_byte[xxx])

        #time.sleep(0.5)
        # read data from oscilloscope
        #a = le.getWaveform1()
        #print a.shape
        #print 'here 2'

        tracesA[i%traces_per_file] = le.getWaveform1()[0:n_feats] #getWaveform'n', where n is the channel

        #tracesB[i%traces_per_file] = le.getWaveform2()[0:50000]
        nonces[i%traces_per_file] = msg2
        noncesA[i%traces_per_file] = msg3
        
        if(i%traces_per_file == traces_per_file-1):
            gc.collect()            
            spio.savemat("tracesA" + str(i), {'tracesA': tracesA}, do_compression=True, oned_as='row')
        #    spio.savemat("tracesB" + str(i), {'tracesB': tracesB}, do_compression=True, oned_as='row')
            spio.savemat("nonces" + str(i), {'nonces': nonces}, do_compression=True, oned_as='row')
            spio.savemat("noncesA" + str(i), {'noncesA': noncesA}, do_compression=True, oned_as='row')
            
        if(i%100 == 99):
            print "Elapsed time: " + str(time.time() - ts1) + " seconds"
            print "Collected traces: " + str(i+1)            
        
        totaltraces = i

    if(totaltraces%traces_per_file != traces_per_file-1):
        spio.savemat("tracesA" + str(totaltraces), {'tracesA': tracesA}, do_compression=True, oned_as='row')
    #    spio.savemat("tracesB" + str(totaltraces), {'tracesB': tracesB}, do_compression=True, oned_as='row')
        spio.savemat("nonces" + str(totaltraces), {'nonces': nonces}, do_compression=True, oned_as='row')
        spio.savemat("noncesA" + str(totaltraces), {'noncesA': noncesA}, do_compression=True, oned_as='row')

    le.displayOn()
    print 'done'
    
    filename1 = "traces" + st
    file_no = int(traces/traces_per_file)
    set_size = traces_per_file

    trace_aes = np.zeros((file_no*set_size,n_feats))
    msg_aes = np.zeros(file_no*set_size)
    ot = np.zeros(file_no*set_size)
    
    for i in range(0,file_no):
        print(filename1)
        path = filename1 +"/tracesA%d.mat" %((i+1)*set_size-1)
        mat = scipy.io.loadmat(path, squeeze_me=True)
        traces = mat["tracesA"]
        idx = np.arange(i*set_size,(i+1)*set_size,1)
        trace_aes[idx,:] = np.array(traces, dtype = 'double')
        path = filename1 +"/nonces%d.mat" %((i+1)*set_size-1)
        mat = scipy.io.loadmat(path, squeeze_me=True)
        inputs = mat["nonces"]
        msg_aes[idx] = inputs
        

    print(msg_aes[0:10])
       
    in_aes = np.zeros(len(msg_aes))
    out_aes = np.zeros(len(msg_aes)) 
    
    in_aes_i = np.zeros(len(msg_aes))
    out_aes_i = np.zeros(len(msg_aes))

    print(len(np.unique(in_aes_i)))
    corr_val =  (calc_snr(in_aes_i, trace_aes))   

    plt.figure()
    plt.plot(corr_val)

    plt.show()