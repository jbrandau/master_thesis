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

no_steps_x = 10
no_steps_y = 10
no_steps_z = 0

myEM=EM_station.EM_station('COM31', analysis_steps_x=no_steps_x, analysis_steps_y=no_steps_y, analysis_steps_z=no_steps_z)

if not myEM.is_connected():
    print "EM station not connected"
    sys.exit()

print myEM.get_cur_probe_pos()

myEM.set_pos_A([195000, -27000, 0])
myEM.set_pos_B([-202000, 369000, 0])

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
    num_traces = 10000
    traces_per_file = 500
    samples_per_trace = 2500

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
            baudrate=9600,
            timeout=None
            )

    if en_oscilloscope == True:
      ts = time.time()
      st = datetime.datetime.fromtimestamp(ts).strftime('SBOX_traces%Y-%m-%d_%H_%M_%S/')
      if not os.path.exists(st):
        os.makedirs(st)
        os.chdir(st)

    ser.reset_input_buffer()


    time.sleep(0.5)
    write(ser,0xDE)
    time.sleep(0.5)
    write(ser,0xAD)
    time.sleep(0.5)
    write(ser,0xBE)
    time.sleep(0.5)
    write(ser,0xEF)
    time.sleep(0.5)

    check_first = 0
    got_dead_beef = 0
    dead_beef_start = 0

    while(got_dead_beef == 0):
        while ser.in_waiting:
          no_bytes_received = ser.in_waiting
          print no_bytes_received
          dead_beef = ser.read(no_bytes_received)
          for oo in range(0,no_bytes_received):
            if(ord(dead_beef[oo]) == 0xDE):
              dead_beef_start = 1
              break

          start_dead_beef_no = oo
        if(ord(dead_beef[oo+0]) == 0xDE and ord(dead_beef[oo+1]) == 0xAD and ord(dead_beef[oo+2]) == 0xBE and ord(dead_beef[oo+3]) == 0xEF):
          got_dead_beef = 1

    print("GOT DEAD BEEF CHECK....")

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

          tracesA = np.empty((traces_per_file, samples_per_trace),np.uint8)
          nonces = np.empty((traces_per_file, 1), np.uint8)
          noncesA = np.empty((traces_per_file, 1), np.uint8)
          msg2 = [0]
          msg3 = [0]

          for i in xrange(0, num_traces):
                trace_mod = i%traces_per_file

                le.trigger()
                msg2[0] = int(random.randint(0,0xFF))

                ser.write(struct.pack("B", msg2[0]))
                read_byte = ser.read(1)

                if(msg2[0] != ord(read_byte)):
                  print msg2[0]
                  print ord(read_byte)
                  print "Something wrong"

                for xxx in range(1):
                    msg3[xxx] = ord(read_byte[xxx])

                nonces[i%traces_per_file] = msg2
                noncesA[i%traces_per_file] = msg3

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
