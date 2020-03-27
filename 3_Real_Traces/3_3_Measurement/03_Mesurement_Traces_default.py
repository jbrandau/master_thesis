#!/usr/bin/python

import copy
import gc
import time
import serial
import random
import struct
import numpy as np
import scipy.io as spio
import datetime
import os
import gmpy2
import copy
import sys
import EM_station

no_steps_x = 5
no_steps_y = 2
no_steps_z = 0

myEM=EM_station.EM_station('COM31', analysis_steps_x=no_steps_x, analysis_steps_y=no_steps_y, analysis_steps_z=no_steps_z)

if not myEM.is_connected():
    print "EM station not connected"
    sys.exit()

print myEM.get_cur_probe_pos()

myEM.set_pos_A([27000, 324000, 0])
myEM.set_pos_B([-345000, 695000, 0])

myEM.get_cur_probe_pos()
myEM.gen_analysis_map()
print "analysis map completed"

en_oscilloscope = True
if en_oscilloscope == True:
    import Oscilloscope as lecroy

def write(ser, data):
   ser.write(chr(data))

def write64(ser, addr, data):
   ser.write(chr(addr  ) + chr(byte(data, 0)) +
             chr(addr+1) + chr(byte(data, 1)) +
             chr(addr+2) + chr(byte(data, 2)) +
             chr(addr+3) + chr(byte(data, 3)) +
             chr(addr+4) + chr(byte(data, 4)) +
             chr(addr+5) + chr(byte(data, 5)) +
             chr(addr+6) + chr(byte(data, 6)) +
             chr(addr+7) + chr(byte(data, 7)))

def read(ser, addr):
   ser.write(chr( addr | 0x80))
   return ord(ser.read())

def byte(val, index):
    return ((int(val)>>(8*index)) & 0xff)

#
if __name__ == "__main__":
    num_traces = 1024
    traces_per_file = 2
    samples_per_trace = 100000

    if en_oscilloscope == True:
        le = lecroy.Oscilloscope()
        le.connect()
        le.calibrate()
        le.displayOn()
        le.Samples = samples_per_trace

    if en_oscilloscope == False:
        import Oscilloscope as lecroy
        le = lecroy.Oscilloscope()
        le.connect()
        le.displayOn()

    ser = serial.Serial(
            port='COM37',
            baudrate=115200,
            timeout=None
            )


    if en_oscilloscope == True:
      ts = time.time()
      st = datetime.datetime.fromtimestamp(ts).strftime('Round5_1bit_DoM_traces%Y-%m-%d_%H_%M_%S/')
      if not os.path.exists(st):
        os.makedirs(st)
        os.chdir(st)

    ser.reset_input_buffer()
    for x_pos in xrange(0,no_steps_x):
        for y_pos in range(0,no_steps_y):
          myEM.perform_analysis_step()
          prob_pos = myEM.get_cur_probe_pos()
            time.sleep(0.5)
            if en_oscilloscope == True:
                position = "spot_%d_%d" %(x_pos,y_pos)
                if not os.path.exists(position):
                    os.makedirs(position)
                os.chdir(position)

            for i in xrange(0, num_traces):
                  trace_mod = i%traces_per_file
                  write(ser,0x53)
                  c = ser.read()
                  d = ord(c)

                  while(d != 0x5A):
                    print 'Wrong data received...'
                    break
                  if en_oscilloscope == True:
                      if(i%traces_per_file == traces_per_file-1):
                        time.sleep(0.1)
                        seqtrace = le.getWaveform_8_1()[0:samples_per_trace*traces_per_file]
                        tmp_traces = np.split(seqtrace,seqtrace.shape[0]/samples_per_trace)
                        spio.savemat("traces_" + str(i+1), {'traces': tmp_traces}, do_compression=True, oned_as='row')
                        print "Saving file " + str(time.time() - ts) + " seconds"
                        print "Collected traces: " + str(i+1)
            os.chdir("..")
    os.chdir("..")
