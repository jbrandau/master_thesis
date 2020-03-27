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

    le.trigger()
    ser.write(struct.pack("B", 0xDE))
    ser.write(struct.pack("B", 0xAD))
    ser.write(struct.pack("B", 0xBE))
    ser.write(struct.pack("B", 0xEF))

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
    nonces = np.empty((traces_per_file, 1), np.uint8)
    noncesA = np.empty((traces_per_file, 1), np.uint8)
    msg2 = [0]
    msg3 = [0]

    totaltraces = 0

    for i in xrange(0,traces) :
        le.trigger()
        msg2[0] = int(random.randint(0,0xFF))
        #msg2[0] = int(123)

        ser.write(struct.pack("B", msg2[0]))

        # read ack byte from target
        #print "getting back: "
        read_byte = ser.read(1)
        for xxx in range(1):
            msg3[xxx] = ord(read_byte[xxx])

        tracesA[i%traces_per_file] = le.getWaveform1()[0:n_feats] #getWaveform'n', where n is the channel

        nonces[i%traces_per_file] = msg2
        noncesA[i%traces_per_file] = msg3

        if(i%traces_per_file == traces_per_file-1):
            gc.collect()
            spio.savemat("tracesA" + str(i), {'tracesA': tracesA}, do_compression=True, oned_as='row')
            spio.savemat("nonces" + str(i), {'nonces': nonces}, do_compression=True, oned_as='row')
            spio.savemat("noncesA" + str(i), {'noncesA': noncesA}, do_compression=True, oned_as='row')

        if(i%100 == 99):
            print "Elapsed time: " + str(time.time() - ts1) + " seconds"
            print "Collected traces: " + str(i+1)

        totaltraces = i

    if(totaltraces%traces_per_file != traces_per_file-1):
        spio.savemat("tracesA" + str(totaltraces), {'tracesA': tracesA}, do_compression=True, oned_as='row')
        spio.savemat("nonces" + str(totaltraces), {'nonces': nonces}, do_compression=True, oned_as='row')
        spio.savemat("noncesA" + str(totaltraces), {'noncesA': noncesA}, do_compression=True, oned_as='row')

    le.displayOn()
    print 'done'
